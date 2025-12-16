"""Utility functions for math operations."""

import math
from typing import Optional


def validate_division(b: float) -> bool:
    """Validate that division by zero is not attempted."""
    return b != 0


def calculate_percentage(value: float, total: float) -> float:
    """Calculate percentage of value out of total."""
    if total == 0:
        raise ValueError("Total cannot be zero")
    return (value / total) * 100


def round_to_precision(number: float, precision: int = 2) -> float:
    """Round a number to specified precision."""
    return round(number, precision)


def is_even(number: int) -> bool:
    """Check if a number is even."""
    return number % 2 == 0


def factorial(n: int) -> int:
    """Calculate factorial of a number."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def format_number(number: float) -> str:
    """Format a number as a string with commas."""
    return f"{number:,.2f}"


def get_statistics(numbers: list[float]) -> dict[str, float]:
    """Calculate statistics for a list of numbers."""
    if not numbers:
        return {"mean": 0, "min": 0, "max": 0, "sum": 0}
    
    return {
        "mean": sum(numbers) / len(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "sum": sum(numbers)
    }

