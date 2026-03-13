import type { ProcessingStage } from "../../types/workflow";
import "./processing-status.scss";

interface ProcessingStatusProps {
  currentStage: ProcessingStage | null;
  isProcessing: boolean;
}

const STAGES: ProcessingStage[] = [
  "Uploading document",
  "Parsing document",
  "Analyzing screenshots",
  "Generating workflow",
  "Rendering diagram",
];

function ProcessingStatus({
  currentStage,
  isProcessing,
}: ProcessingStatusProps): JSX.Element {
  const activeIndex = currentStage ? STAGES.indexOf(currentStage) : -1;

  return (
    <section className="card processing-status">
      <h2>Processing Status</h2>
      <ul>
        {STAGES.map((stage, index) => {
          const status =
            index < activeIndex
              ? "done"
              : index === activeIndex
                ? "active"
                : "pending";

          return (
            <li key={stage} className={`processing-status__item ${status}`}>
              <span className="dot" />
              <span>{stage}</span>
            </li>
          );
        })}
      </ul>
      {!isProcessing && activeIndex < 0 && (
        <p className="processing-status__idle">
          Upload a document to begin workflow generation.
        </p>
      )}
    </section>
  );
}

export default ProcessingStatus;
