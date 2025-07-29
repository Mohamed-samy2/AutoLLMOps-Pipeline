from langchain_core.tools import tool
import requests
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
import os

@tool
def google_search(query:str):
    """Finds general knowledge information using Google search. Can also be used
    to augment more 'general' knowledge to a previous specialist query."""

    serpapi_params = {
        "engine": "google",
        "api_key": os.getenv("SERPAPI_KEY")
    }

    search = GoogleSearch({
        **serpapi_params,
        "q": query,
        "num": 5
    })
    
    results = search.get_dict()["organic_results"]
    contexts = "\n---\n".join(
        ["\n".join([x["title"], x["snippet"], x["link"]]) for x in results]
    )
    
    return contexts

@tool
def get_link_content(url:str):
    try:
        # Send HTTP request
        response = requests.get(url, timeout=20)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script/style tags
        for script_or_style in soup(["script", "style", "noscript"]):
            script_or_style.extract()

        # Get visible text and clean extra spaces
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines()]
        clean_text = "\n".join(line for line in lines if line)

        return clean_text

    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {e}"