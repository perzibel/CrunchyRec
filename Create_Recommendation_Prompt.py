# ================================================
# Create_Recommendation_Prompt.py
# ================================================
# This script reads your full report and creates
# a high-quality prompt you can copy-paste into
# any AI (Grok, ChatGPT, Claude, etc.)

import json
import os
from datetime import datetime

REPORT_FILE = "crunchyroll_recommendations.json"
PROMPT_FILE = "crunchyroll_recommendation_prompt.txt"


def load_report():
    if not os.path.exists(REPORT_FILE):
        print(f"❌ {REPORT_FILE} not found!")
        print("Please run Crunch_scrapper.py first.")
        exit(1)

    with open(REPORT_FILE, encoding="utf-8") as f:
        return json.load(f)


def create_prompt(report):
    # Sort by score again (just in case)
    report = sorted(report, key=lambda x: x["score"], reverse=True)

    # Top watched & highest scored series
    top_series = report[:20]  # Take top 20 for good context

    prompt = f"""You are an expert anime recommendation assistant with deep knowledge of Crunchyroll content.

### My Crunchyroll Watching History & Taste Profile:

I have watched {len(report)} different series on Crunchyroll.

**Total watch time:** Approximately {round(sum(r['total_watch_minutes'] for r in report) / 60, 1)} hours

**My Top Highly Rated Series (I really enjoyed these):**
"""

    for i, r in enumerate(top_series[:12], 1):
        genres = ", ".join(r.get("genres", [])) if r.get("genres") else "N/A"
        descriptors = ", ".join(r.get("content_descriptors", [])) if r.get("content_descriptors") else "None"

        prompt += f"""{i}. **{r['series_name']}**
   - Score: {r['score']}/100
   - Episodes watched: {r['episodes_watched']}
   - Average completion: {r['avg_completion_percent']}%
   - Maturity: {r['maturity_rating']}
   - Genres/Categories: {genres}
   - Content: {descriptors}
"""

    # Add genre taste summary
    from collections import defaultdict
    genre_scores = defaultdict(list)
    for r in report:
        for g in r.get("genres", []):
            genre_scores[g].append(r["score"])

    if genre_scores:
        sorted_genres = sorted(genre_scores.items(), key=lambda x: sum(x[1]) / len(x[1]), reverse=True)
        prompt += "\n**My Genre Preferences (ranked by how much I liked them):**\n"
        for genre, scores in sorted_genres[:10]:
            avg = round(sum(scores) / len(scores), 1)
            prompt += f"- {genre}: {avg}/100\n"

    prompt += f"""
**My Content Preferences:**
- I tend to drop series very early if I don't like them (low tolerance for slow starts).
- I strongly prefer series where I finish most or all available episodes.
- Maturity level I usually watch: {top_series[0]['maturity_rating'] if top_series else 'TV-14'}

---

### Task:
Based on the above information about my taste, recommend **10 new anime series** that I haven't watched yet.

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

    print("✍️  Generating smart recommendation prompt...")
    prompt_text = create_prompt(report)

    # Save to file
    with open(PROMPT_FILE, "w", encoding="utf-8") as f:
        f.write(prompt_text)

    print("\n" + "=" * 80)
    print("✅ RECOMMENDATION PROMPT CREATED SUCCESSFULLY!")
    print("=" * 80)
    print(f"File saved as: {PROMPT_FILE}")
    print("\nYou can now open this file and copy the entire prompt into Grok, ChatGPT, Claude, or any other LLM.")
    print("The prompt contains your full taste profile for highly personalized recommendations.\n")

    # Optional: Print first 300 characters so you can see it
    print("Preview of prompt:")
    print("-" * 50)
    print(prompt_text[:450] + "...")


if __name__ == "__main__":
    main()