from langchain_core.tools import tool
import requests
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
import os

@tool(description="""
    Performs a Google search using SerpAPI and retrieves the top 10 organic results.

    This tool is useful for finding general knowledge or supplementing specialized queries
    with broader contextual information. It returns a concatenated string of the result titles,
    snippets (previews), and links, separated for readability.

    Parameters:
        query (str): The search query to submit to Google.

    Returns:
        str: A formatted string containing the top 10 search results, each including:
            - Title of the result
            - Snippet (short description)
            - Link to the source
    """)
async def google_search(query:str):
    """Finds general knowledge information using Google search. Can also be used
    to augment more 'general' knowledge to a previous specialist query."""

    serpapi_params = {
        "engine": "google",
        "api_key": os.getenv("SERPAPI_KEY")
    }

    search = GoogleSearch({
        **serpapi_params,
        "q": query,
        "num": 10
    })
    
    results = search.get_dict()["organic_results"]
    contexts = "\n---\n".join(
        ["\n".join([x["title"], x["snippet"], x["link"]]) for x in results]
    )
    
    return contexts

@tool(description="""
    Fetches and extracts clean, readable text content from a web page URL.

    This tool sends an HTTP request to the provided URL, parses the HTML,
    removes all script, style, and noscript elements, and returns the visible text.
    It is useful for summarizing article content or extracting relevant information
    from a webpage.

    Parameters:
        url (str): The URL of the web page to fetch.

    Returns:
        str: Cleaned and readable text extracted from the web page.
            If an error occurs during the request, returns an error message.
    """)
async def get_link_content(url:str):
    try:
        # Send HTTP request
        response = requests.get(url, timeout=30)
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