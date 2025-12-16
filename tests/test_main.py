import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestRootEndpoint:
    """Test cases for the root endpoint."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello, World!"}


class TestHealthEndpoint:
    """Test cases for the /health endpoint."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"


class TestAddEndpoint:
    """Test cases for the /add endpoint."""
    
    def test_add_positive_numbers(self):
        """Test addition with positive numbers."""
        response = client.post("/add", json={"a": 10, "b": 5})
        assert response.status_code == 200
        assert response.json() == {"result": 15}
    
    def test_add_negative_numbers(self):
        """Test addition with negative numbers."""
        response = client.post("/add", json={"a": -10, "b": -5})
        assert response.status_code == 200
        assert response.json() == {"result": -15}
    
    def test_add_mixed_numbers(self):
        """Test addition with mixed positive and negative numbers."""
        response = client.post("/add", json={"a": 10, "b": -5})
        assert response.status_code == 200
        assert response.json() == {"result": 5}
    
    def test_add_decimal_numbers(self):
        """Test addition with decimal numbers."""
        response = client.post("/add", json={"a": 10.5, "b": 5.2})
        assert response.status_code == 200
        assert response.json() == {"result": 15.7}
    
    def test_add_zero(self):
        """Test addition with zero."""
        response = client.post("/add", json={"a": 10, "b": 0})
        assert response.status_code == 200
        assert response.json() == {"result": 10}
    
    def test_add_missing_field(self):
        """Test addition with missing field."""
        response = client.post("/add", json={"a": 10})
        assert response.status_code == 422
    
    def test_add_invalid_type(self):
        """Test addition with invalid type."""
        response = client.post("/add", json={"a": "invalid", "b": 5})
        assert response.status_code == 422


class TestSubtractEndpoint:
    """Test cases for the /subtract endpoint."""
    
    def test_subtract_positive_numbers(self):
        """Test subtraction with positive numbers."""
        response = client.post("/subtract", json={"a": 10, "b": 5})
        assert response.status_code == 200
        assert response.json() == {"result": 5}
    
    def test_subtract_negative_numbers(self):
        """Test subtraction with negative numbers."""
        response = client.post("/subtract", json={"a": -10, "b": -5})
        assert response.status_code == 200
        assert response.json() == {"result": -5}
    
    def test_subtract_mixed_numbers(self):
        """Test subtraction with mixed positive and negative numbers."""
        response = client.post("/subtract", json={"a": 10, "b": -5})
        assert response.status_code == 200
        assert response.json() == {"result": 15}
    
    def test_subtract_decimal_numbers(self):
        """Test subtraction with decimal numbers."""
        response = client.post("/subtract", json={"a": 10.5, "b": 5.2})
        assert response.status_code == 200
        assert abs(response.json()["result"] - 5.3) < 0.0001
    
    def test_subtract_zero(self):
        """Test subtraction with zero."""
        response = client.post("/subtract", json={"a": 10, "b": 0})
        assert response.status_code == 200
        assert response.json() == {"result": 10}
    
    def test_subtract_missing_field(self):
        """Test subtraction with missing field."""
        response = client.post("/subtract", json={"a": 10})
        assert response.status_code == 422
    
    def test_subtract_invalid_type(self):
        """Test subtraction with invalid type."""
        response = client.post("/subtract", json={"a": "invalid", "b": 5})
        assert response.status_code == 422


