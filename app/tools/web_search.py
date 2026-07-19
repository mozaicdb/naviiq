# Naviiq Web Search Tool
# Used by the decision engine and roadmap generator to fetch current career data
from ddgs import DDGS
import logging
import concurrent.futures
logger = logging.getLogger(__name__)
def search_web(query: str, max_results: int = 3, timeout: int = 8) -> str:
    """
    Search the web using DuckDuckGo and return a summary of results.
    Fails fast after timeout seconds instead of hanging.
    """
    def do_search():
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results))
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(do_search)
            results = future.result(timeout=timeout)
        if not results:
            return "No search results found."
        ad_patterns = ["bing.com/aclick", "googleadservices.com", "doubleclick.net", "/aclk?"]
        filtered_results = [
            r for r in results
            if not any(pattern in r.get("href", "") for pattern in ad_patterns)
        ]
        if not filtered_results:
            return "No search results found."
        summary = ""
        for i, result in enumerate(filtered_results, 1):
            title = result.get("title", "")
            body = result.get("body", "")
            url = result.get("href", "")
            summary += f"{i}. {title}: {body}\nURL: {url}\n\n"
        return summary.strip()
    except concurrent.futures.TimeoutError:
        logger.error(f"Web search timed out for query: {query}")
        return "Web search timed out."
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return "Web search unavailable."