from __future__ import annotations

import logging
import os
import time
from typing import Any

import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GENAI_URL: str = os.getenv("GENAI_URL", "")
MODEL_NAME: str = os.getenv("MODEL_NAME", "")
GENAI_API_KEY: str = os.getenv("GENAI_API_KEY", "")

TIMEOUT_SECONDS = 300
RETRIES = 3
RETRY_DELAY = 5

logger = logging.getLogger(__name__)


def _headers() -> dict[str, str]:
    h: dict[str, str] = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    if GENAI_API_KEY:
        h["Authorization"] = f"Bearer {GENAI_API_KEY}"
    return h


def call_llm(
    messages: list[dict[str, Any]],
    temperature: float = 0.2,
    json_mode: bool = False,
) -> str | None:
    """Send a chat completion request to the configured GenAI endpoint.

    Returns the raw content string from the first choice, or None on failure.
    Set json_mode=True only when the model is expected to return a JSON object.
    """
    if not GENAI_URL or not MODEL_NAME:
        logger.error("GENAI_URL or MODEL_NAME not configured in environment.")
        return None

    payload: dict[str, Any] = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": temperature,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    for attempt in range(RETRIES):
        try:
            response = requests.post(
                GENAI_URL,
                json=payload,
                headers=_headers(),
                timeout=TIMEOUT_SECONDS,
                verify=False,
            )
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            logger.error("LLM API error %s: %s", response.status_code, response.text)
        except requests.exceptions.Timeout:
            logger.warning("LLM request timed out (attempt %d/%d)", attempt + 1, RETRIES)
            if attempt < RETRIES - 1:
                time.sleep(RETRY_DELAY)
        except Exception as exc:
            logger.error("LLM request failed: %s", exc)
            return None

    return None
