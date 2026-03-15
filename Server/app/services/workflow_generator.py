from __future__ import annotations

import json
import logging

from app.models.workflow_schema import WorkflowData, WorkflowStep
from app.services.llm_client import call_llm

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are an expert at analyzing Standard Operating Procedure (SOP) documents.

Extract the key workflow steps from the provided SOP text as a sequential list of actions.

Rules:
1. Each step must be a clear, concise action phrase (5-15 words).
2. Steps must be sequential and actionable — what the user must do.
3. Extract between 4 and 12 steps.
4. Focus on the actions, not headers, footers, or metadata.
5. If image context is provided, use it to enrich or clarify the steps.

Respond ONLY in JSON format:
{"steps": ["<action 1>", "<action 2>", ...]}"""


class WorkflowGeneratorService:
    def generate(self, text: str, image_descriptions: list[str]) -> WorkflowData:
        steps = self._extract_steps_via_llm(text, image_descriptions)

        if not steps:
            steps = self._extract_steps_fallback(text)

        if not steps:
            steps = [
                "Open SOP document",
                "Review process instructions",
                "Execute process in target system",
                "Validate and complete task",
            ]

        workflow_steps = [
            WorkflowStep(id=self._index_to_node_id(i), action=step)
            for i, step in enumerate(steps)
        ]
        return WorkflowData(steps=workflow_steps)

    def _extract_steps_via_llm(self, text: str, image_descriptions: list[str]) -> list[str]:
        if not text.strip() and not image_descriptions:
            return []

        user_content = f"SOP Text:\n{text[:6000]}"
        if image_descriptions:
            image_context = "\n".join(
                f"Image {i + 1}: {desc}" for i, desc in enumerate(image_descriptions[:6])
            )
            user_content += f"\n\nImage Context:\n{image_context}"

        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]

        try:
            result = call_llm(messages)
            if result:
                parsed = json.loads(result)
                steps = parsed.get("steps", [])
                if isinstance(steps, list) and steps:
                    return [str(s).strip() for s in steps if str(s).strip()][:12]
        except Exception as exc:
            logger.error("LLM step extraction failed: %s", exc)

        return []

    def _extract_steps_fallback(self, text: str) -> list[str]:
        import re
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        normalized = [re.sub(r"^\d+[\).\-\s]+", "", line).strip() for line in lines]
        return [line for line in normalized if len(line) >= 8 and len(line.split()) >= 2][:12]

    @staticmethod
    def _index_to_node_id(index: int) -> str:
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if index < len(alphabet):
            return alphabet[index]
        return f"N{index + 1}"
