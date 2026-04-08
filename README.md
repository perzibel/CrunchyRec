# CrunchRec

**Your personal Crunchyroll watch history analyzer and anime recommendation engine.**

CrunchRec automatically scrapes your Crunchyroll watch history, analyzes your taste, builds a long-term database of series you've enjoyed, and generates smart AI-ready prompts for personalized anime recommendations.

---

## Features

- Automatic login and scraping of your Crunchyroll watch history
- Smart scoring system based on completion rate, episodes watched, and full watches
- Long-term watched series database (keeps your top 50 series)
- Detailed taste analysis (genres, maturity ratings, content descriptors)
- Generates high-quality prompts for any LLM (Grok, ChatGPT, Claude, etc.)
- Manual series addition to database
- Configurable credentials (no need to enter email/password every time)

---

## Project Structure

CrunchRec \
├── crunch_handler.py          # Main handler (run, add_watched, prompt) \
├── Crunch_Rec.py             # Watch history analysis & scoring \
├── Crunch_DB.py              # Long-term watched series database \
├── Create_Recommendation_Prompt.py  # Generates AI prompt \
├── config.json               # Your login + settings (auto-created) \
├── watch_history.json        # Latest raw history data \
├── crunchyroll_recommendations.json \
├── crunchyroll_watched_db.json  
└── crunchyroll_recommendation_prompt.txt 

------

## Installation & Setup

1. Clone the repository:
   git clone https://github.com/yourusername/CrunchRec.git
   cd CrunchRec
2. Install dependencies:
   pip install playwright
   playwright install chromium
3.Run the handler for the first time
   python crunchrec.py  ## It will automatically create config.json and ask you to save your Crunchyroll credentials.

# Usage
## Main Commands

### Run the full pipeline (scrape → analyze → update DB → generate prompt)
python crunchrec.py run

## Show help
python crunchrec.py -h

## Manually add a series to your watched database
python crunchrec.py add_watched

## Only generate and print the recommendation prompt
python crunchrec.py prompt

## Example Workflow

python crunchrec.py run → Full automation
Open crunchyroll_recommendation_prompt.txt
Copy the prompt and paste it into Grok / ChatGPT / Claude for personalized recommendations


## How Scoring Works

100 = You watched nearly all episodes fully and loved the series
High score = High completion rate + many episodes watched
Low score = Dropped after 1 episode or very low watch time
Bonus for fully watched episodes and quantity

## Files Explained

config.json – Stores your email, password, and settings
crunchyroll_watched_db.json – Your long-term taste profile (top 50 series)
crunchyroll_recommendation_prompt.txt – Ready-to-use prompt for any AI



## Disclaimer
This project is for personal educational use only.
Make sure to respect Crunchyroll's Terms of Service. Use at your own risk.

## Contributing
Feel free to open issues or pull requests if you want to improve scoring, add new features, or enhance the AI prompt.


# Made with ❤️ for anime fans who want better recommendations