class TestMultiplyEndpoint:
    """Test cases for the /multiply endpoint."""
    
    def test_multiply_positive_numbers(self):
        """Test multiplication with positive numbers."""
        response = client.post("/multiply", json={"a": 10, "b": 5})
        assert response.status_code == 200
        assert response.json() == {"result": 50}
    
    def test_multiply_negative_numbers(self):
        """Test multiplication with negative numbers."""
        response = client.post("/multiply", json={"a": -10, "b": -5})
        assert response.status_code == 200
        assert response.json() == {"result": 50}
    
    def test_multiply_mixed_numbers(self):
        """Test multiplication with mixed positive and negative numbers."""
        response = client.post("/multiply", json={"a": 10, "b": -5})
        assert response.status_code == 200
        assert response.json() == {"result": -50}
    
    def test_multiply_decimal_numbers(self):
        """Test multiplication with decimal numbers."""
        response = client.post("/multiply", json={"a": 10.5, "b": 5.2})
        assert response.status_code == 200
        assert abs(response.json()["result"] - 54.6) < 0.0001
    
    def test_multiply_zero(self):
        """Test multiplication with zero."""
        response = client.post("/multiply", json={"a": 10, "b": 0})
        assert response.status_code == 200
        assert response.json() == {"result": 0}
    
    def test_multiply_missing_field(self):
        """Test multiplication with missing field."""
        response = client.post("/multiply", json={"a": 10})
        assert response.status_code == 422
    
    def test_multiply_invalid_type(self):
        """Test multiplication with invalid type."""
        response = client.post("/multiply", json={"a": "invalid", "b": 5})
        assert response.status_code == 422


class TestDivideEndpoint:
    """Test cases for the /divide endpoint."""
    
    def test_divide_positive_numbers(self):
        """Test division with positive numbers."""
        response = client.post("/divide", json={"a": 10, "b": 5})
        assert response.status_code == 200
        assert response.json() == {"result": 2.0}
    
    def test_divide_decimal_numbers(self):
        """Test division with decimal numbers."""
        response = client.post("/divide", json={"a": 10.5, "b": 2.5})
        assert response.status_code == 200
        assert response.json() == {"result": 4.2}
    
    def test_divide_negative_numbers(self):
        """Test division with negative numbers."""
        response = client.post("/divide", json={"a": -10, "b": -5})
        assert response.status_code == 200
        assert response.json() == {"result": 2.0}
    
    def test_divide_mixed_numbers(self):
        """Test division with mixed positive and negative numbers."""
        response = client.post("/divide", json={"a": 10, "b": -5})
        assert response.status_code == 200
        assert response.json() == {"result": -2.0}
    
    def test_divide_by_zero(self):
        """Test division by zero."""
        response = client.post("/divide", json={"a": 10, "b": 0})
        assert response.status_code == 400
        assert "Division by zero" in response.json()["detail"]
    
    def test_divide_missing_field(self):
        """Test division with missing field."""
        response = client.post("/divide", json={"a": 10})
        assert response.status_code == 422
    
    def test_divide_invalid_type(self):
        """Test division with invalid type."""
        response = client.post("/divide", json={"a": "invalid", "b": 5})
        assert response.status_code == 422


class TestPowerEndpoint:
    """Test cases for the /power endpoint."""
    
    def test_power_positive_numbers(self):
        """Test power with positive numbers."""
        response = client.post("/power", json={"a": 2, "b": 3})
        assert response.status_code == 200
        assert response.json() == {"result": 8.0}
    
    def test_power_negative_base(self):
        """Test power with negative base."""
        response = client.post("/power", json={"a": -2, "b": 3})
        assert response.status_code == 200
        assert response.json() == {"result": -8.0}
    
    def test_power_fractional_exponent(self):
        """Test power with fractional exponent."""
        response = client.post("/power", json={"a": 4, "b": 0.5})
        assert response.status_code == 200
        assert abs(response.json()["result"] - 2.0) < 0.0001
    
    def test_power_zero_base(self):
        """Test power with zero base."""
        response = client.post("/power", json={"a": 0, "b": 5})
        assert response.status_code == 200
        assert response.json() == {"result": 0.0}
    
    def test_power_zero_exponent(self):
        """Test power with zero exponent."""
        response = client.post("/power", json={"a": 5, "b": 0})
        assert response.status_code == 200
        assert response.json() == {"result": 1.0}
    
    def test_power_missing_field(self):
        """Test power with missing field."""
        response = client.post("/power", json={"a": 2})
        assert response.status_code == 422
    
    def test_power_invalid_type(self):
        """Test power with invalid type."""
        response = client.post("/power", json={"a": "invalid", "b": 5})
        assert response.status_code == 422


