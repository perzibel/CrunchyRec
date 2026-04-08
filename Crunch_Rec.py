# ================================================
# Crunch_Rec.py
# ================================================

import json
from collections import defaultdict
import os

WATCH_HISTORY_FILE = "watch_history.json"
OUTPUT_REPORT_FILE = "crunchyroll_recommendations.json"


def load_watch_history():
    if not os.path.exists(WATCH_HISTORY_FILE):
        print(f"❌ {WATCH_HISTORY_FILE} not found! Run your main script first.")
        exit(1)

    with open(WATCH_HISTORY_FILE, encoding="utf-8") as f:
        return json.load(f)


def get_series_title(entry):
    """Safely extract series_title from panel.episode_metadata.series_title"""
    try:
        title = entry["panel"]["episode_metadata"]["series_title"]
        if title and isinstance(title, str) and title.strip():
            return title.strip()
    except (KeyError, TypeError):
        pass

    # Fallback 1: direct series_title
    try:
        title = entry.get("series_title")
        if title and isinstance(title, str) and title.strip():
            return title.strip()
    except:
        pass

    # Fallback 2: clean from title field
    title = entry.get("title", "Unknown Series")
    if " - " in title:
        title = title.split(" - ")[0]
    elif " Episode" in title:
        title = title.split(" Episode")[0]

    return title.strip()[:150]


def get_genres(entry):
    """Extract genres/categories from panel.episode_metadata.tenant_categories"""
    try:
        categories = entry["panel"]["episode_metadata"]["tenant_categories"]
        if isinstance(categories, list):
            genre_list = []
            for cat in categories:
                if isinstance(cat, str):
                    genre_list.append(cat.strip())
                elif isinstance(cat, dict):
                    name = cat.get("tenant_category") or cat.get("category") or str(cat)
                    if name and isinstance(name, str):
                        genre_list.append(name.strip())
            return [g for g in genre_list if g]
    except (KeyError, TypeError):
        pass

    # Root level fallback
    try:
        categories = entry.get("tenant_categories")
        if isinstance(categories, list):
            return [str(cat).strip() for cat in categories if str(cat).strip()]
    except:
        pass

    return []


def calculate_episode_completion(ep):
    """Returns completion % (0-100) for a single episode"""
    if ep.get("fully_watched"):
        return 100.0

    playhead_sec = ep.get("playhead", 0)
    duration_ms = ep.get("duration_ms", 1)
    duration_sec = duration_ms / 1000.0

    if duration_sec <= 0:
        return 0.0

    completion = (playhead_sec / duration_sec) * 100
    return min(100.0, completion)


def main():
    print("🚀 Loading Crunchyroll watch history...")
    history = load_watch_history()
    entries = history.get("data", [])

    if not entries:
        print("❌ No data found in watch_history.json")
        return

    print(f"✅ Loaded {len(entries)} watched episodes")

    # Group by series using parent_id
    series_groups = defaultdict(list)
    for entry in entries:
        series_id = entry.get("parent_id") or "unknown"
        series_groups[series_id].append(entry)

    print(f"📊 Found {len(series_groups)} unique series")

    # ====================== SCORING ======================
    report = []

    for series_id, episodes in series_groups.items():
        first_ep = episodes[0]

        # Get series name
        series_name = get_series_title(first_ep)
        series_name = series_name.strip()[:150]

        num_episodes = len(episodes)
        total_completion = 0.0
        total_watch_seconds = 0
        fully_watched_count = 0

        for ep in episodes:
            comp = calculate_episode_completion(ep)
            total_completion += comp

            if ep.get("fully_watched"):
                fully_watched_count += 1

            total_watch_seconds += ep.get("playhead", 0)

        avg_completion = total_completion / num_episodes if num_episodes > 0 else 0.0
        total_minutes = round(total_watch_seconds / 60, 1)

        # === SERIES SCORE (0-100) ===
        score = avg_completion * 0.6
        quantity_bonus = min(35, num_episodes * 2.5)
        score += quantity_bonus

        if fully_watched_count >= 5 and fully_watched_count == num_episodes:
            score += 25
        elif fully_watched_count >= num_episodes * 0.8:
            score += 15

        if num_episodes == 1 and avg_completion < 30:
            score -= 20

        score = round(max(0, min(100, score)), 1)

        # Last watched
        dates = [ep.get("date_played") for ep in episodes if ep.get("date_played")]
        last_watched = max(dates) if dates else None

        report.append({
            "series_id": series_id,
            "series_name": series_name,
            "genres": get_genres(first_ep),                    # ← Added correctly
            "episodes_watched": num_episodes,
            "fully_watched": fully_watched_count,
            "avg_completion_percent": round(avg_completion, 1),
            "total_watch_minutes": total_minutes,
            "last_watched": last_watched,
            "score": score,
            "maturity_rating": first_ep["panel"]["episode_metadata"]['maturity_ratings'],
            "content_descriptors": first_ep["panel"]["episode_metadata"]["content_descriptors"]
        })

    # Sort by score descending
    report.sort(key=lambda x: x["score"], reverse=True)

    # ====================== OUTPUT ======================
    print("\n" + "=" * 70)
    print("🎬 YOUR CRUNCHYROLL TASTE REPORT")
    print("=" * 70)
    print(f"Total series watched : {len(report)}")
    total_hours = round(sum(r['total_watch_minutes'] for r in report) / 60, 1)
    print(f"Total watch time      : {total_hours} hours")

    # Genre Analysis
    genre_scores = defaultdict(list)
    for r in report:
        for genre in r.get("genres", []):
            genre_scores[genre].append(r["score"])

    if genre_scores:
        print("\n🎯 YOUR GENRE / CATEGORY TASTE (100 = you loved it)")
        sorted_genres = sorted(
            genre_scores.items(),
            key=lambda x: sum(x[1]) / len(x[1]),
            reverse=True
        )
        for genre, scores in sorted_genres[:12]:
            avg_score = round(sum(scores) / len(scores), 1)
            print(f"   {genre}: {avg_score}/100  ({len(scores)} series)")
    else:
        print("\nℹ️  No genre/category data found (tenant_categories missing).")

    print("\n🏆 TOP 15 HIGHEST SCORED SERIES")
    for i, r in enumerate(report[:15], 1):
        genres_str = ", ".join(r.get("genres", []))[:80]
        print(f"{i:2d}. {r['series_name']}")
        print(f"    Score: {r['score']}/100  | Episodes: {r['episodes_watched']} "
              f"| Completion: {r['avg_completion_percent']}%  | Time: {r['total_watch_minutes']} min | {r['maturity_rating']} | {r['content_descriptors']}")
        if genres_str:
            print(f"    Genres : {genres_str}")
        if r.get('last_watched'):
            print(f"    Last watched: {r['last_watched'][:10]}")

    # Save full report
    with open(OUTPUT_REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Full report saved to → {OUTPUT_REPORT_FILE}")


if __name__ == "__main__":
    main()