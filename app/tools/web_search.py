# Naviiq Web Search Tool
# Used by the decision engine and roadmap generator to fetch current career data

from ddgs import DDGS
import logging

logger = logging.getLogger(__name__)

def search_web(query: str, max_results: int = 3) -> str:
    """
    Search the web using DuckDuckGo and return a summary of results.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        
        if not results:
            return "No search results found."
        
        summary = ""
        for i, result in enumerate(results, 1):
            title = result.get("title", "")
            body = result.get("body", "")
            summary += f"{i}. {title}: {body}\n\n"
        
        return summary.strip()
    
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return "Web search unavailable."