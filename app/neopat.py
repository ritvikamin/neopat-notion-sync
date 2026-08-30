import os
from urllib.parse import unquote

import requests
from dotenv import load_dotenv

load_dotenv()

REFRESH_URL = "https://api.neopat.ai/api/v1/auth/tokens/refresh/student"

DRIVES_URL = "https://api.neopat.ai/api/v1/drives/student/drives"

DEGREE_SPEC = {
    "department_id": "5a3c4ccd-97dd-4eb7-b538-1fa14d0fe877",
    "programme_id": "af864992-ad1f-4107-b2da-5bb4386626d5",
    "degree_id": "60ef7af4-c4ab-4fc7-983c-9fb5be02cbd1",
}

PASSED_OUT_YEAR = 2027

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

def get_drives(access_token, page=1, limit=12):
    response = requests.post(
        DRIVES_URL,
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
            "Authorization": access_token,
            "Content-Type": "application/json",
            "Origin": "https://vit.neopat.ai",
            "Referer": "https://vit.neopat.ai/",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/151.0.0.0 Safari/537.36"
            ),
        },
        json={
            "page": page,
            "limit": limit,
            "passed_out_year": PASSED_OUT_YEAR,
            "degree_spec": DEGREE_SPEC,
            "source": [
                "_id",
                "name",
                "company_name",
                "company_logo",
                "profile_designation",
                "drive_type",
                "drive_id",
                "drive_number",
                "company_location",
                "salary_information",
                "lastDate",
                "drive_status",
                "drive_objective",
                "company_category",
                "createdAt",
                "updatedAt",
                "degree",
                "profileBased",
                "optionalFormData",
                "resumeUpload",
                "selectMultipleProfiles",
                "preference_count",
                "company_id",
                "opt_out_reason",
                "reasons",
                "removal_reason",
            ],
            "listType": "Ongoing",
            "sort": {
                "field": "lastDate",
                "order": "ASC",
            },
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()

def get_all_drives(access_token, limit=12):
    page = 1
    all_drives = []

    while True:
        data = get_drives(access_token, page=page, limit=limit)

        drives = data["data"]["data"]
        total = data["data"]["count"]

        all_drives.extend(drives)

        print(f"Fetched page {page}: {len(drives)} drives")

        if len(all_drives) >= total or not drives:
            break

        page += 1

    return all_drives

if __name__ == "__main__":
    access_token = refresh_access_token()

    drives = get_all_drives(access_token)

    print(f"Total drives: {len(drives)}")

    for drive in drives:
        print(
            drive["company_name"],
            "|",
            drive["lastDate"],
        )