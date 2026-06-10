import re
import os 
import time
import json
import asyncio

CACHE_DIR_MATCHES_FOTMOB = "worldcup26/json_matches_fotmob"
COOKIES_FILE = "worldcup26/data/fotmob_cookies.json"
os.makedirs(CACHE_DIR_MATCHES_FOTMOB, exist_ok=True)

def extract_url_fotmob(df, home_team_whoscored, away_team_whoscored, round=None):
    url_match_fotmob= df[(df['home.name'] == home_team_whoscored) & (df['away.name'] == away_team_whoscored) & (df['roundName'] ==round)]['pageUrl'].iloc[0]
    return url_match_fotmob

def extract_match_id_fotmob(url):
    return url.split("#")[-1]

def get_cache_path_fotmob(match_id):
    return os.path.join(CACHE_DIR_MATCHES_FOTMOB, f"{match_id}.json")

def save_match_cache_fotmob(match_id, data):
    cache_path_fotmob = get_cache_path_fotmob(match_id)

    data = {
        "data": data
    }

    with open(cache_path_fotmob, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

def load_match_cache_fotmob(match_id):
    cache_path_fotmob = get_cache_path_fotmob(match_id)

    if not os.path.exists(cache_path_fotmob):
        return None

    with open(cache_path_fotmob, "r", encoding="utf-8") as f:
        return json.load(f)

async def fetch_match_json( url):
        from patchright.async_api import async_playwright
        """
        Fetch match details JSON data using Playwright.

        This function navigates to a match URL, listens for network responses
        containing match details data, and captures the corresponding JSON payload.
        It also manages cookies to maintain session persistence.

        Args:
            url (str): Match URL containing the match ID.

        Returns:
            dict: JSON data containing match details.

        Raises:
            TypeError: If url is not a string.
            ValueError: If match ID cannot be extracted from the URL.
            RuntimeError: If browser launch or navigation fails.
            Exception: If match data is not captured within the expected time.
        """

        # 🔹 Input validation
        if not isinstance(url, str):
            raise TypeError("url must be a string")
        

        match_id_match = re.search(r"#(\d+)", url).group(1)

        if not match_id_match:
            raise ValueError("Could not extract match ID from URL")
    
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch( headless=True)

            except Exception as e:
                raise RuntimeError(f"Failed to launch browser: {e}")
            
            context = await browser.new_context()

            # 🔹 Load cookies if available and valid
            if os.path.exists(COOKIES_FILE):

                mod_time = os.path.getmtime(COOKIES_FILE)

                if (time.time() - mod_time) / 3600 > 1:
                    os.remove(COOKIES_FILE)
                    print("🗑️ Cookies expired")

                else:
                    with open(COOKIES_FILE) as f:
                        cookies = json.load(f)
                    await context.add_cookies(cookies)
                    print("🍪 Cookies loaded")

            page = await context.new_page()

            # 🔹 Store captured responses
            captured = []

            async def handle_response(response):
                """
                Capture matchDetails responses from network traffic.
                """
                if "matchDetails" in response.url and f"matchId={match_id_match}" in response.url:
                    print(f"🔥 DETECTED: {response.url}")
                    try:
                        data = await response.json()
                        captured.append(data)
                    except Exception as e:
                        print(f"⚠️ Error reading JSON: {e}")

            page.on("response", handle_response)

            try:
                print("\n🌐 Surfing the internet...")
                 # 🔹 Navigate to match page
                await page.goto(url, wait_until="domcontentloaded")

                # 🔹 Wait up to 60 seconds for matchDetails response
                print("⏳ Waiting for matchDetails (resolves the Turnstile if it appears)...")
                for _ in range(600):  # 60 segundos
                    if captured:
                        break
                    await asyncio.sleep(0.1)

                if not captured:
                    raise Exception("Match data was not captured within 60 seconds")

                # 🔹 Save cookies
                cookies = await context.cookies()
                with open(COOKIES_FILE, "w") as f:
                    json.dump(cookies, f, indent=2)
                print("🍪 Save Cookies")

                print("✅ DATA READY")
                return captured[0]

            finally:
                # 🔹 Ensure browser is closed
                await browser.close()
