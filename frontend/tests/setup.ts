/**
 * Vitest test setup file.
 *
 * Configures testing environment with jest-dom matchers and MSW.
 *
 * M10: Added canvas mock for heatmap visualization tests.
 */

import "@testing-library/jest-dom/vitest";
import { beforeAll, afterEach, afterAll } from "vitest";
import { server } from "../src/mocks/server";

// Mock ImageData for jsdom (M10)
// ImageData is not available in jsdom without the canvas package
class MockImageData {
  public readonly data: Uint8ClampedArray;
  public readonly width: number;
  public readonly height: number;
  public readonly colorSpace: PredefinedColorSpace = "srgb";

  constructor(sw: number, sh: number);
  constructor(data: Uint8ClampedArray, sw: number, sh?: number);
  constructor(
    dataOrWidth: Uint8ClampedArray | number,
    swOrHeight: number,
    sh?: number
  ) {
    if (typeof dataOrWidth === "number") {
      this.width = dataOrWidth;
      this.height = swOrHeight;
      this.data = new Uint8ClampedArray(this.width * this.height * 4);
    } else {
      this.data = dataOrWidth;
      this.width = swOrHeight;
      this.height = sh ?? Math.floor(dataOrWidth.length / (swOrHeight * 4));
    }
  }
}

// Add to global
// eslint-disable-next-line @typescript-eslint/no-explicit-any
(globalThis as any).ImageData = MockImageData;

// Mock HTMLCanvasElement.getContext for jsdom (M10)
// This avoids needing to install the canvas npm package
const mockContext2d = {
  putImageData: () => {},
  getImageData: (_x: number, _y: number, w: number, h: number) =>
    new MockImageData(w, h),
  createImageData: (w: number, h: number) => new MockImageData(w, h),
  fillRect: () => {},
  clearRect: () => {},
  drawImage: () => {},
  scale: () => {},
  save: () => {},
  restore: () => {},
  beginPath: () => {},
  closePath: () => {},
  stroke: () => {},
  fill: () => {},
  rect: () => {},
  arc: () => {},
  moveTo: () => {},
  lineTo: () => {},
  setTransform: () => {},
  resetTransform: () => {},
  canvas: { width: 300, height: 300 },
};

HTMLCanvasElement.prototype.getContext = function (contextType: string) {
  if (contextType === "2d") {
    return mockContext2d as unknown as CanvasRenderingContext2D;
  }
  return null;
} as typeof HTMLCanvasElement.prototype.getContext;

// Establish API mocking before all tests
beforeAll(() => server.listen({ onUnhandledRequest: "error" }));

// Reset handlers after each test
afterEach(() => server.resetHandlers());

// Clean up after all tests
afterAll(() => server.close());
