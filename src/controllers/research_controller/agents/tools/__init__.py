from .googlesearch_tools import google_search,get_link_content 
from .arxiv_tools import arxiv_search
from .wikipedia_tools import search_wikipedia
from langchain_core.tools.base import BaseTool
from langchain_tavily import TavilySearch

arxiv_tools: list[BaseTool] = [arxiv_search]
google_tools: list[BaseTool] = [google_search,get_link_content]
wikipedia_tools:list[BaseTool]= [search_wikipedia]
websearch_tools:list[BaseTool]= [TavilySearch(max_results=10,topic="general")]