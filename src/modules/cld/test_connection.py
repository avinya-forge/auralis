import requests


def verify_connectivity(provider_url: str) -> bool:
    if not provider_url.startswith("https://"):
        return False
    try:
        response = requests.get(provider_url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False
