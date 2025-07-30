from langchain_core.tools import tool
import wikipedia


@tool(description="""
    Searches Wikipedia and retrieves summaries and full content of up to 10 relevant pages.

    This tool performs a Wikipedia search using the provided query and attempts to fetch the summary
    and full content for the top 10 results. It is useful for getting quick overviews and detailed
    information on general knowledge topics.

    Parameters:
        query (str): The search term to look up on Wikipedia.

    Returns:
        str: A formatted string containing the page title, summary, and full content of up to 10 pages.
            If no good result is found, returns a message indicating that.
            If an error occurs during fetching, returns an error message.
    """)
async def search_wikipedia(query: str) -> str:
    """Run Wikipedia search and get page summaries."""
    page_titles = wikipedia.search(query)
    summaries = []
    for page_title in page_titles[: 10]:
        try:
            wiki_page =  wikipedia.page(title=page_title, auto_suggest=False)
            summaries.append(f"Page: {page_title}\nSummary: {wiki_page.summary}\nContent: {wiki_page.content}")
        except Exception as e:
            
            return  f"Error fetching URL"
    if not summaries:
        return "No good Wikipedia Search Result was found"
    return "\n\n".join(summaries)