class TestModuloEndpoint:
    """Test cases for the /modulo endpoint."""
    
    def test_modulo_positive_numbers(self):
        """Test modulo with positive numbers."""
        response = client.post("/modulo", json={"a": 10, "b": 3})
        assert response.status_code == 200
        assert response.json() == {"result": 1.0}
    
    def test_modulo_negative_dividend(self):
        """Test modulo with negative dividend."""
        response = client.post("/modulo", json={"a": -10, "b": 3})
        assert response.status_code == 200
        assert response.json() == {"result": -1.0}
    
    def test_modulo_decimal_numbers(self):
        """Test modulo with decimal numbers."""
        response = client.post("/modulo", json={"a": 10.5, "b": 3.2})
        assert response.status_code == 200
        assert abs(response.json()["result"] - 1.0) < 0.1
    
    def test_modulo_by_zero(self):
        """Test modulo by zero."""
        response = client.post("/modulo", json={"a": 10, "b": 0})
        assert response.status_code == 400
        assert "Modulo by zero" in response.json()["detail"]
    
    def test_modulo_missing_field(self):
        """Test modulo with missing field."""
        response = client.post("/modulo", json={"a": 10})
        assert response.status_code == 422
    
    def test_modulo_invalid_type(self):
        """Test modulo with invalid type."""
        response = client.post("/modulo", json={"a": "invalid", "b": 5})
        assert response.status_code == 422


class TestSqrtEndpoint:
    """Test cases for the /sqrt endpoint."""
    
    def test_sqrt_positive_number(self):
        """Test square root of positive number."""
        response = client.post("/sqrt", json={"value": 16})
        assert response.status_code == 200
        assert response.json() == {"result": 4.0}
    
    def test_sqrt_zero(self):
        """Test square root of zero."""
        response = client.post("/sqrt", json={"value": 0})
        assert response.status_code == 200
        assert response.json() == {"result": 0.0}
    
    def test_sqrt_decimal_number(self):
        """Test square root of decimal number."""
        response = client.post("/sqrt", json={"value": 2.25})
        assert response.status_code == 200
        assert response.json() == {"result": 1.5}
    
    def test_sqrt_negative_number(self):
        """Test square root of negative number."""
        response = client.post("/sqrt", json={"value": -16})
        assert response.status_code == 400
        assert "negative" in response.json()["detail"].lower()
    
    def test_sqrt_missing_field(self):
        """Test sqrt with missing field."""
        response = client.post("/sqrt", json={})
        assert response.status_code == 422
    
    def test_sqrt_invalid_type(self):
        """Test sqrt with invalid type."""
        response = client.post("/sqrt", json={"value": "invalid"})
        assert response.status_code == 422


class TestPercentageEndpoint:
    """Test cases for the /percentage endpoint."""
    
    def test_percentage_positive_numbers(self):
        """Test percentage calculation with positive numbers."""
        response = client.post("/percentage", json={"a": 25, "b": 100})
        assert response.status_code == 200
        assert response.json() == {"result": 25.0}
    
    def test_percentage_decimal_numbers(self):
        """Test percentage calculation with decimal numbers."""
        response = client.post("/percentage", json={"a": 10.5, "b": 50})
        assert response.status_code == 200
        assert response.json() == {"result": 21.0}
    
    def test_percentage_over_100(self):
        """Test percentage calculation over 100%."""
        response = client.post("/percentage", json={"a": 150, "b": 100})
        assert response.status_code == 200
        assert response.json() == {"result": 150.0}
    
    def test_percentage_by_zero(self):
        """Test percentage calculation with zero total."""
        response = client.post("/percentage", json={"a": 25, "b": 0})
        assert response.status_code == 400
        assert "zero" in response.json()["detail"].lower()
    
    def test_percentage_missing_field(self):
        """Test percentage with missing field."""
        response = client.post("/percentage", json={"a": 25})
        assert response.status_code == 422
    
    def test_percentage_invalid_type(self):
        """Test percentage with invalid type."""
        response = client.post("/percentage", json={"a": "invalid", "b": 100})
        assert response.status_code == 422


