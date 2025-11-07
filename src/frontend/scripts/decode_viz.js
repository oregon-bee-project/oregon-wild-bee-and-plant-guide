import Papa from "papaparse";
import fluid from "infusion";
import pako from "pako";
import fs from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";
import { resolve } from "path";

// filename code
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

//register namespace
var simplex = fluid.registerNamespace("simplex");
//inflateUint8Array function
simplex.inflateUint8Array = async function (url) {
  const filePath = resolve(__dirname, url);
  const fileBuffer = await fs.readFile(filePath);
  const byteArray = new Uint8Array(fileBuffer);

  const inflated = pako.inflate(byteArray, { to: "string" });
  return inflated;
};

// parse function
simplex.parse = async function (url) {
  const data = await simplex.inflateUint8Array(url);
  const results = Papa.parse(data, { header: true, skipEmptyLines: true });
  return results.data;
};

//Usage
// Replace with .viz file
const url = "../b-data/plant-pollinators-OBA-2025-assigned-subset-labels.viz";

simplex.parse(url).then((parsed) => {
  console.log("Parsed rows:", parsed.length);
  console.log(parsed.slice(0, 3)); // preview first few rows
});
