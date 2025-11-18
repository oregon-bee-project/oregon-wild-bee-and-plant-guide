import Papa from "papaparse";
import fluid from "infusion"; //for user interfaces
import pako from "pako"; //fetches zip and other compresssed files
import fs from "fs/promises";
import path from "path"; //imports the path module for working with file directories and paths
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

/**
 * Asynchronously fetches, inflates, and parses data from a given URL.
 * * Assumes the data at the URL is a compressed (e.g., gzipped) CSV file.
 * It uses Papa.parse to convert the CSV data into an array of objects.
 *
 * @param {string} url - The URL of the compressed data file to fetch and parse.
 * @returns {Promise<Array<object>>} A promise that resolves to an array of objects,
 * where each object represents a row from the CSV.
 */
simplex.parse = async function (url) {
  const data = await simplex.inflateUint8Array(url);
  const results = Papa.parse(data, { header: true, skipEmptyLines: true });
  return results.data;
};

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
