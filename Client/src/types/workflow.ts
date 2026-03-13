export type ProcessingStage =
  | "Uploading document"
  | "Parsing document"
  | "Analyzing screenshots"
  | "Generating workflow"
  | "Rendering diagram";

export interface WorkflowStep {
  id: string;
  action: string;
}

export interface WorkflowData {
  steps: WorkflowStep[];
}

export interface ProcessResponse {
  diagram: string;
  workflow: WorkflowData;
}
