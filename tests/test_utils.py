"""Tests for utility functions."""

import pytest
from app.utils import (
    validate_division,
    calculate_percentage,
    round_to_precision,
    is_even,
    factorial,
    format_number,
    get_statistics
)


class TestValidateDivision:
    """Test cases for validate_division function."""
    
    def test_validate_division_non_zero(self):
        """Test validation with non-zero divisor."""
        assert validate_division(5) is True
        assert validate_division(-5) is True
        assert validate_division(0.1) is True
    
    def test_validate_division_zero(self):
        """Test validation with zero divisor."""
        assert validate_division(0) is False
        assert validate_division(0.0) is False


class TestCalculatePercentage:
    """Test cases for calculate_percentage function."""
    
    def test_calculate_percentage_positive(self):
        """Test percentage calculation with positive numbers."""
        assert calculate_percentage(25, 100) == 25.0
        assert calculate_percentage(50, 200) == 25.0
    
    def test_calculate_percentage_decimal(self):
        """Test percentage calculation with decimal numbers."""
        assert abs(calculate_percentage(10.5, 50) - 21.0) < 0.0001
    
    def test_calculate_percentage_over_100(self):
        """Test percentage calculation over 100%."""
        assert calculate_percentage(150, 100) == 150.0
    
    def test_calculate_percentage_zero_total(self):
        """Test percentage calculation with zero total raises ValueError."""
        with pytest.raises(ValueError, match="Total cannot be zero"):
            calculate_percentage(25, 0)


class TestRoundToPrecision:
    """Test cases for round_to_precision function."""
    
    def test_round_to_precision_default(self):
        """Test rounding with default precision (2)."""
        assert round_to_precision(3.14159) == 3.14
        assert round_to_precision(2.999) == 3.0
    
    def test_round_to_precision_custom(self):
        """Test rounding with custom precision."""
        assert round_to_precision(3.14159, 3) == 3.142
        assert round_to_precision(2.999, 0) == 3.0
        assert round_to_precision(3.14159, 4) == 3.1416


class TestIsEven:
    """Test cases for is_even function."""
    
    def test_is_even_positive(self):
        """Test is_even with positive numbers."""
        assert is_even(2) is True
        assert is_even(4) is True
        assert is_even(1) is False
        assert is_even(3) is False
    
    def test_is_even_negative(self):
        """Test is_even with negative numbers."""
        assert is_even(-2) is True
        assert is_even(-4) is True
        assert is_even(-1) is False
        assert is_even(-3) is False
    
    def test_is_even_zero(self):
        """Test is_even with zero."""
        assert is_even(0) is True


class TestFactorial:
    """Test cases for factorial function."""
    
    # def test_factorial_positive(self):
    #     """Test factorial with positive numbers."""
    #     assert factorial(0) == 1
    #     assert factorial(1) == 1
    #     assert factorial(2) == 2
    #     assert factorial(3) == 6
    #     assert factorial(4) == 24
    #     assert factorial(5) == 120
    # Test commented out to demonstrate missing coverage
    
    def test_factorial_negative(self):
        """Test factorial with negative number raises ValueError."""
        with pytest.raises(ValueError, match="Factorial is not defined for negative numbers"):
            factorial(-1)
        with pytest.raises(ValueError, match="Factorial is not defined for negative numbers"):
            factorial(-5)


class TestFormatNumber:
    """Test cases for format_number function."""
    
    def test_format_number_positive(self):
        """Test formatting positive numbers."""
        assert format_number(1234.56) == "1,234.56"
        assert format_number(1000.0) == "1,000.00"
    
    def test_format_number_negative(self):
        """Test formatting negative numbers."""
        assert format_number(-1234.56) == "-1,234.56"
    
    def test_format_number_small(self):
        """Test formatting small numbers."""
        assert format_number(0.5) == "0.50"
        assert format_number(42) == "42.00"


class TestGetStatistics:
    """Test cases for get_statistics function."""
    
    def test_get_statistics_positive_numbers(self):
        """Test statistics with positive numbers."""
        result = get_statistics([1, 2, 3, 4, 5])
        assert result["mean"] == 3.0
        assert result["min"] == 1.0
        assert result["max"] == 5.0
        assert result["sum"] == 15.0
    
    def test_get_statistics_negative_numbers(self):
        """Test statistics with negative numbers."""
        result = get_statistics([-5, -3, -1])
        assert abs(result["mean"] - (-3.0)) < 0.0001
        assert result["min"] == -5.0
        assert result["max"] == -1.0
        assert result["sum"] == -9.0
    
    def test_get_statistics_mixed_numbers(self):
        """Test statistics with mixed numbers."""
        result = get_statistics([-2, 0, 2, 4])
        assert result["mean"] == 1.0
        assert result["min"] == -2.0
        assert result["max"] == 4.0
        assert result["sum"] == 4.0
    
    def test_get_statistics_decimal_numbers(self):
        """Test statistics with decimal numbers."""
        result = get_statistics([1.5, 2.5, 3.5])
        assert abs(result["mean"] - 2.5) < 0.0001
        assert result["min"] == 1.5
        assert result["max"] == 3.5
        assert abs(result["sum"] - 7.5) < 0.0001
    
    def test_get_statistics_empty_list(self):
        """Test statistics with empty list."""
        result = get_statistics([])
        assert result["mean"] == 0
        assert result["min"] == 0
        assert result["max"] == 0
        assert result["sum"] == 0
    
    def test_get_statistics_single_number(self):
        """Test statistics with single number."""
        result = get_statistics([42])
        assert result["mean"] == 42.0
        assert result["min"] == 42.0
        assert result["max"] == 42.0
        assert result["sum"] == 42.0
