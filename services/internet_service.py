# Folder: services/ | Plik: internet_service.py
import os
from tavily import TavilyClient

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

def execute_web_search(query: str) -> str:
    """
    Wykonuje zaawansowane wyszukiwanie w internecie w czasie rzeczywistym.
    Zwraca do agenta wyłącznie oczyszczony, merytoryczny kontekst tekstowy.
    """
    if not TAVILY_API_KEY:
        return "[SYSTEM ERROR: TAVILY_API_KEY is missing in cloud variables. Internet search is disabled.]"
    
    try:
        # Inicjalizujemy klienta Tavily
        tavily = TavilyClient(api_key=TAVILY_API_KEY)
        
        # Wykonujemy zapytanie o 3 najbardziej relewantne wyniki tekstowe
        response = tavily.search(query=query, search_depth="basic", max_results=3)
        
        results = []
        for result in response.get("results", []):
            title = result.get("title", "No Title")
            url = result.get("url", "")
            content = result.get("content", "")
            results.append(f"Source: {title} ({url})\nContext: {content}")
            
        if results:
            return "\n\n---\n\n".join(results)
        return "Search executed but no relevant public web contexts were found."
        
    except Exception as e:
        return f"Error occurred during web search execution: {str(e)}"
