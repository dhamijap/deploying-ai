from langchain.tools import tool
import requests
import json
from utils.logger import get_logger

_logs = get_logger(__name__)
 
def get_game_deals_from_service(preferences: str):
    # CheapShark uses 'title' to filter by game name
    url = "https://www.cheapshark.com"
    params = {
        "title": preferences,
        "upperPrice": 15
    }
    # Using the [Requests Library](https://requests.readthedocs.io)
    response = requests.get(url, params=params)
    return response

def format_cheapshark_data(response: requests.Response) -> str:
    # CheapShark returns a list, so we parse it directly
    deals = response.json() 
    
    if not deals:
        return "Deals found, I have not."

    # Grab the top result
    top_deal = deals[0]
    return (f"Game: {top_deal['title']}, "
            f"Price: ${top_deal['salePrice']}, "
            f"Link: https://www.cheapshark.com{top_deal['dealID']}")

# How the @tool would call them:
@tool
def recommend_game(preferences: str) -> str:
    # 1. Log the incoming request
    _logs.debug(f"Searching CheapShark for: {preferences}")

    # 2. Get the raw response from the web
    response = get_game_deals_from_service(preferences)
    
    # 3. Format that response into a string the AI can read
    game_deal = format_cheapshark_data(response)
    
    # 4. Log the result and return
    _logs.debug(f"Result found: {game_deal}")
    return game_deal
