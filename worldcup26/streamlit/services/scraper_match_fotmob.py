import re
import os 
import time
import json
import asyncio
import pandas as pd

CACHE_DIR_MATCHES_FOTMOB = "worldcup26/json_matches_fotmob"
COOKIES_FILE = "worldcup26/data/fotmob_cookies.json"
os.makedirs(CACHE_DIR_MATCHES_FOTMOB, exist_ok=True)

def extract_url_fotmob(df: pd.DataFrame,home_team_whoscored: str,away_team_whoscored: str,round: str | None = None) -> str:
    """
    Extract the FotMob match URL from a fixtures dataset.

    This function searches for a match using the home team,
    away team, and round name, then returns the corresponding
    FotMob page URL.

    Args:
        df (pd.DataFrame): FotMob matches dataset.
        home_team_whoscored (str): Home team name.
        away_team_whoscored (str): Away team name.
        round (str | None, optional): Competition round name.

    Returns:
        str: FotMob match URL.

    Raises:
        TypeError: If input arguments have invalid types.
        KeyError: If required columns are missing.
        ValueError: If no matching match is found.
    """

    # 🔹 Validate input types
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    if not isinstance(home_team_whoscored, str):
        raise TypeError("home_team_whoscored must be a string")

    if not isinstance(away_team_whoscored, str):
        raise TypeError("away_team_whoscored must be a string")

    required_columns = ["home.name", "away.name", "round", "pageUrl"]

    # 🔹 Validate required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise KeyError(f"Missing required columns: {missing_columns}")

    matches = df[(df["home.name"] == home_team_whoscored)& (df["away.name"] == away_team_whoscored)& (df["round"] == round)]

    # 🔹 Ensure a match was found
    if matches.empty:
        raise ValueError(f"No FotMob match found for {home_team_whoscored} vs {away_team_whoscored} ({round})")

    return matches["pageUrl"].iloc[0]

def extract_match_id_fotmob(url: str) -> str:
    """
    Extract the FotMob match ID from a match URL.

    Args:
        url (str): FotMob match URL containing a match ID.

    Returns:
        str: Extracted match ID.

    Raises:
        TypeError: If url is not a string.
        ValueError: If a match ID cannot be extracted.
    """

    # 🔹 Validate input type
    if not isinstance(url, str):
        raise TypeError("url must be a string")

    match = re.search(r"#(\d+)", url)

    if not match:
        raise ValueError("Could not extract match ID from URL")

    return match.group(1)

def get_cache_path_fotmob(match_id: str) -> str:
    """
    Build the cache file path for a FotMob match.

    Args:
        match_id (str): FotMob match identifier.

    Returns:
        str: Full path to the cache file.

    Raises:
        TypeError: If match_id is not a string.
        ValueError: If match_id is empty.
    """

    # 🔹 Validate input type
    if not isinstance(match_id, str):
        raise TypeError("match_id must be a string")

    if not match_id.strip():
        raise ValueError("match_id cannot be empty")

    return os.path.join(CACHE_DIR_MATCHES_FOTMOB, f"{match_id}.json")

def save_match_cache_fotmob( match_id: str, data: dict) -> None:
    """
    Save FotMob match data to the local cache.

    The match data is stored as a JSON file using the match ID
    as the filename.

    Args:
        match_id (str): FotMob match identifier.
        data (dict): Match data to cache.

    Returns:
        None

    Raises:
        TypeError: If input arguments have invalid types.
        RuntimeError: If the cache file cannot be written.
    """

    # 🔹 Validate input types
    if not isinstance(match_id, str):
        raise TypeError("match_id must be a string")

    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")

    cache_path_fotmob = get_cache_path_fotmob(match_id)

    payload = { "data": data}

    try:
        # 🔹 Save cache file
        with open(cache_path_fotmob, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)

    except Exception as e:
        raise RuntimeError(f"Failed to save match cache: {e}")

def load_match_cache_fotmob( match_id: str) -> dict | None:
    """
    Load cached FotMob match data.

    Args:
        match_id (str): FotMob match identifier.

    Returns:
        dict | None:
            Cached match data if available,
            otherwise None.

    Raises:
        TypeError: If match_id is not a string.
        RuntimeError: If the cache file cannot be read.
    """

    # 🔹 Validate input type
    if not isinstance(match_id, str):
        raise TypeError("match_id must be a string")

    cache_path_fotmob = get_cache_path_fotmob(match_id)

    # 🔹 Return None when cache does not exist
    if not os.path.exists(cache_path_fotmob):
        return None

    try:
        # 🔹 Load cached JSON data
        with open(cache_path_fotmob, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        raise RuntimeError(f"Failed to load match cache: {e}")

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
