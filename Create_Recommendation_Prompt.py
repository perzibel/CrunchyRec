# ================================================
# Create_Recommendation_Prompt.py
# ================================================

import json
import os
from datetime import datetime
from collections import defaultdict

# Assuming Crunch_DB is in your project (import it correctly)
try:
    from Crunch_DB import load_db  # Adjust the import if the class/module name is different
except ImportError:
    print("❌ Could not import Crunch_DB.load_db()")
    print("Make sure Crunch_DB.py is in the same folder or properly installed.")
    exit(1)

REPORT_FILE = "crunchyroll_recommendations.json"
PROMPT_FILE = "crunchyroll_recommendation_prompt.txt"


def load_report():
    if not os.path.exists(REPORT_FILE):
        print(f"❌ {REPORT_FILE} not found!")
        print("Please run Crunch_scrapper.py first.")
        return []  # Return empty list instead of exiting

    with open(REPORT_FILE, encoding="utf-8") as f:
        return json.load(f)


def combine_report_and_db(report, db_data):
    """
    Combine report and DB.
    - If series_name exists in report → use report version (priority)
    - Else use DB version
    """
    combined = {}

    # First add everything from report (higher priority)
    for item in report:
        name = item.get("series_name")
        if name:
            combined[name.lower()] = item  # Use lower case key for duplicate check

    # Add items from DB only if not already in report
    for item in db_data:
        name = item.get("series_name")
        if name and name.lower() not in combined:
            combined[name.lower()] = item

    # Return as list, sorted by score descending (report items have score, DB may not)
    return sorted(
        combined.values(),
        key=lambda x: x.get("score", 0),
        reverse=True
    )


def create_prompt(combined_data):
    if not combined_data:
        return "No data available to generate prompt."

    # Top watched & highest scored series (from combined data)
    top_series = combined_data[:20]

    prompt = f"""You are an expert anime recommendation assistant with deep knowledge of Crunchyroll content.

### My Crunchyroll Watching History & Taste Profile:

I have data on {len(combined_data)} different series on Crunchyroll.

**Total watch time:** Approximately {round(sum(r.get('total_watch_minutes', 0) for r in combined_data) / 60, 1)} hours in my most recent history view

**My Top Highly Rated Series (I really enjoyed these):**
"""

    for i, r in enumerate(top_series[:12], 1):
        genres = ", ".join(r.get("genres", [])) if r.get("genres") else "N/A"
        descriptors = ", ".join(r.get("content_descriptors", [])) if r.get("content_descriptors") else "None"

        prompt += f"""{i}. **{r.get('series_name', 'Unknown')}**
   - Score: {r.get('score', 'N/A')}/100
   - Episodes watched: {r.get('episodes_watched', 'N/A')}
   - Average completion: {r.get('avg_completion_percent', 'N/A')}%
   - Maturity: {r.get('maturity_rating', 'N/A')}
   - Genres/Categories: {genres}
   - Content: {descriptors}
"""

    # Genre taste summary (only from series that have a score)
    genre_scores = defaultdict(list)
    for r in combined_data:
        if r.get("score"):
            for g in r.get("genres", []):
                genre_scores[g].append(r["score"])

    if genre_scores:
        sorted_genres = sorted(
            genre_scores.items(),
            key=lambda x: sum(x[1]) / len(x[1]),
            reverse=True
        )
        prompt += "\n**My Genre Preferences (ranked by how much I liked them):**\n"
        for genre, scores in sorted_genres[:10]:
            avg = round(sum(scores) / len(scores), 1)
            prompt += f"- {genre}: {avg}/100\n"

    prompt += f"""
**My Content Preferences:**
- I tend to drop series very early if I don't like them (low tolerance for slow starts).
- I strongly prefer series where I finish most or all available episodes.
- Maturity level I usually watch: {top_series[0].get('maturity_rating', 'TV-14') if top_series else 'TV-14'}

---

### Task:
Based on the above information about my taste, recommend **10 new anime series** that I haven't watched yet (avoid anything already in my history).

**Requirements for recommendations:**
- Focus on series that match my high-scoring patterns (story, pacing, genres, tone).
- Include a mix of popular and hidden gems.
- For each recommendation, give:
  1. Series name
  2. Why it matches my taste (be specific, reference my top series or genres)
  3. Brief plot summary (2-3 sentences)
  4. Expected maturity rating
  5. Number of seasons/episodes available on Crunchyroll (if known)

Prioritize series with similar genres and vibe to my highest scored shows.
Avoid anything too similar to the ones I dropped early.

Today's date: {datetime.now().strftime('%B %d, %Y')}

Please format the response clearly and engagingly."""

    return prompt


def main():
    print("📖 Loading your Crunchyroll taste report...")
    report = load_report()

    print("📚 Loading database via Crunch_DB.load_db()...")
    try:
        db_data = load_db()  # Call your DB function
        if not isinstance(db_data, list):
            print("⚠️  DB returned non-list data. Converting to list.")
            db_data = list(db_data) if hasattr(db_data, '__iter__') else []
    except Exception as e:
        print(f"⚠️  Failed to load DB: {e}")
        db_data = []

    print(f"🔄 Combining report ({len(report)} items) + DB ({len(db_data)} items)...")
    combined = combine_report_and_db(report, db_data)

    print(f"✍️  Generating smart recommendation prompt using {len(combined)} total series...")
    prompt_text = create_prompt(combined)

    # Save to file
    with open(PROMPT_FILE, "w", encoding="utf-8") as f:
        f.write(prompt_text)

    print("\n" + "=" * 80)
    print("✅ RECOMMENDATION PROMPT CREATED SUCCESSFULLY!")
    print("=" * 80)
    print(f"File saved as: {PROMPT_FILE}")
    print(f"Total series used: {len(combined)} ({len(report)} from report + {len(combined) - len(report)} from DB)")
    print("\nYou can now open this file and copy the entire prompt into Grok, ChatGPT, Claude, or any other LLM.\n")

    # Preview
    print("Preview of prompt:")
    print("-" * 50)
    print(prompt_text[:500] + "..." if len(prompt_text) > 500 else prompt_text)


if __name__ == "__main__":
    main()