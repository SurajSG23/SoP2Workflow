import { useMemo } from "react";
import "./upload-panel.scss";

interface UploadPanelProps {
  selectedFile: File | null;
  isProcessing: boolean;
  onFileSelected: (file: File) => void;
  onSubmit: () => void;
}

const ALLOWED_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
];

function UploadPanel({
  selectedFile,
  isProcessing,
  onFileSelected,
  onSubmit,
}: UploadPanelProps): JSX.Element {
  const fileLabel = useMemo(() => {
    if (!selectedFile) {
      return "No file selected";
    }

    return selectedFile.name;
  }, [selectedFile]);

  const handleDrop = (event: React.DragEvent<HTMLDivElement>): void => {
    event.preventDefault();
    if (isProcessing) {
      return;
    }

    const file = event.dataTransfer.files[0];
    if (file && ALLOWED_TYPES.includes(file.type)) {
      onFileSelected(file);
    }
  };

  const handleFileInput = (event: React.ChangeEvent<HTMLInputElement>): void => {
    const file = event.target.files?.[0];
    if (file && ALLOWED_TYPES.includes(file.type)) {
      onFileSelected(file);
    }
  };

  return (
    <section className="card upload-panel">
      <div
        className="upload-panel__dropzone"
        onDragOver={(event) => event.preventDefault()}
        onDrop={handleDrop}
      >
        <p className="upload-panel__title">Upload SOP Document</p>
        <p className="upload-panel__hint">Drag and drop PDF or DOCX files here</p>

        <label className="upload-panel__button">
          Select File
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileInput}
            disabled={isProcessing}
          />
        </label>

        <p className="upload-panel__file">{fileLabel}</p>
      </div>

      <button
        className="upload-panel__submit"
        type="button"
        disabled={!selectedFile || isProcessing}
        onClick={onSubmit}
      >
        {isProcessing ? "Processing..." : "Generate Workflow"}
      </button>
    </section>
  );
}

export default UploadPanel;
