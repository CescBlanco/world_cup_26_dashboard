import os
import re
import json
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup

#------------------------------------MANAGMENT SCRAPER WHOSCORED-------------------------------------------------
CACHE_DIR_MATCHES = "worldcup26/data_matches"
os.makedirs(CACHE_DIR_MATCHES, exist_ok=True)

def extract_match_id(url):
    return re.search(r"/matches/(\d+)/", url).group(1)

def get_cache_path(match_id):
    return os.path.join(CACHE_DIR_MATCHES, f"{match_id}.json")

def save_match_cache_whoscored(match_id, formation_mappings, event_types_json, matchdict, players_dict):
    cache_path = get_cache_path(match_id)

    data = {
        "formation_mappings": formation_mappings,
        "event_types_json": event_types_json,
        "matchdict": matchdict,
        "players_dict": players_dict
    }

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

def load_match_cache_whoscored(match_id):
    cache_path = get_cache_path(match_id)

    if not os.path.exists(cache_path):
        return None

    with open(cache_path, "r", encoding="utf-8") as f:
        return json.load(f)
                    

def extract_match_dict_url(url):
    
    driver = webdriver.Chrome()
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    
    element1 = soup.select_one('script:-soup-contains("formationIdNameMappings")')
    formation_mappings = json.loads(element1.text.split("formationIdNameMappings:")[1].split("}")[0] + "}")

    element2 = soup.select_one('script:-soup-contains("matchCentreEventTypeJson")')
    event_types_json  = json.loads(element2.text.split("matchCentreEventTypeJson: ")[1].split(",\n")[0])

    element = soup.select_one('script:-soup-contains("matchCentreData")')
    matchdict = json.loads(element.text.split("matchCentreData: ")[1].split(",\n")[0])

    players_dict = matchdict['playerIdNameDictionary']

    return formation_mappings, event_types_json, matchdict, players_dict
