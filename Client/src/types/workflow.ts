export type ProcessingStage =
  | "Uploading document"
  | "Parsing document"
  | "Generating workflow"
  | "Rendering diagram";

export interface ProcessResponse {
  diagram: string;
}
