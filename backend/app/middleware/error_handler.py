"""
Middleware global de manejo de errores.
Captura HTTPException y Exception para retornar JSON uniforme.
Evita que los 500 filtren stack-traces en producción.
"""

import logging
import traceback
from datetime import datetime

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("app.error_handler")


class GlobalErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response

        except HTTPException as http_exc:
            # HTTPException ya tiene status + detail
            # La envolvemos en formato JSON uniforme
            detail = http_exc.detail
            if isinstance(detail, dict):
                body = detail
            else:
                body = {"error": "http_error", "message": str(detail)}

            body.setdefault("timestamp", datetime.utcnow().isoformat())
            body.setdefault("path", str(request.url.path))

            logger.warning(
                "HTTP %d — %s — %s",
                http_exc.status_code,
                request.url.path,
                detail,
            )
            return JSONResponse(status_code=http_exc.status_code, content=body)

        except Exception as exc:
            # Error no controlado → 500
            trace = traceback.format_exc()
            logger.error("UNHANDLED 500 — %s — %s", request.url.path, trace)

            return JSONResponse(
                status_code=500,
                content={
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred. Please try again later.",
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": str(request.url.path),
                },
            )