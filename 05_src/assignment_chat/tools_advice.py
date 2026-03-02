from langchain.tools import tool
import json
import requests


@tool
def get_advice(n:int=1):
    """
    Returns n pieces of advice from adviceslip.com API.
    """
    url = "https://api.adviceslip.com/advice"
    params = {
        "count": n
    }
    response = requests.get(url, params=params)
    resp_dict = json.loads(response.text)
    facts_list = resp_dict.get("data", [])
    facts = "\n".join([f"{i+1}. {fact}\n" for i, fact in enumerate(facts_list)])
    return facts

