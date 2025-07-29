from langchain_core.tools import tool
import wikipedia


@tool
def search_wikipedia(query: str) -> str:
    """Run Wikipedia search and get page summaries."""
    page_titles = wikipedia.search(query)
    summaries = []
    for page_title in page_titles[: 3]:
        try:
            wiki_page =  wikipedia.page(title=page_title, auto_suggest=False)
            summaries.append(f"Page: {page_title}\nSummary: {wiki_page.summary}\nContent: {wiki_page.content}")
        except Exception as e:
            
            return  f"Error fetching URL"
    if not summaries:
        return "No good Wikipedia Search Result was found"
    return "\n\n".join(summaries)