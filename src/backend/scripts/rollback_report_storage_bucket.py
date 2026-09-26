"""Remove o bucket de relatorios pela API oficial do Supabase Storage."""

from __future__ import annotations

import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from dotenv import load_dotenv


BUCKET_ID = "generated-reports"


def delete_bucket() -> bool:
    """Remove o bucket vazio; retorna False quando ele ja nao existe."""

    supabase_url = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not supabase_url or not service_key:
        raise RuntimeError(
            "Configure SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY para executar "
            "o rollback seguro do bucket."
        )

    request = Request(
        f"{supabase_url}/storage/v1/bucket/{quote(BUCKET_ID, safe='')}",
        method="DELETE",
        headers={
            "Authorization": f"Bearer {service_key}",
            "apikey": service_key,
        },
    )
    try:
        with urlopen(request, timeout=20):
            return True
    except HTTPError as error:
        if error.code == 404:
            return False
        if error.code in {400, 409}:
            raise RuntimeError(
                "O bucket nao esta vazio; rollback abortado sem remover objetos."
            ) from error
        raise RuntimeError(
            f"Supabase Storage recusou o rollback do bucket (HTTP {error.code})."
        ) from error
    except URLError as error:
        raise RuntimeError(
            "Nao foi possivel conectar ao Supabase Storage para o rollback."
        ) from error


def main() -> None:
    load_dotenv()
    removed = delete_bucket()
    print("BUCKET_REMOVED=" + str(removed))


if __name__ == "__main__":
    main()
