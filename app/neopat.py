import os
from urllib.parse import unquote

import requests
from dotenv import load_dotenv

load_dotenv()

REFRESH_URL = "https://api.neopat.ai/api/v1/auth/tokens/refresh/student"


def refresh_access_token():
    refresh_token = os.getenv("NEOPAT_REFRESH_TOKEN")

    if not refresh_token:
        raise RuntimeError("NEOPAT_REFRESH_TOKEN is not set")

    refresh_token = unquote(refresh_token)

    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/json",
        "Origin": "https://vit.neopat.ai",
        "Referer": "https://vit.neopat.ai/",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        ),
    }

    response = requests.post(
        REFRESH_URL,
        json={"token": refresh_token},
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    token_data = data.get("data", {})

    access_token = (
        token_data.get("token")
        or token_data.get("access_token")
    )

    if not access_token:
        raise RuntimeError("NeoPAT did not return an access token")

    return access_token


if __name__ == "__main__":
    refresh_access_token()
    print("Successfully refreshed NeoPAT access token")