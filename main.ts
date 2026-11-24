import { copyFileSync, statSync, readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";

// News image for Monday 23 November 2026: the program is a deterministic
// copy of the front page this entry drew (entry.png, 1024x1024, 45 dated
// stories, 7 regions, real news photographs only). No network, no random
// input: the same bytes go out on every run.
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "out";
const src = join(dirname(fileURLToPath(import.meta.url)), "entry.png");
const dst = join(outDir, "entry.png");

copyFileSync(src, dst);

const bytes = statSync(dst).size;
if (bytes > 1048576) {
  throw new Error(`entry.png is ${bytes} bytes, over the 1 MiB limit`);
}

// The gate also caps the image at 1024x1024: read the PNG header (IHDR)
// and refuse anything larger instead of shipping it.
const head = readFileSync(dst).subarray(0, 33);
if (head.subarray(1, 4).toString("ascii") !== "PNG") {
  throw new Error("entry.png is not a PNG file");
}
const width = head.readUInt32BE(16);
const height = head.readUInt32BE(20);
if (width > 1024 || height > 1024) {
  throw new Error(`entry.png is ${width}x${height}, over the 1024x1024 limit`);
}
const sha256 = createHash("sha256").update(readFileSync(dst)).digest("hex");
console.log(`wrote ${dst} (${bytes} bytes, ${width}x${height}, sha256 ${sha256})`);