class TestFactorialEndpoint:
    """Test cases for the /factorial endpoint."""
    
    def test_factorial_positive_integer(self):
        """Test factorial of positive integer."""
        response = client.post("/factorial", json={"value": 5})
        assert response.status_code == 200
        assert response.json() == {"result": 120.0}
    
    def test_factorial_zero(self):
        """Test factorial of zero."""
        response = client.post("/factorial", json={"value": 0})
        assert response.status_code == 200
        assert response.json() == {"result": 1.0}
    
    def test_factorial_one(self):
        """Test factorial of one."""
        response = client.post("/factorial", json={"value": 1})
        assert response.status_code == 200
        assert response.json() == {"result": 1.0}
    
    def test_factorial_negative_number(self):
        """Test factorial of negative number."""
        response = client.post("/factorial", json={"value": -5})
        assert response.status_code == 400
        assert "non-negative integers" in response.json()["detail"]
    
    def test_factorial_non_integer(self):
        """Test factorial of non-integer."""
        response = client.post("/factorial", json={"value": 5.5})
        assert response.status_code == 400
        assert "non-negative integers" in response.json()["detail"]
    
    def test_factorial_missing_field(self):
        """Test factorial with missing field."""
        response = client.post("/factorial", json={})
        assert response.status_code == 422
    
    def test_factorial_invalid_type(self):
        """Test factorial with invalid type."""
        response = client.post("/factorial", json={"value": "invalid"})
        assert response.status_code == 422


class TestStatisticsEndpoint:
    """Test cases for the /statistics endpoint."""
    
    def test_statistics_positive_numbers(self):
        """Test statistics with positive numbers."""
        response = client.post("/statistics", json=[1, 2, 3, 4, 5])
        assert response.status_code == 200
        data = response.json()
        assert data["mean"] == 3.0
        assert data["min"] == 1.0
        assert data["max"] == 5.0
        assert data["sum"] == 15.0
    
    def test_statistics_negative_numbers(self):
        """Test statistics with negative numbers."""
        response = client.post("/statistics", json=[-5, -3, -1])
        assert response.status_code == 200
        data = response.json()
        assert abs(data["mean"] - (-3.0)) < 0.0001
        assert data["min"] == -5.0
        assert data["max"] == -1.0
        assert data["sum"] == -9.0
    
    def test_statistics_mixed_numbers(self):
        """Test statistics with mixed positive and negative numbers."""
        response = client.post("/statistics", json=[-2, 0, 2, 4])
        assert response.status_code == 200
        data = response.json()
        assert data["mean"] == 1.0
        assert data["min"] == -2.0
        assert data["max"] == 4.0
        assert data["sum"] == 4.0
    
    def test_statistics_decimal_numbers(self):
        """Test statistics with decimal numbers."""
        response = client.post("/statistics", json=[1.5, 2.5, 3.5])
        assert response.status_code == 200
        data = response.json()
        assert abs(data["mean"] - 2.5) < 0.0001
        assert data["min"] == 1.5
        assert data["max"] == 3.5
        assert abs(data["sum"] - 7.5) < 0.0001
    
    def test_statistics_empty_list(self):
        """Test statistics with empty list."""
        response = client.post("/statistics", json=[])
        assert response.status_code == 200
        data = response.json()
        assert data["mean"] == 0
        assert data["min"] == 0
        assert data["max"] == 0
        assert data["sum"] == 0
    
    def test_statistics_single_number(self):
        """Test statistics with single number."""
        response = client.post("/statistics", json=[42])
        assert response.status_code == 200
        data = response.json()
        assert data["mean"] == 42.0
        assert data["min"] == 42.0
        assert data["max"] == 42.0
        assert data["sum"] == 42.0
    
    def test_statistics_invalid_type(self):
        """Test statistics with invalid type."""
        response = client.post("/statistics", json="not a list")
        assert response.status_code == 422
