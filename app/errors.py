"""Custom error handlers."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"]
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": errors}
    )


async def division_by_zero_handler(request: Request, exc: ValueError):
    """Handle division by zero errors."""
    if "zero" in str(exc).lower():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Division by zero is not allowed"}
        )
    raise exc


class MathError(Exception):
    """Custom math error."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

