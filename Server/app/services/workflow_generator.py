from __future__ import annotations

import re

from app.models.workflow_schema import WorkflowData, WorkflowStep


class WorkflowGeneratorService:
    def generate(self, text: str, image_descriptions: list[str]) -> WorkflowData:
        extracted_steps = self._extract_steps(text)

        if not extracted_steps and image_descriptions:
            extracted_steps = [
                f"Review screenshot context: {description}"
                for description in image_descriptions[:6]
            ]

        if not extracted_steps:
            extracted_steps = [
                "Open SOP document",
                "Review process instructions",
                "Execute process in target system",
                "Validate and complete task",
            ]

        workflow_steps = [
            WorkflowStep(id=self._index_to_node_id(index), action=step)
            for index, step in enumerate(extracted_steps)
        ]

        return WorkflowData(steps=workflow_steps)

    def _extract_steps(self, text: str) -> list[str]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        normalized_lines = [re.sub(r"^\d+[\).\-\s]+", "", line).strip() for line in lines]

        action_candidates = [line for line in normalized_lines if self._looks_like_step(line)]
        return action_candidates[:12]

    @staticmethod
    def _looks_like_step(line: str) -> bool:
        if len(line) < 8:
            return False
        if len(line.split()) < 2:
            return False
        return True

    @staticmethod
    def _index_to_node_id(index: int) -> str:
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if index < len(alphabet):
            return alphabet[index]
        return f"N{index + 1}"
