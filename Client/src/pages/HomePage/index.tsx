import { useMemo, useState } from "react";
import UploadPanel from "../../components/UploadPanel";
import ProcessingStatus from "../../components/ProcessingStatus";
import WorkflowViewer from "../../components/WorkflowViewer";
import { processDocument } from "../../services/api";
import type { ProcessingStage } from "../../types/workflow";
import "./home-page.scss";

const STAGES: ProcessingStage[] = [
  "Uploading document",
  "Parsing document",
  "Generating workflow",
  "Rendering diagram",
];

function HomePage(): JSX.Element {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStageIndex, setCurrentStageIndex] = useState<number>(-1);
  const [diagram, setDiagram] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const currentStage = useMemo<ProcessingStage | null>(() => {
    if (currentStageIndex < 0 || currentStageIndex >= STAGES.length) {
      return null;
    }
    return STAGES[currentStageIndex];
  }, [currentStageIndex]);

  const handleSubmit = async (): Promise<void> => {
    if (!selectedFile || isProcessing) {
      return;
    }

    setError(null);
    setDiagram(null);
    setIsProcessing(true);
    setCurrentStageIndex(0);

    const interval = window.setInterval(() => {
      setCurrentStageIndex((previous) =>
        previous < STAGES.length - 1 ? previous + 1 : previous
      );
    }, 800);

    try {
      const response = await processDocument(selectedFile);
      setDiagram(response.diagram);
      setCurrentStageIndex(STAGES.length - 1);
    } catch (submitError) {
      const message =
        submitError instanceof Error
          ? submitError.message
          : "Failed to generate workflow diagram.";
      setError(message);
      setCurrentStageIndex(-1);
    } finally {
      window.clearInterval(interval);
      setIsProcessing(false);
    }
  };

  return (
    <div className="home-page">
      <div className="home-page__left">
        <UploadPanel
          selectedFile={selectedFile}
          isProcessing={isProcessing}
          onFileSelected={setSelectedFile}
          onSubmit={handleSubmit}
        />
        {error && <p className="home-page__error">{error}</p>}
        <ProcessingStatus currentStage={currentStage} isProcessing={isProcessing} />
      </div>
      <div className="home-page__right">
        <WorkflowViewer diagram={diagram} isProcessing={isProcessing} />
      </div>
    </div>
  );
}

export default HomePage;
