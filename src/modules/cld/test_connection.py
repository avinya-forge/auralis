"""
Auralis - Cloud Connectivity Test Module
Implements validation for cloud providers.
"""

import logging
from typing import Dict, Optional

import requests

logger = logging.getLogger(__name__)


def validate_cloud_endpoint(
    url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 5
) -> bool:
    """
    Pings a cloud provider endpoint to verify connectivity.

    Args:
        url: The endpoint URL to validate.
        headers: Optional headers (e.g., Authorization).
        timeout: Request timeout in seconds.

    Returns:
        True if the endpoint returns a 2xx status code, False otherwise.
    """
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Cloud provider connectivity check failed for {url}: {e}")
        return False
