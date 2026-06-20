"""Health check utilities for deployed Azure Function Apps."""

import requests
import time
from typing import bool


def check_function_app_health(
    app_name: str, resource_group: str = None, timeout: int = 10
) -> bool:
    """
    Check the health of a deployed Azure Function App.

    Args:
        app_name: The name of the Azure Function App (without .azurewebsites.net)
        resource_group: Resource group name (optional, for future use)
        timeout: Request timeout in seconds (default: 10)

    Returns:
        True if health check passes, False otherwise

    Raises:
        Exception: If all retry attempts fail
    """
    app_url = f"https://{app_name}.azurewebsites.net"
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            start_time = time.time()
            response = requests.get(app_url, timeout=timeout)
            elapsed = time.time() - start_time

            if response.status_code == 200:
                print(f"✓ Health check passed: HTTP {response.status_code} ({elapsed:.2f}s)")
                return True
            else:
                print(
                    f"⚠ Health check got unexpected status: HTTP {response.status_code}"
                )
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise Exception(
                        f"Health check failed after {max_retries} attempts. "
                        f"Last status: {response.status_code}"
                    )

        except requests.exceptions.Timeout:
            print(f"✗ Health check attempt {attempt + 1}/{max_retries} timed out")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise Exception(f"Health check failed: timeout after {max_retries} attempts")

        except requests.exceptions.ConnectionError as e:
            print(f"✗ Health check attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise Exception(
                    f"Health check failed: connection error after {max_retries} attempts"
                )

        except Exception as e:
            print(f"✗ Health check attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise

    return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python health_check.py <app_name>")
        sys.exit(1)

    app_name = sys.argv[1]
    try:
        result = check_function_app_health(app_name)
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"Health check failed: {e}")
        sys.exit(1)
