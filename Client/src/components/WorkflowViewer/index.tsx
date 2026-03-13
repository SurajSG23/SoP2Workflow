import { useEffect, useMemo, useRef, useState } from "react";
import mermaid from "mermaid";
import "./workflow-viewer.scss";

interface WorkflowViewerProps {
  diagram: string | null;
  isProcessing: boolean;
}

mermaid.initialize({
  startOnLoad: false,
  securityLevel: "loose",
  theme: "base",
  themeVariables: {
    primaryColor: "#e8f5e9",
    primaryBorderColor: "#2e7d32",
    primaryTextColor: "#1f2933",
    lineColor: "#2e7d32",
  },
});

function WorkflowViewer({ diagram, isProcessing }: WorkflowViewerProps): JSX.Element {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [error, setError] = useState<string | null>(null);

  const diagramId = useMemo(
    () => `workflow-${Math.random().toString(36).slice(2, 10)}`,
    [diagram]
  );

  useEffect(() => {
    let cancelled = false;

    const renderDiagram = async (): Promise<void> => {
      if (!containerRef.current || !diagram) {
        return;
      }

      try {
        setError(null);
        const { svg } = await mermaid.render(diagramId, diagram);
        if (!cancelled && containerRef.current) {
          containerRef.current.innerHTML = svg;
        }
      } catch {
        if (!cancelled) {
          setError("Unable to render Mermaid diagram.");
        }
      }
    };

    void renderDiagram();

    return () => {
      cancelled = true;
    };
  }, [diagram, diagramId]);

  return (
    <section className="card workflow-viewer">
      <h2>Workflow Diagram</h2>
      {!diagram && !isProcessing && (
        <p className="workflow-viewer__placeholder">
          The generated workflow diagram will appear here.
        </p>
      )}
      {isProcessing && (
        <p className="workflow-viewer__placeholder">Generating workflow diagram...</p>
      )}
      {error && <p className="workflow-viewer__error">{error}</p>}
      <div ref={containerRef} className="workflow-viewer__canvas" />
    </section>
  );
}

export default WorkflowViewer;
