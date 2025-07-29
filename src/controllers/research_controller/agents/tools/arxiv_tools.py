from langchain_core.tools import tool
import requests
import feedparser


@tool()
def arxiv_search(query:str):
    
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


