# app/middlewares.py
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
import logging

logger = logging.getLogger("uvicorn.error")  # use uvicorn logger by default


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


async def global_exception_handler(request: Request, exc: Exception):
    # Log full traceback for debugging
    tb_str = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    logger.error(f"Unhandled error:\n{tb_str}")

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error. Please check server logs."},
    )
