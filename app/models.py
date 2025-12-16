from pydantic import BaseModel
from typing import Optional


class MathRequest(BaseModel):
    """Request model for math operations."""
    a: float
    b: float


class SingleNumberRequest(BaseModel):
    """Request model for single number operations."""
    value: float


class MathResponse(BaseModel):
    """Response model for math operations."""
    result: float


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str

