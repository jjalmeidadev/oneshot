"""Armazenamento privado de artefatos, com Supabase como destino de producao."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

import httpx

from app.reports.errors import ReportConfigurationError, ReportError
from app.reports.schemas import ReportArtifact


@dataclass(frozen=True)
class ArtifactContent:
    data: bytes
    file_name: str
    content_type: str


class ArtifactStore:
    def __init__(self, mode: str | None = None) -> None:
        self.mode = (mode or os.getenv("REPORT_STORAGE_MODE", "local")).strip().lower()
        if self.mode not in {"local", "supabase"}:
            raise ReportConfigurationError()

    def persist(self, artifact: ReportArtifact) -> ReportArtifact:
        if self.mode == "local":
            return artifact
        path = self._validated_local_path(artifact)
        data = path.read_bytes()
        object_path = f"{artifact.created_at:%Y/%m}/{artifact.artifact_id}/{artifact.file_name}"
        self._ensure_bucket()
        response = httpx.post(
            self._object_url(object_path),
            content=data,
            headers={
                **self._headers(),
                "Content-Type": artifact.content_type,
                "x-upsert": "false",
            },
            timeout=self._timeout(),
        )
        if response.status_code not in {200, 201}:
            raise ReportConfigurationError()
        path.unlink(missing_ok=True)
        return artifact.model_copy(
            update={
                "storage_provider": "supabase",
                "storage_reference": object_path,
            }
        )

    def read(self, artifact: ReportArtifact, artifact_root: Path) -> ArtifactContent:
        if artifact.storage_provider == "local":
            path = Path(artifact.storage_reference or "").resolve()
            root = artifact_root.resolve()
            if root not in path.parents or not path.is_file():
                raise self._not_available()
            data = path.read_bytes()
        elif artifact.storage_provider == "supabase":
            if not artifact.storage_reference:
                raise self._not_available()
            response = httpx.get(
                self._object_url(artifact.storage_reference),
                headers=self._headers(),
                timeout=self._timeout(),
            )
            if response.status_code != 200:
                raise self._not_available()
            data = response.content
        else:
            raise self._not_available()
        return ArtifactContent(
            data=data,
            file_name=artifact.file_name,
            content_type=artifact.content_type,
        )

    def _ensure_bucket(self) -> None:
        bucket = self._bucket()
        response = httpx.get(
            f"{self._url()}/storage/v1/bucket/{quote(bucket, safe='')}",
            headers=self._headers(),
            timeout=self._timeout(),
        )
        if response.status_code == 200:
            return
        if response.status_code != 404 or not _env_bool(
            "SUPABASE_STORAGE_AUTO_CREATE", True
        ):
            raise ReportConfigurationError()
        created = httpx.post(
            f"{self._url()}/storage/v1/bucket",
            json={
                "id": bucket,
                "name": bucket,
                "public": False,
                "allowed_mime_types": [
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                ],
            },
            headers=self._headers(),
            timeout=self._timeout(),
        )
        if created.status_code not in {200, 201}:
            raise ReportConfigurationError()

    def _object_url(self, object_path: str) -> str:
        return (
            f"{self._url()}/storage/v1/object/"
            f"{quote(self._bucket(), safe='')}/{quote(object_path, safe='/')}"
        )

    @staticmethod
    def _validated_local_path(artifact: ReportArtifact) -> Path:
        if not artifact.storage_reference:
            raise ReportConfigurationError()
        path = Path(artifact.storage_reference).resolve()
        if not path.is_file():
            raise ReportConfigurationError()
        return path

    @staticmethod
    def _url() -> str:
        value = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
        if not value:
            raise ReportConfigurationError()
        return value

    @staticmethod
    def _service_key() -> str:
        value = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        if not value:
            raise ReportConfigurationError()
        return value

    def _headers(self) -> dict[str, str]:
        key = self._service_key()
        return {"Authorization": f"Bearer {key}", "apikey": key}

    @staticmethod
    def _bucket() -> str:
        return os.getenv("SUPABASE_STORAGE_BUCKET", "generated-reports").strip()

    @staticmethod
    def _timeout() -> float:
        try:
            return max(1.0, min(float(os.getenv("SUPABASE_STORAGE_TIMEOUT_SECONDS", "20")), 120.0))
        except ValueError as error:
            raise ReportConfigurationError() from error

    @staticmethod
    def _not_available() -> ReportError:
        return ReportError(
            "REPORT_ARTIFACT_NOT_AVAILABLE",
            "O arquivo do relatorio nao esta disponivel.",
            404,
        )


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}
