import hmac
import os

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

PUBLIC_PATHS = {"/health"}


class ApiKeyMiddleware:
    """Pure ASGI middleware (safe for streaming MCP responses). Requires x-api-key."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["path"] in PUBLIC_PATHS or scope["method"] == "OPTIONS":
            await self.app(scope, receive, send)
            return
        expected = os.environ.get("API_KEY", "")
        given = dict(scope["headers"]).get(b"x-api-key", b"").decode("latin-1")
        if not expected or not hmac.compare_digest(given.encode(), expected.encode()):
            await JSONResponse({"detail": "Unauthorized"}, status_code=401)(scope, receive, send)
            return
        await self.app(scope, receive, send)
