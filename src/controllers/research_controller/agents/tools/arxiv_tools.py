from langchain_core.tools import tool
import requests
import feedparser


@tool(description="""
    Search and retrieve the latest research papers from arXiv based on a given query.

    This tool sends a query to the arXiv API, retrieves up to 5 of the most recently submitted papers,
    and returns their titles, abstracts, and direct PDF download links.

    Parameters:
        query (str): The search term to look for in arXiv's database.

    Returns:
        List[Dict]: A list of dictionaries, each containing:
            - 'title': The title of the paper.
            - 'abstract': A brief summary of the paper.
            - 'pdf_url': A direct link to the PDF version of the paper.
    """)
async def arxiv_search(query:str):
    
    url = "https://export.arxiv.org/api/query"
    params = {
    "search_query": f"all:{query}",  # Search across all fields
    "start": 0,                      # Start index for results
    "max_results":5,                # Number of results to return
    "sortBy": "submittedDate",
    "sortOrder": "descending"
    }
    
    res = requests.get(url, params=params)

    # Parse the Atom feed
    feed = feedparser.parse(res.text)

    # Print titles and links
    results = []
    for entry in feed.entries:
        result = {
            "title": entry.title,
            "abstract": entry.summary,
            "pdf_url": entry.link.replace("abs", "pdf") + ".pdf",
        }
        results.append(result)

    return results


