from playwright.sync_api import sync_playwright
import json
import time


def print_ascii_notice():
    print(r"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ⚠️  TERMS OF USE NOTICE                                    ║
║                                                              ║
║   Pressing the "Log In" button means you accept              ║
║   the code Terms of Use.                                     ║
║                                                              ║
║   👉 Please refer to the GitHub page for full details.       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")


def main(email, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # or True if you accept higher detection risk
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-features=WebRtcHideLocalIpsWithMdns",  # sometimes helps
                "--disable-gpu",  # or keep it on depending on your machine
            ]
        )

        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
            locale="en-IL",
            timezone_id="Asia/Jerusalem",
            permissions=["geolocation"],
            java_script_enabled=True,
            accept_downloads=True,
            ignore_https_errors=False
        )

        context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });

        window.chrome = {
            runtime: {}
        };
        """)

        page = context.new_page()

        # === Login ===
        print("Going to login page...")
        page.goto("https://feedly.com/homepage", wait_until="networkidle")
        page.get_by_label("Log in").click()
        """
        page.get_by_label("Email Address").fill(email)
        page.get_by_role("textbox", name="Password").fill(password)

        print_ascii_notice()

        # Wait until logged in and redirected
        page.wait_for_url("https://www.crunchyroll.com/discover", timeout=120000)
        watch_history_data = None

        with page.expect_response(
                lambda response: "/watch-history" in response.url and response.status == 200,
                timeout=45000
        ) as response_info:
            page.goto("https://www.crunchyroll.com/history", wait_until="networkidle")

        # This will resolve when the matching XHR/fetch finishes
        api_response = response_info.value

        try:
            data = api_response.json()
            print("\n✅ Successfully captured watch history data!")
            print(f"Total items: {data.get('total', 'N/A')}")
            print(f"Entries received: {len(data.get('data', []))}")

            # Save to file
            with open("watch_history.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print("✅ Full data saved to watch_history.json")

            # Optional: show a small part
            if data.get("data"):
                print("\nFirst entry example:")
                print(json.dumps(data["data"][0], indent=2)[:800])

        except Exception as e:
            print("❌ Could not parse JSON:", e)
            print("Response URL was:", api_response.url)
            print("Status:", api_response.status)

        print("\nBrowser is kept open. Close the browser window when you're done.")
        print("\nBrowser will stay open.")
        browser.close()  # Optional: uncomment if you want to close automatically

"""
if __name__ == "__main__":
    EMAIL = ""
    PASSWORD = ""
    main(EMAIL, PASSWORD)
