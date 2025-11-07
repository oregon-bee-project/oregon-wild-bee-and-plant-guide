/*
* - This is a file that gets called every time you run "npm test".
* - It performs some test environment setup, such as mocking 
*   browser APIs used by Chakra UI that Node does not support.
*/

import '@testing-library/jest-dom';
import { vi } from "vitest";

// mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});
  
// mock ResizeObserver
class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}
global.ResizeObserver = ResizeObserver;

const originalError = console.error;
console.error = (...args) => {
  if (args[0].includes('Error: Could not parse CSS stylesheet')) {
    return;
  }
  originalError(...args);
};

// Mock MapLibre so WebGL never initializes in test environment
vi.mock("maplibre-gl", () => {
  return {
    default: {
      Map: function () {
        return {
          on: () => {},
          remove: () => {},
          addControl: () => {},
          setCenter: () => {},
          setZoom: () => {},
        };
      }
    }
  };
});