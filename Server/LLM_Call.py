import os
import json
import time
import base64
import logging
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import requests
import urllib3

load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GENAI_URL = ""
MODEL_NAME = ""

TIMEOUT_SECONDS = 300
RETRIES = 3
RETRY_DELAY = 5

logging.basicConfig(level=logging.INFO)

# ---------------- PROMPT ---------------- #

FINAL_PROMPT = """
You are analyzing frames from a screen recording.

Your primary task is to track the mouse cursor (pointer) and describe exactly what the user is doing with it.

Rules:

1. Focus FIRST on the mouse cursor location.
2. Describe the UI element directly under or closest to the cursor.
3. If the cursor is hovering, say "Cursor hovering over <element>".
4. If the cursor appears to be clicking, say "Cursor clicking <element>".
5. If the cursor is moving without interacting, say "Cursor moving across <area>".
6. DO NOT guess actions that are not visually clear.
7. Only describe what is visible in the frame.
8. Mention the interface element (button, menu, text field, icon, tab, etc.).
9. Keep the description short (8-12 words).
10. If no cursor is visible, say "No cursor visible in this frame".

Examples:

* "Cursor hovering over Settings button in navigation bar"
* "Cursor clicking Save button in dialog window"
* "Cursor moving across document editing area"
* "Cursor hovering over search input field"

Respond ONLY in JSON format:

{
"description": "<cursor action and UI element>"
}
"""

# ---------------- UTILS ---------------- #

def ensure_base64_prefix(base64_string: str, mime_type: str = "image/png") -> str:
    if base64_string.startswith("data:"):
        return base64_string
    return f"data:{mime_type};base64,{base64_string}"


def encode_image_from_path(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def encode_image_from_url(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return base64.b64encode(response.content).decode("utf-8")


def build_payload(base64_image: str) -> Dict[str, Any]:
    return {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": FINAL_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": base64_image
                        }
                    }
                ]
            }
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"}
    }


def call_genai(payload: Dict[str, Any], headers: Dict[str, str]) -> Optional[str]:

    for attempt in range(RETRIES):

        try:

            response = requests.post(
                GENAI_URL,
                json=payload,
                headers=headers,
                timeout=TIMEOUT_SECONDS,
                verify=False
            )

            if response.status_code == 200:
                data = response.json()
                print("Desc: ", data)
                return data["choices"][0]["message"]["content"]

            logging.error(response.text)

        except requests.exceptions.Timeout:

            if attempt < RETRIES - 1:
                time.sleep(RETRY_DELAY)

        except Exception as e:
            logging.error(str(e))
            return None

    return None


# ---------------- MAIN FUNCTION ---------------- #

def describe_frames(video_id: str, frame_dir: str | None = None) -> List[Optional[str]]:
    """Call the LLM for all frames of a given video_id.

    Args:
        video_id: UUID identifying the video.
        frame_dir: Optional explicit path to the directory containing
            the extracted frame images.  When *None* the legacy path
            ``static/frames/{video_id}/`` is used for backwards compat.
    """
    print("Calling the model for video:", video_id)

    api_key = os.getenv("GENAI_API_KEY", "").strip()

    headers: Dict[str, str] = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # Locate frames on disk
    if frame_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        frame_dir = os.path.join(base_dir, "static", "frames", video_id)

    if not os.path.isdir(frame_dir):
        logging.error("Frame directory does not exist for video_id %s", video_id)
        return []

    frame_files = sorted(
        [f for f in os.listdir(frame_dir) if f.lower().endswith((".jpg", ".png"))]
    )

    results: List[Optional[str]] = []

    for frame_file in frame_files:
        frame_path = os.path.join(frame_dir, frame_file)
        try:
            print("Processing frame file:", frame_path)
            # Read image bytes directly from disk instead of going through HTTP
            base64_img = encode_image_from_path(frame_path)
            base64_img = ensure_base64_prefix(base64_img)

            payload = build_payload(base64_img)

            result = call_genai(payload, headers)
            description: Optional[str] = None

            if result:
                try:
                    parsed = json.loads(result)
                    description = parsed.get("description")
                except Exception:
                    # If the model didn't return valid JSON, fall back to raw text
                    description = result

            results.append(description)
        except Exception as e:
            logging.error("Error processing frame %s: %s", frame_path, str(e))
            results.append(None)

    return results