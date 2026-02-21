/**
 * Download Utilities Tests (M12)
 *
 * Tests for the downloadBlob helper with dependency injection.
 * Coverage restoration for COV-002.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  downloadBlob,
  generateReportFilename,
  defaultDownloadDeps,
  type DownloadDeps,
} from "../src/utils/downloadUtils";

describe("downloadUtils", () => {
  describe("downloadBlob", () => {
    let mockDeps: DownloadDeps;
    let mockLink: HTMLAnchorElement;

    beforeEach(() => {
      // Create a mock link element
      mockLink = {
        href: "",
        download: "",
        click: vi.fn(),
      } as unknown as HTMLAnchorElement;

      // Create mock dependencies
      mockDeps = {
        createObjectURL: vi.fn(() => "blob:mock-url-12345"),
        revokeObjectURL: vi.fn(),
        createLink: vi.fn(() => mockLink),
        appendToBody: vi.fn(),
        removeFromBody: vi.fn(),
        clickLink: vi.fn(),
      };
    });

    it("should create an object URL from the blob", () => {
      const blob = new Blob(["test content"], { type: "application/pdf" });
      downloadBlob(blob, "test.pdf", mockDeps);

      expect(mockDeps.createObjectURL).toHaveBeenCalledTimes(1);
      expect(mockDeps.createObjectURL).toHaveBeenCalledWith(blob);
    });

    it("should create a link element", () => {
      const blob = new Blob(["test content"], { type: "application/pdf" });
      downloadBlob(blob, "test.pdf", mockDeps);

      expect(mockDeps.createLink).toHaveBeenCalledTimes(1);
    });

    it("should set the link href to the object URL", () => {
      const blob = new Blob(["test content"], { type: "application/pdf" });
      downloadBlob(blob, "test.pdf", mockDeps);

      expect(mockLink.href).toBe("blob:mock-url-12345");
    });

    it("should set the link download attribute to the filename", () => {
      const blob = new Blob(["test content"], { type: "application/pdf" });
      downloadBlob(blob, "my-report.pdf", mockDeps);

      expect(mockLink.download).toBe("my-report.pdf");
    });

    it("should append the link to the body", () => {
      const blob = new Blob(["test content"], { type: "application/pdf" });
      downloadBlob(blob, "test.pdf", mockDeps);

      expect(mockDeps.appendToBody).toHaveBeenCalledTimes(1);
      expect(mockDeps.appendToBody).toHaveBeenCalledWith(mockLink);
    });

    it("should click the link to trigger download", () => {
      const blob = new Blob(["test content"], { type: "application/pdf" });
      downloadBlob(blob, "test.pdf", mockDeps);

      expect(mockDeps.clickLink).toHaveBeenCalledTimes(1);
      expect(mockDeps.clickLink).toHaveBeenCalledWith(mockLink);
    });

    it("should remove the link from the body after clicking", () => {
      const blob = new Blob(["test content"], { type: "application/pdf" });
      downloadBlob(blob, "test.pdf", mockDeps);

      expect(mockDeps.removeFromBody).toHaveBeenCalledTimes(1);
      expect(mockDeps.removeFromBody).toHaveBeenCalledWith(mockLink);
    });

    it("should revoke the object URL after download", () => {
      const blob = new Blob(["test content"], { type: "application/pdf" });
      downloadBlob(blob, "test.pdf", mockDeps);

      expect(mockDeps.revokeObjectURL).toHaveBeenCalledTimes(1);
      expect(mockDeps.revokeObjectURL).toHaveBeenCalledWith("blob:mock-url-12345");
    });

    it("should execute operations in correct order", () => {
      const callOrder: string[] = [];

      const orderedDeps: DownloadDeps = {
        createObjectURL: vi.fn(() => {
          callOrder.push("createObjectURL");
          return "blob:url";
        }),
        revokeObjectURL: vi.fn(() => callOrder.push("revokeObjectURL")),
        createLink: vi.fn(() => {
          callOrder.push("createLink");
          return mockLink;
        }),
        appendToBody: vi.fn(() => callOrder.push("appendToBody")),
        removeFromBody: vi.fn(() => callOrder.push("removeFromBody")),
        clickLink: vi.fn(() => callOrder.push("clickLink")),
      };

      const blob = new Blob(["test"], { type: "text/plain" });
      downloadBlob(blob, "test.txt", orderedDeps);

      expect(callOrder).toEqual([
        "createObjectURL",
        "createLink",
        "appendToBody",
        "clickLink",
        "removeFromBody",
        "revokeObjectURL",
      ]);
    });

    it("should handle empty filename", () => {
      const blob = new Blob(["test content"], { type: "application/pdf" });
      downloadBlob(blob, "", mockDeps);

      expect(mockLink.download).toBe("");
      expect(mockDeps.clickLink).toHaveBeenCalled();
    });

    it("should handle filename with special characters", () => {
      const blob = new Blob(["test content"], { type: "application/pdf" });
      downloadBlob(blob, "report (1) [final].pdf", mockDeps);

      expect(mockLink.download).toBe("report (1) [final].pdf");
    });

    it("should handle empty blob", () => {
      const blob = new Blob([], { type: "application/pdf" });
      downloadBlob(blob, "empty.pdf", mockDeps);

      expect(mockDeps.createObjectURL).toHaveBeenCalledWith(blob);
      expect(mockDeps.clickLink).toHaveBeenCalled();
    });

    it("should handle large blob", () => {
      const largeContent = "x".repeat(10_000_000); // 10MB
      const blob = new Blob([largeContent], { type: "application/pdf" });
      downloadBlob(blob, "large.pdf", mockDeps);

      expect(mockDeps.createObjectURL).toHaveBeenCalledWith(blob);
      expect(mockDeps.clickLink).toHaveBeenCalled();
    });

    it("should handle different MIME types", () => {
      const jsonBlob = new Blob(['{"key": "value"}'], { type: "application/json" });
      downloadBlob(jsonBlob, "data.json", mockDeps);

      expect(mockDeps.createObjectURL).toHaveBeenCalledWith(jsonBlob);
      expect(mockLink.download).toBe("data.json");
    });
  });

  describe("generateReportFilename", () => {
    it("should generate filename with case_id", () => {
      const filename = generateReportFilename("case_001");
      expect(filename).toBe("clarity_report_case_001.pdf");
    });

    it("should handle alphanumeric case IDs", () => {
      const filename = generateReportFilename("abc123");
      expect(filename).toBe("clarity_report_abc123.pdf");
    });

    it("should handle case IDs with underscores", () => {
      const filename = generateReportFilename("test_case_042");
      expect(filename).toBe("clarity_report_test_case_042.pdf");
    });

    it("should handle case IDs with dashes", () => {
      const filename = generateReportFilename("case-001-final");
      expect(filename).toBe("clarity_report_case-001-final.pdf");
    });

    it("should handle empty case ID", () => {
      const filename = generateReportFilename("");
      expect(filename).toBe("clarity_report_.pdf");
    });

    it("should preserve case sensitivity", () => {
      const filename = generateReportFilename("CaseABC");
      expect(filename).toBe("clarity_report_CaseABC.pdf");
    });
  });

  describe("defaultDownloadDeps", () => {
    it("should have createObjectURL function", () => {
      expect(typeof defaultDownloadDeps.createObjectURL).toBe("function");
    });

    it("should have revokeObjectURL function", () => {
      expect(typeof defaultDownloadDeps.revokeObjectURL).toBe("function");
    });

    it("should have createLink function", () => {
      expect(typeof defaultDownloadDeps.createLink).toBe("function");
    });

    it("should have appendToBody function", () => {
      expect(typeof defaultDownloadDeps.appendToBody).toBe("function");
    });

    it("should have removeFromBody function", () => {
      expect(typeof defaultDownloadDeps.removeFromBody).toBe("function");
    });

    it("should have clickLink function", () => {
      expect(typeof defaultDownloadDeps.clickLink).toBe("function");
    });

    it("createLink should return an anchor element", () => {
      const link = defaultDownloadDeps.createLink();
      expect(link.tagName).toBe("A");
    });
  });
});

