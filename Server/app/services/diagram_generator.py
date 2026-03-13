from __future__ import annotations

from app.models.workflow_schema import WorkflowData


class DiagramGeneratorService:
    def generate_mermaid(self, workflow: WorkflowData) -> str:
        if not workflow.steps:
            return "flowchart TD\nA[No workflow steps found]"

        lines = ["flowchart TD"]

        for step in workflow.steps:
            action = self._sanitize(step.action)
            lines.append(f"{step.id}[{action}]")

        for current, nxt in zip(workflow.steps, workflow.steps[1:]):
            lines.append(f"{current.id} --> {nxt.id}")

        return "\n".join(lines)

    @staticmethod
    def _sanitize(text: str) -> str:
        return text.replace("[", "(").replace("]", ")").replace('"', "'")
