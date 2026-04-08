# ================================================
# Crunch_DB.py
# ================================================
# This file manages your long-term watched series database
# Keeps only the most important info: Title, Genres, Score

import json
import os
from collections import defaultdict

DB_FILE = "crunchyroll_watched_db.json"
MAX_SERIES_IN_DB = 50


def load_db():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)


def update_db_from_report():
    """Run this after Crunch_scrapper.py to update the long-term DB"""
    report_file = "crunchyroll_recommendations.json"

    if not os.path.exists(report_file):
        print(f"❌ {report_file} not found! Run Crunch_scrapper.py first.")
        return

    with open(report_file, encoding="utf-8") as f:
        report = json.load(f)

    db = load_db()

    # Create a set of existing series names for fast lookup
    existing_names = {item["series_name"].lower() for item in db}

    updated = False

    for entry in report:
        name = entry.get("series_name")
        if not name or name.lower() in existing_names:
            continue

        new_entry = {
            "series_name": name,
            "genres": entry.get("genres", []),
            "score": entry.get("score", 0),
            "maturity_rating": entry.get("maturity_rating", "Unknown"),
            "last_updated": entry.get("last_watched")
        }

        db.append(new_entry)
        existing_names.add(name.lower())
        updated = True
        print(f"Added to DB: {name} (Score: {entry.get('score')})")

    # Keep only the top MAX_SERIES_IN_DB by score
    if len(db) > MAX_SERIES_IN_DB:
        db = sorted(db, key=lambda x: x.get("score", 0), reverse=True)[:MAX_SERIES_IN_DB]
        print(f"DB trimmed to top {MAX_SERIES_IN_DB} series")

    save_db(db)
    print(f"✅ Database updated! Total series in DB: {len(db)}")


if __name__ == "__main__":
    update_db_from_report()