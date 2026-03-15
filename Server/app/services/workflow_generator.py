from __future__ import annotations

import logging
import re

from app.services.llm_client import call_llm

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are an expert in business process modeling (BPMN).
Task: Convert this guide that contains user actions performed into an accurate workflow diagram.
Follow this process:
STEP 1 — Extract workflow steps
Return a numbered list of atomic actions.
STEP 2 — Identify decision points
Mark steps that contain conditional logic.
STEP 3 — Determine step transitions
Determine the next step for each action.
STEP 4 — Create workflow structure
Represent the workflow using nodes and edges.
STEP 5 — Generate Mermaid diagram.
Rules:
- Start with "Start"
- End with "End"
- Use [] for actions
- Use {} for decisions
- Label decision edges Yes/No
- Preserve loops if present
Return ONLY valid Mermaid syntax that gets rendered in mermaid editor."""


class WorkflowGeneratorService:
    def generate(self, text: str) -> str:
        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ]

        result = call_llm(messages, temperature=0.2, json_mode=False)

        if result:
            return self._clean_mermaid(result)

        logger.warning("LLM unavailable — returning fallback diagram.")
        return self._fallback_diagram()

    @staticmethod
    def _clean_mermaid(raw: str) -> str:
        """Strip markdown code fences if the model wrapped the output."""
        raw = raw.strip()
        # Remove ```mermaid ... ``` or ``` ... ``` wrappers
        raw = re.sub(r"^```(?:mermaid)?\s*", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\s*```$", "", raw)
        return raw.strip()

    @staticmethod
    def _fallback_diagram() -> str:
        return (
            "flowchart TD\n"
            "    Start([Start]) --> A[Upload SOP document]\n"
            "    A --> B[LLM unavailable — configure GENAI_URL and MODEL_NAME in .env]\n"
            "    B --> End([End])"
        )
