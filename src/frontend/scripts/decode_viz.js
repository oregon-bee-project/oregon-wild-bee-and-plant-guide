import Papa from "papaparse";
import pako from "pako";
import fs from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";

// filename code
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Helper: inflate and return CSV text
async function inflateVizFile(relativePath) {
  const filePath = path.resolve(__dirname, relativePath);
  const fileBuffer = await fs.readFile(filePath);
  const byteArray = new Uint8Array(fileBuffer);

  return pako.inflate(byteArray, { to: "string" });
}

// Parse CSV string using PapaParse
async function parseViz(relativePath) {
  const csvText = await inflateVizFile(relativePath);
  const parsed = Papa.parse(csvText, {
    header: true,
    skipEmptyLines: true,
  });
  return parsed.data;
}

// Write JSON into same directory as source file
async function writeJson(relativePath, data) {
  const srcPath = path.resolve(__dirname, relativePath);
  const jsonPath = srcPath.replace(/\.viz$/i, ".json");

  await fs.writeFile(jsonPath, JSON.stringify(data, null, 2), "utf-8");
  console.log(`JSON written to: ${jsonPath}`);
}

// Usage
const url = "../b-data/plant-pollinators-OBA-2025-assigned-subset-labels.viz";

(async () => {
  const parsed = await parseViz(url);
  console.log("Parsed rows:", parsed.length);
  console.log(parsed.slice(0, 3));

  await writeJson(url, parsed);
})();
