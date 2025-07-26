import requests
import logging
from typing import Dict, Any, Optional

GEMINI_API_KEY = "AIzaSyAA9C7gcXx3xipslh8Ey3Po6poXrSXnKFM"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

logger = logging.getLogger("gemini_client")

def parse_log_with_gemini(log_message: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
    """
    Send a log message to Gemini API for entity extraction and summarization.
    Returns a dict with extracted entities and summary, or None on failure.
    """
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }
    data = {
        "contents": [
            {"parts": [{"text": f"Extract all entities (IP addresses, usernames, actions, timestamps) and summarize this log. Return a JSON object with keys: 'entities' (object with keys: timestamp, username, action, ip_address) and 'summary' (string). Log: {log_message}"}]}
        ]
    }
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        if "candidates" in result and result["candidates"]:
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            return {"gemini_response": text}
        logger.warning("No candidates in Gemini response: %s", result)
        return None
    except Exception as e:
        logger.error("Gemini API call failed: %s", e)
        return None 