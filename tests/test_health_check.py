"""Unit tests for health check functionality."""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from health_check import check_function_app_health


class TestHealthCheck:
    """Tests for the health check module."""

    @patch("health_check.requests.get")
    def test_health_check_success_on_first_attempt(self, mock_get):
        """Test successful health check on first attempt."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = check_function_app_health("test-app")
        assert result is True
        assert mock_get.call_count == 1

    @patch("health_check.requests.get")
    @patch("health_check.time.sleep")
    def test_health_check_succeeds_after_retries(self, mock_sleep, mock_get):
        """Test health check succeeds after initial failures."""
        mock_response = MagicMock()
        mock_response.status_code = 200

        # First two attempts fail with connection error, third succeeds
        mock_get.side_effect = [
            Exception("Connection refused"),
            Exception("Connection refused"),
            mock_response,
        ]

        result = check_function_app_health("test-app")
        assert result is True
        assert mock_get.call_count == 3
        assert mock_sleep.call_count == 2

    @patch("health_check.requests.get")
    def test_health_check_fails_with_non_200_status(self, mock_get):
        """Test health check fails when status code is not 200."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            check_function_app_health("test-app")

        assert "unexpected status" in str(exc_info.value)

    @patch("health_check.requests.get")
    @patch("health_check.time.sleep")
    def test_health_check_fails_after_max_retries(self, mock_sleep, mock_get):
        """Test health check fails after max retries exhausted."""
        mock_get.side_effect = Exception("Connection timeout")

        with pytest.raises(Exception) as exc_info:
            check_function_app_health("test-app")

        assert "after 3 attempts" in str(exc_info.value)
        assert mock_get.call_count == 3

    @patch("health_check.requests.get")
    def test_health_check_respects_custom_timeout(self, mock_get):
        """Test that custom timeout is passed to requests."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        check_function_app_health("test-app", timeout=20)

        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs["timeout"] == 20

    @patch("health_check.requests.get")
    def test_health_check_constructs_correct_url(self, mock_get):
        """Test that the correct URL is constructed."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        check_function_app_health("my-function-app")

        mock_get.assert_called_once_with("https://my-function-app.azurewebsites.net", timeout=10)
