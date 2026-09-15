"""Politica fechada de aliases de modelo aceitos pelo Copilot Studio."""

from __future__ import annotations

import os

from app.copilot.errors import (
    CopilotConfigurationError,
    ModelRouteNotAllowedError,
    ModelRouteUnavailableError,
)

RECOGNIZED_MODEL_ROUTES = frozenset({"auto", "gpt", "claude"})


def resolve_model_route(requested_route: str) -> str:
    """Valida o alias sem aceitar nomes arbitrarios de provedor ou modelo."""

    route = requested_route.strip().lower()
    if route not in RECOGNIZED_MODEL_ROUTES:
        raise ModelRouteNotAllowedError()

    allowed = _configured_routes("COPILOT_ALLOWED_MODEL_ROUTES", default={"auto"})
    if route not in allowed:
        raise ModelRouteNotAllowedError()

    available = _configured_routes(
        "COPILOT_AVAILABLE_MODEL_ROUTES",
        default={"auto"},
    )
    if route not in available:
        raise ModelRouteUnavailableError()
    return route


def _configured_routes(name: str, *, default: set[str]) -> set[str]:
    raw = os.getenv(name)
    routes = (
        default
        if raw is None
        else {value.strip().lower() for value in raw.split(",") if value.strip()}
    )
    if not routes or not routes.issubset(RECOGNIZED_MODEL_ROUTES):
        raise CopilotConfigurationError()
    return routes
