from langchain.tools import tool
import requests
from utils.logger import get_logger

_logs = get_logger(__name__)

def get_game_deals_from_service(query: str, min_rating: int = 3):
    """
    Fetches deals from CheapShark.
    - query: The game title.
    - min_rating: 0-10 scale (CheapShark's internal 'dealRating').
    """
    url = "https://www.cheapshark.com/api/1.0/deals"
    
    params = {
        "title": query,
        "dealRating": min_rating, # Filters out low-value deals
        "pageSize": 10, 
        "sortBy": "Deal Rating",   # Prioritizes the "best" deals first
        "storeID": 1 # filters only for Steam)
    }
    # If the AI passes a generic word like "top" or "any", ignore it.
    # Otherwise, search for the specific game title it asked for.
    if query.lower() not in ["top", "top game", "any", "best"]:
        params["title"] = query
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response

def format_cheapshark_data(response: requests.Response) -> str:
    deals = response.json()
    
    if not deals:
        return "Game I have found, a 'Great Deal' it is not."

    formatted_deals = []
    for i, deal in enumerate(deals[:3]):
        # CheapShark's dealRating is a string representation of a float (e.g., "9.5")
        rating = deal.get('dealRating', '0.0')
        
        formatted_deals.append(
            f"{i+1}. {deal['title']}: ${deal['salePrice']} "
            f"(Deal Quality: {rating}/10)"
            f"\Steam Link: https://store.steampowered.com/app/{deal['steamAppID']}/"
        )

    return "\n".join(formatted_deals)

@tool
def recommend_game(preferences: str) -> str:
    """
    Search for the best video game deals right now. 
    
    Instructions for the AI:
    - If the user asks for deals on a SPECIFIC game (e.g., "Batman", "Elden Ring"), pass that exact game title as the 'preferences' string.
    - If the user asks for GENERAL deals, "top games", "best deals", or doesn't name a specific game, pass the exact word "top" as the 'preferences' string.
    """
    
    # 1. Log the incoming request
    _logs.debug(f"Searching CheapShark for: {preferences}", "I am")

    # 2. Get the raw response from the web
    response = get_game_deals_from_service(preferences)
    
    # 3. Format that response into a string the AI can read
    game_deal = format_cheapshark_data(response)
    
    # 4. Log the result and return
    _logs.debug(f"Found game deals, I have: {game_deal}")
    return game_deal