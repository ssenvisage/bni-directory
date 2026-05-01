#!/usr/bin/env python3

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "BNI Contact list(Sheet1).csv"
OUTPUT_PATH = ROOT / "members-data.js"


def clean(value):
    return (value or "").strip()


def sort_key(member):
    return member["name"].casefold()


def pick_phone(row):
    return clean(row.get("Cell")) or clean(row.get("Office"))


def pick_office_phone(row):
    office_phone = clean(row.get("Office"))
    cell_phone = clean(row.get("Cell"))
    return office_phone if office_phone and office_phone != cell_phone else ""


def load_members():
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with CSV_PATH.open("r", encoding=encoding, newline="") as csv_file:
                reader = csv.DictReader(csv_file)
                members = []

                for row in reader:
                    name = clean(row.get("Name"))
                    if not name:
                        continue

                    members.append(
                        {
                            "name": name,
                            "profession": clean(row.get("Service")),
                            "company": clean(row.get("Business Name")),
                            "category": clean(row.get("Industry")) or "General",
                            "bio": clean(row.get("Description")),
                            "phone": pick_phone(row),
                            "officePhone": pick_office_phone(row),
                            "email": clean(row.get("Email")),
                            "website": clean(row.get("Website")),
                            "logoUrl": "",
                        }
                    )

                return sorted(members, key=sort_key)
        except UnicodeDecodeError:
            continue

    raise UnicodeDecodeError("csv", b"", 0, 1, "Unable to decode CSV with known encodings")


def main():
    members = load_members()
    payload = "window.BNI_DIRECTORY_DATA = " + json.dumps(members, indent=2, ensure_ascii=True) + ";\n"
    OUTPUT_PATH.write_text(payload, encoding="utf-8")
    print(f"Wrote {len(members)} members to {OUTPUT_PATH.name}")


if __name__ == "__main__":
    main()
