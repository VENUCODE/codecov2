"""Tests for error handlers."""

import pytest
from fastapi.testclient import TestClient
from fastapi.exceptions import RequestValidationError
from app.main import app
from app.errors import MathError

client = TestClient(app)


class TestValidationExceptionHandler:
    """Test cases for validation_exception_handler."""
    
    def test_validation_error_missing_field(self):
        """Test validation error with missing field."""
        response = client.post("/add", json={"a": 10})
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert "errors" in data
        assert len(data["errors"]) > 0
    
    def test_validation_error_invalid_type(self):
        """Test validation error with invalid type."""
        response = client.post("/add", json={"a": "invalid", "b": 5})
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert "errors" in data


class TestDivisionByZeroHandler:
    """Test cases for division_by_zero_handler."""
    
    def test_division_by_zero_in_divide(self):
        """Test division by zero in divide endpoint."""
        response = client.post("/divide", json={"a": 10, "b": 0})
        assert response.status_code == 400
        assert "Division by zero" in response.json()["detail"]
    
    def test_modulo_by_zero(self):
        """Test modulo by zero."""
        response = client.post("/modulo", json={"a": 10, "b": 0})
        assert response.status_code == 400
        assert "Modulo by zero" in response.json()["detail"]


class TestMathError:
    """Test cases for MathError custom exception."""
    
    def test_math_error_creation(self):
        """Test MathError exception creation."""
        error = MathError("Test error message")
        assert error.message == "Test error message"
        assert str(error) == "Test error message"
    
    def test_math_error_inheritance(self):
        """Test MathError inherits from Exception."""
        error = MathError("Test")
        assert isinstance(error, Exception)
