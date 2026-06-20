"""Sample test to verify pytest discovery and execution."""


def test_basic_functionality():
    """Example test that verifies basic functionality."""
    assert 1 + 1 == 2


def test_string_operations():
    """Example test for string operations."""
    text = "hello"
    assert text.upper() == "HELLO"
    assert len(text) == 5
