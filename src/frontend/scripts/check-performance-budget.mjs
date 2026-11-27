import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";
import { gzip } from "node:zlib";

const gzipAsync = promisify(gzip);

const dist = fileURLToPath(new URL("../build/", import.meta.url));
const limits = {
  js: 2 * 1024 * 1024,
  css: 150 * 1024,
};

async function walk(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) files.push(...(await walk(path)));
    else files.push(path);
  }
  return files;
}

try {
  const files = await walk(dist);
  const assets = files.filter((file) => /\.(js|css)$/.test(file));
  const failures = [];
  for (const file of assets) {
    const extension = file.endsWith(".js") ? "js" : "css";
    const size = (await gzipAsync(await readFile(file))).byteLength;
    if (size > limits[extension]) {
      failures.push(
        `${file}: ${size} gzip bytes > ${limits[extension]} gzip byte ${extension} budget`,
      );
    }
  }
  if (failures.length) {
    console.error(failures.join("\n"));
    process.exitCode = 1;
  } else {
    console.log(
      `Performance budget passed for ${assets.length} JS/CSS assets.`,
    );
  }
} catch (error) {
  console.error("Missing production output. Run npm run build first.");
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
}
