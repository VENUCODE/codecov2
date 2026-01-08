import math

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.errors import division_by_zero_handler, validation_exception_handler
from app.models import HealthResponse, MathRequest, MathResponse, SingleNumberRequest
from app.utils import (
    calculate_percentage,
    factorial,
    format_number,
    get_statistics,
    is_even,
    round_to_precision,
    validate_division,
)

app = FastAPI(title="Math Operations API", version="1.0.0")

# Add error handlers


app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValueError, division_by_zero_handler)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="1.0.0")


@app.post("/add", response_model=MathResponse)
def add(request: MathRequest) -> MathResponse:
    """Add two numbers."""
    result = request.a + request.b
    return MathResponse(result=result)


@app.post("/subtract", response_model=MathResponse)
def subtract(request: MathRequest) -> MathResponse:
    """Subtract two numbers."""
    result = request.a - request.b
    return MathResponse(result=result)


@app.post("/multiply", response_model=MathResponse)
def multiply(request: MathRequest) -> MathResponse:
    """Multiply two numbers."""
    result = request.a * request.b
    return MathResponse(result=result)


@app.post("/divide", response_model=MathResponse)
def divide(request: MathRequest) -> MathResponse:
    """Divide two numbers."""
    if not validate_division(request.b):
        raise HTTPException(status_code=400, detail="Division by zero is not allowed")
    result = request.a / request.b
    return MathResponse(result=round_to_precision(result))


@app.post("/power", response_model=MathResponse)
def power(request: MathRequest) -> MathResponse:
    """Raise first number to the power of second number."""
    result = math.pow(request.a, request.b)
    return MathResponse(result=result)


@app.post("/modulo", response_model=MathResponse)
def modulo(request: MathRequest) -> MathResponse:
    """Calculate modulo (remainder) of division."""
    if not validate_division(request.b):
        raise HTTPException(status_code=400, detail="Modulo by zero is not allowed")
    result = request.a % request.b
    return MathResponse(result=result)


@app.post("/sqrt", response_model=MathResponse)
def sqrt(request: SingleNumberRequest) -> MathResponse:
    """Calculate square root of a number."""
    if request.value < 0:
        raise HTTPException(
            status_code=400, detail="Cannot calculate square root of negative number"
        )
    result = math.sqrt(request.value)
    return MathResponse(result=round_to_precision(result))


@app.post("/percentage", response_model=MathResponse)
def percentage(request: MathRequest) -> MathResponse:
    """Calculate percentage of first number out of second number."""
    try:
        result = calculate_percentage(request.a, request.b)
        return MathResponse(result=round_to_precision(result))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/factorial", response_model=MathResponse)
def calculate_factorial(request: SingleNumberRequest) -> MathResponse:
    """Calculate factorial of a number."""
    if request.value < 0 or request.value != int(request.value):
        raise HTTPException(
            status_code=400, detail="Factorial is only defined for non-negative integers"
        )
    result = factorial(int(request.value))
    return MathResponse(result=float(result))


@app.post("/statistics", response_model=dict)
def statistics(numbers: list[float]) -> dict:
    """Calculate statistics for a list of numbers."""
    stats = get_statistics(numbers)
    return stats


@app.get("/is_even/{number}")
def check_even(number: int):
    """Check if a number is even."""
    result = is_even(number)
    return {"number": number, "is_even": result}


@app.get("/format/{number}")
def format_number_endpoint(number: float):
    """Format a number with commas."""
    formatted = format_number(number)
    return {"original": number, "formatted": formatted}
