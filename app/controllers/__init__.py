"""Controllers and error handlers for API endpoints."""

from typing import Any

from advanced_alchemy.exceptions import DuplicateKeyError, NotFoundError
from litestar import Request, Response
from litestar.status_codes import HTTP_409_CONFLICT

from app.config import settings


def not_found_error_handler(_: Request[Any, Any, Any], __: NotFoundError) -> Response[Any]:
    """Handle not found errors."""
    return Response(
        status_code=404,
        content={"status_code": 404, "detail": "Not found"},
    )


def duplicate_error_handler(_: Request[Any, Any, Any], __: DuplicateKeyError) -> Response[Any]:
    """Handle duplicate errors."""
    # Use the exception detail when available to provide a clearer message to the client.
    raw_detail = getattr(__, "detail", None)
    if not raw_detail or raw_detail == "There was an issue processing the statement.":
        detail = "Conflicto: ya existe un registro con un valor único (por ejemplo, username)."
    else:
        detail = raw_detail

    content: dict[str, Any] = {"status_code": HTTP_409_CONFLICT, "detail": detail}
    if settings.debug:
        content["debug_detail"] = raw_detail
    return Response(
        status_code=HTTP_409_CONFLICT,
        content=content,
    )
