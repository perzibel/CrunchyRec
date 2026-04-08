# ================================================
# crunch_handler.py
# Main command handler for Crunchyroll automation
# ================================================

import argparse
import json
import os
import sys
from datetime import datetime
import Crunch_scrapper, Crunch_DB, Create_Recommendation_Prompt, Prase_history

CONFIG_FILE = "config.json"

# Default config if file doesn't exist
DEFAULT_CONFIG = {
    "email": "",
    "password": "",
    "use_local_db": True,
    "db_file": "crunchyroll_watched_db.json",
    "max_series_in_db": 50,
    "last_run": ""
}


def load_config():
    if not os.path.exists(CONFIG_FILE):
        print("⚠️  Config file not found. Creating a new one...")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            config = json.load(f)

        # Fill missing keys with defaults
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
        return config
    except:
        print("⚠️  Invalid config file. Using defaults.")
        return DEFAULT_CONFIG


def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def setup_config_if_needed():
    """Prompt user for credentials if config is empty"""
    config = load_config()

    if not config.get("email") or not config.get("password"):
        print("\n🔐 No login credentials found in config.")
        print("Would you like to save your Crunchyroll login details for future runs?")
        choice = input("Enter 'yes' to save credentials (recommended for automation): ").strip().lower()

        if choice in ['yes', 'y']:
            email = input("Enter your Crunchyroll Email: ").strip()
            password = input("Enter your Crunchyroll Password: ").strip()

            config["email"] = email
            config["password"] = password
            save_config(config)
            print("✅ Credentials saved securely in config.json")
        else:
            print("Continuing without saving credentials.")

    return config


def run_full_pipeline(config):
    """Run the complete workflow: Playwright → Rec → DB → Prompt"""
    print("🚀 Starting full Crunchyroll pipeline...")

    # Import and run your existing scripts
    try:
        # 1. Run Playwright scraper (update with your actual login logic if needed)
        from Crunch_scrapper import main as run_scraper  # assuming Crunch_scrapper.py has your playwright code
        # Or call your playwright script directly if it's in another file

        print("Step 1: Running scraper...")
        run_scraper(config["email"],config["password"])
        # For now we'll assume watch_history.json is generated

        # 2. Run analysis
        print("Step 2: Analyzing watch history...")
        from Crunch_Rec import main as run_rec
        run_rec()

        # 3. Update long-term DB
        if config.get("use_local_db", True):
            print("Step 3: Updating long-term database...")
            from Crunch_DB import update_db_from_report
            update_db_from_report()

        # 4. Generate prompt
        print("Step 4: Generating recommendation prompt...")
        from Create_Recommendation_Prompt import main as generate_prompt
        generate_prompt()

        config["last_run"] = datetime.now().isoformat()
        save_config(config)

        print("\n🎉 Full pipeline completed successfully!")

    except Exception as e:
        print(f"❌ Error during pipeline: {e}")


def add_watched_manually():
    """Manually add a series to the long-term DB"""
    from Crunch_DB import load_db, save_db

    db = load_db()

    print("\n➕ Manually adding a series to watched database")
    name = input("Series Name: ").strip()
    if not name:
        print("Cancelled.")
        return

    genres_input = input("Genres (comma separated, e.g. Action, Adventure): ").strip()
    genres = [g.strip() for g in genres_input.split(",") if g.strip()]

    try:
        score = float(input("Score (0-100): ").strip())
    except:
        score = 50.0

    maturity = input("Maturity Rating (e.g. TV-14, TV-MA): ").strip() or "Unknown"

    new_entry = {
        "series_name": name,
        "genres": genres,
        "score": score,
        "maturity_rating": maturity,
        "last_updated": datetime.now().isoformat()
    }

    db.append(new_entry)
    # Keep only top N
    db = sorted(db, key=lambda x: x.get("score", 0), reverse=True)[:50]

    save_db(db)
    print(f"✅ Added '{name}' to database. Total entries: {len(db)}")


def print_prompt_only():
    """Only generate and print the prompt to console"""
    try:
        from Create_Recommendation_Prompt import create_prompt
        from Crunch_scrapper import load_report  # or directly load recommendations.json
        report = load_report() if hasattr(load_report, '__call__') else json.load(
            open("crunchyroll_recommendations.json"))
        prompt = create_prompt(report)
        print("\n" + "=" * 80)
        print("📋 RECOMMENDATION PROMPT (copy everything below)")
        print("=" * 80)
        print(prompt)
    except Exception as e:
        print(f"❌ Could not generate prompt: {e}")


def main():
    config = setup_config_if_needed()

    parser = argparse.ArgumentParser(
        prog="crunch",
        description="Crunchyroll Watch History & Recommendation Manager"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Default run command
    parser_run = subparsers.add_parser("run", help="Run full pipeline (scrape → analyze → DB → prompt)")

    # Add watched
    parser_add = subparsers.add_parser("add_watched", help="Manually add a series to the long-term DB")

    # Print prompt only
    parser_prompt = subparsers.add_parser("prompt", help="Print current recommendation prompt to console")

    # Help is automatic with -h / --help

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "run":
        run_full_pipeline(config)
    elif args.command == "add_watched":
        add_watched_manually()
    elif args.command == "prompt":
        print_prompt_only()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
