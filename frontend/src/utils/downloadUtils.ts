/**
 * Download Utilities (M12)
 *
 * Testable file download helpers with dependency injection.
 * Extracted from CounterfactualConsole.tsx for coverage restoration (COV-002).
 */

/**
 * Dependencies for download operations.
 * Injectable for testing purposes.
 */
export interface DownloadDeps {
  createObjectURL: (blob: Blob) => string;
  revokeObjectURL: (url: string) => void;
  createLink: () => HTMLAnchorElement;
  appendToBody: (element: HTMLElement) => void;
  removeFromBody: (element: HTMLElement) => void;
  clickLink: (link: HTMLAnchorElement) => void;
}

/**
 * Default browser dependencies for download operations.
 * Uses standard DOM APIs.
 */
export const defaultDownloadDeps: DownloadDeps = {
  createObjectURL: (blob: Blob) => window.URL.createObjectURL(blob),
  revokeObjectURL: (url: string) => window.URL.revokeObjectURL(url),
  createLink: () => document.createElement("a"),
  appendToBody: (element: HTMLElement) => document.body.appendChild(element),
  removeFromBody: (element: HTMLElement) => document.body.removeChild(element),
  clickLink: (link: HTMLAnchorElement) => link.click(),
};

/**
 * Trigger a file download from a Blob.
 *
 * @param blob - The file content as a Blob
 * @param filename - The filename for the downloaded file
 * @param deps - Injectable dependencies (defaults to browser APIs)
 *
 * @example
 * ```typescript
 * const blob = await response.blob();
 * downloadBlob(blob, "report.pdf");
 * ```
 */
export function downloadBlob(
  blob: Blob,
  filename: string,
  deps: DownloadDeps = defaultDownloadDeps
): void {
  const url = deps.createObjectURL(blob);
  const link = deps.createLink();

  link.href = url;
  link.download = filename;

  deps.appendToBody(link);
  deps.clickLink(link);
  deps.removeFromBody(link);

  deps.revokeObjectURL(url);
}

/**
 * Generate filename for a CLARITY report PDF.
 *
 * @param caseId - The case identifier
 * @returns Formatted filename string
 */
export function generateReportFilename(caseId: string): string {
  return `clarity_report_${caseId}.pdf`;
}

