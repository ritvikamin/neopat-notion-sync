import os

from dotenv import load_dotenv
from notion_client import Client

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
    response = notion.pages.create(
        parent={
            "data_source_id": NOTION_DATA_SOURCE_ID
        },
        properties=build_placement_properties(placement),
    )

    return response


def update_placement(page_id, placement):
    response = notion.pages.update(
        page_id=page_id,
        properties=build_placement_properties(placement),
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


def sync_placement(placement):
    existing = find_placement_by_neopat_id(
        placement["drive_id"]
    )

    if existing:
        update_placement(
            existing["id"],
            placement,
        )

        return "updated"

    create_placement(placement)

    return "created"