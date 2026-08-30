import logging

from app.neopat import get_all_drives, refresh_access_token
from app.normalizer import normalize_drive
from app.notion import sync_placement


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def sync_all():
    logger.info("Starting placement sync")

    access_token = refresh_access_token()
    drives = get_all_drives(access_token)

    logger.info("Fetched %d drives from NeoPAT", len(drives))

    created = 0
    updated = 0
    failed = 0

    for index, drive in enumerate(drives, start=1):
        company = drive.get("company_name", "Unknown")

        try:
            placement = normalize_drive(drive)
            result = sync_placement(placement)

            if result == "created":
                created += 1
            elif result == "updated":
                updated += 1

            logger.info(
                "[%d/%d] %s → %s",
                index,
                len(drives),
                company,
                result,
            )

        except Exception:
            failed += 1

            logger.exception(
                "[%d/%d] %s → FAILED",
                index,
                len(drives),
                company,
            )

    logger.info(
        "Sync complete | Created: %d | Updated: %d | Failed: %d",
        created,
        updated,
        failed,
    )


if __name__ == "__main__":
    sync_all()