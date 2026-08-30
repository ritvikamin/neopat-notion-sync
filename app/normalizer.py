from datetime import datetime


def format_lpa(amount):
    if amount is None:
        return None

    lpa = amount / 100000

    if lpa.is_integer():
        return f"{int(lpa)} LPA"

    return f"{lpa:.2f} LPA"


def extract_ctc(drive):
    salaries = drive.get("salary_information", [])

    if not salaries:
        return "TBA"

    highest_salary = None

    for salary in salaries:
        fixed_salary = salary.get("fixedSalary")
        to_range = salary.get("toRange")

        if fixed_salary is not None:
            value = fixed_salary
        elif to_range is not None:
            value = to_range
        else:
            continue

        if highest_salary is None or value > highest_salary:
            highest_salary = value

    if highest_salary is None:
        return "TBA"

    return format_lpa(highest_salary)


def format_deadline(last_date):
    if not last_date:
        return None

    date = datetime.fromisoformat(
        last_date.replace("Z", "+00:00")
    )

    return date.strftime("%Y-%m-%d")


def normalize_drive(drive):
    return {
        "drive_id": drive.get("drive_id"),
        "company_name": drive.get("company_name"),
        "ctc": extract_ctc(drive),
        "application_deadline": format_deadline(
            drive.get("lastDate")
        ),
    }