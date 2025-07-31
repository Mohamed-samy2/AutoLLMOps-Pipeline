from .googlesearch_tools import google_search,get_link_content 
from .arxiv_tools import arxiv_search
from .wikipedia_tools import search_wikipedia
from langchain_core.tools.base import BaseTool
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from dotenv import load_dotenv
load_dotenv()

@tool(description="""
    Asynchronously inserts a piece of raw text along with its metadata into the database.

    This tool is useful for storing raw content extracted from various sources (e.g., web pages, 
    search results, documents) before processing or generating structured outputs like Q&A pairs.

    Args:
        text (str): The raw textual content to be stored.
        metadata (dict): A dictionary of additional information associated with the text 
                (e.g., source, URL, timestamp, query).
        db_client (optional): An instance of the database client responsible for executing the insertion.

    Returns:
        str: A success or failure message indicating the result of the insertion.
    """)
async def insert_raw_text(text: str, metadata: dict, db_client = None):
    
    result = await db_client.insert_raw_text(text, metadata)
    
    if result:
        return "Raw text inserted successfully."
    else:
        return "Failed to insert raw text."

arxiv_tools: list[BaseTool] = [arxiv_search,insert_raw_text]
google_tools: list[BaseTool] = [google_search,get_link_content, insert_raw_text]
wikipedia_tools:list[BaseTool]= [search_wikipedia, insert_raw_text]
websearch_tools:list[BaseTool]= [TavilySearch(max_results=10,topic="general"), insert_raw_text]
