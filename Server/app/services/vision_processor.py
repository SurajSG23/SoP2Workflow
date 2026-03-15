from __future__ import annotations

import json
import logging

from app.services.llm_client import call_llm, encode_image_bytes

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are analyzing an image extracted from a Standard Operating Procedure (SOP) document.

Describe what this image shows in the context of a business process or workflow.
Focus on: UI elements shown, process steps depicted, diagrams, flow arrows, form fields, buttons, or any instructional content.
Keep the description concise (1-2 sentences).

Respond ONLY in JSON format:
{"description": "<what the image shows in the SOP context>"}"""


class VisionProcessorService:
    def describe_images(self, images: list[bytes]) -> list[str]:
        descriptions: list[str] = []

        for index, image_bytes in enumerate(images, start=1):
            description = self._describe_single(image_bytes, index)
            descriptions.append(description)

        return descriptions

    def _describe_single(self, image_bytes: bytes, index: int) -> str:
        try:
            data_url = encode_image_bytes(image_bytes)
            messages = [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": data_url},
                        }
                    ],
                },
            ]

            result = call_llm(messages)
            if result:
                parsed = json.loads(result)
                return parsed.get("description", f"Image {index} from SOP document.")
        except Exception as exc:
            logger.error("Failed to describe image %d: %s", index, exc)

        return f"Image {index} from SOP document (description unavailable)."
