import os

from dotenv import load_dotenv
from notion_client import Client
from app.normalizer import normalize_drive
from app.neopat import get_all_drives, refresh_access_token

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
NOTION_DATA_SOURCE_ID = os.getenv("NOTION_DATA_SOURCE_ID")

if not NOTION_TOKEN:
    raise RuntimeError("NOTION_TOKEN is not set")

if not NOTION_DATABASE_ID:
    raise RuntimeError("NOTION_DATABASE_ID is not set")

if not NOTION_DATA_SOURCE_ID:
    raise RuntimeError("NOTION_DATA_SOURCE_ID is not set")


notion = Client(
    auth=NOTION_TOKEN,
    notion_version="2026-03-11",
)


def get_database():
    return notion.databases.retrieve(
        database_id=NOTION_DATABASE_ID
    )


def get_data_source(data_source_id):
    return notion.request(
        path=f"/data_sources/{data_source_id}",
        method="GET",
    )


def build_placement_properties(placement):
    return {
        "Company": {
            "title": [
                {
                    "text": {
                        "content": placement["company_name"]
                    }
                }
            ]
        },
        "CTC": {
            "rich_text": [
                {
                    "text": {
                        "content": placement["ctc"]
                    }
                }
            ]
        },
        "Application Date": {
            "date": {
                "start": placement["application_deadline"]
            }
        },
        "NeoPAT ID": {
            "rich_text": [
                {
                    "text": {
                        "content": placement["drive_id"]
                    }
                }
            ]
        },
    }


def create_placement(placement):
    properties = build_placement_properties(placement)

    response = notion.pages.create(
        parent={
            "data_source_id": NOTION_DATA_SOURCE_ID
        },
        properties=properties,
    )

    return response


def find_placement_by_neopat_id(neopat_id):
    response = notion.data_sources.query(
        data_source_id=NOTION_DATA_SOURCE_ID,
        filter={
            "property": "NeoPAT ID",
            "rich_text": {
                "equals": neopat_id,
            },
        },
    )

    results = response.get("results", [])

    if not results:
        return None

    return results[0]

def update_placement(page_id, placement):
    properties = build_placement_properties(placement)

    response = notion.pages.update(
        page_id=page_id,
        properties=properties,
    )

    return response

if __name__ == "__main__":
    access_token = refresh_access_token()
    drives = get_all_drives(access_token)

    groww = next(
        drive
        for drive in drives
        if drive.get("company_name") == "Groww"
    )

    placement = normalize_drive(groww)

    print("Normalized placement:")
    print(placement)

    result = find_placement_by_neopat_id(
        placement["drive_id"]
    )

    if result:
        print("Placement already exists:")
        print(result["id"])

        updated = update_placement(
            result["id"],
            placement,
        )

        print("Updated Notion page:")
        print(updated["id"])

    else:
        created = create_placement(placement)

        print("Created Notion page:")
        print(created["id"])