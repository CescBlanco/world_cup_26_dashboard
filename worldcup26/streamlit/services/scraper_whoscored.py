import os
import re
import json
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup

#------------------------------------MANAGMENT SCRAPER WHOSCORED-------------------------------------------------
CACHE_DIR_MATCHES = "worldcup26/json_matches_whoscored"
os.makedirs(CACHE_DIR_MATCHES, exist_ok=True)

def extract_match_id(url: str) -> str:
    """
    Extract the WhoScored match ID from a match URL.

    Args:
        url (str): WhoScored match URL.

    Returns:
        str: Extracted match identifier.

    Raises:
        TypeError: If url is not a string.
        ValueError: If the match ID cannot be extracted.
    """

    # 🔹 Validate input type
    if not isinstance(url, str):
        raise TypeError("url must be a string")

    match = re.search(r"/matches/(\d+)/", url)

    # 🔹 Ensure a valid match ID was found
    if not match:
        raise ValueError("Could not extract match ID from URL")

    return match.group(1)

def get_cache_path(match_id: str) -> str:
    """
    Build the cache file path for a WhoScored match.

    Args:
        match_id (str): WhoScored match identifier.

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

    return os.path.join( CACHE_DIR_MATCHES, f"{match_id}.json")

def save_match_cache_whoscored(match_id: str,formation_mappings: dict,event_types_json: dict,matchdict: dict,players_dict: dict) -> None:
    """
    Save WhoScored match data to the local cache.

    The cache file stores formation mappings, event types,
    match metadata, and player information.

    Args:
        match_id (str): WhoScored match identifier.
        formation_mappings (dict): Formation mappings data.
        event_types_json (dict): Event types metadata.
        matchdict (dict): Match information dictionary.
        players_dict (dict): Player information dictionary.

    Returns:
        None

    Raises:
        TypeError: If any argument has an invalid type.
        RuntimeError: If the cache file cannot be written.
    """

    # 🔹 Validate input types
    if not isinstance(match_id, str):
        raise TypeError("match_id must be a string")

    if not isinstance(formation_mappings, dict):
        raise TypeError("formation_mappings must be a dictionary")

    if not isinstance(event_types_json, dict):
        raise TypeError("event_types_json must be a dictionary")

    if not isinstance(matchdict, dict):
        raise TypeError("matchdict must be a dictionary")

    if not isinstance(players_dict, dict):
        raise TypeError("players_dict must be a dictionary")

    cache_path = get_cache_path(match_id)

    data = {
        "formation_mappings": formation_mappings,
        "event_types_json": event_types_json,
        "matchdict": matchdict,
        "players_dict": players_dict
    }

    try:
        # 🔹 Persist cache data
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    except Exception as e:
        raise RuntimeError(f"Failed to save WhoScored cache: {e}")

def load_match_cache_whoscored( match_id: str) -> dict | None:
    """
    Load cached WhoScored match data.

    Args:
        match_id (str): WhoScored match identifier.

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

    cache_path = get_cache_path(match_id)

    # 🔹 Return None when cache file does not exist
    if not os.path.exists(cache_path):
        return None

    try:
        # 🔹 Load cached data
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        raise RuntimeError(f"Failed to load WhoScored cache: {e}")

def extract_match_dict_url(url: str) -> tuple[dict, dict, dict, dict]:
    """
    Extract match metadata from a WhoScored match page.

    This function loads a match page using Selenium, parses the
    embedded JavaScript objects, and extracts formation mappings,
    event type definitions, match data, and player information.

    Args:
        url (str): WhoScored match URL.

    Returns:
        tuple[dict, dict, dict, dict]:
            A tuple containing:
            - formation_mappings
            - event_types_json
            - matchdict
            - players_dict

    Raises:
        TypeError: If url is not a string.
        ValueError: If required page data cannot be extracted.
        RuntimeError: If page loading or parsing fails.
    """

    # 🔹 Validate input type
    if not isinstance(url, str):
        raise TypeError("url must be a string")

    driver = None

    try:
        # 🔹 Load match page
        driver = webdriver.Chrome()
        driver.get(url)

        # 🔹 Parse page source
        soup = BeautifulSoup( driver.page_source, "html.parser")

        # 🔹 Extract formation mappings
        element1 = soup.select_one( 'script:-soup-contains("formationIdNameMappings")')
        if element1 is None:
            raise ValueError("formationIdNameMappings not found in page source")

        formation_mappings = json.loads(element1.text.split("formationIdNameMappings:")[1].split("}")[0] + "}")

        # 🔹 Extract event type definitions
        element2 = soup.select_one('script:-soup-contains("matchCentreEventTypeJson")')
        if element2 is None:
            raise ValueError("matchCentreEventTypeJson not found in page source")

        event_types_json = json.loads(element2.text.split("matchCentreEventTypeJson: ")[1].split(",\n")[0])

        # 🔹 Extract match data
        element3 = soup.select_one('script:-soup-contains("matchCentreData")')
        if element3 is None:
            raise ValueError( "matchCentreData not found in page source")

        matchdict = json.loads(element3.text.split("matchCentreData: ")[1].split(",\n")[0] )

        # 🔹 Extract player dictionary
        if "playerIdNameDictionary" not in matchdict:
            raise ValueError("playerIdNameDictionary not found in match data")

        players_dict = matchdict["playerIdNameDictionary"]

        return (
            formation_mappings,
            event_types_json,
            matchdict,
            players_dict
        )

    except Exception as e:
        raise RuntimeError( f"Failed to extract match data from URL: {e}")

    finally:
        # 🔹 Ensure browser is always closed
        if driver is not None:
            driver.quit()