// Build the era_data website into web/dist: the page and its scripts from web/static, and the triple store they load.
//
// Usage: node web/build.mjs
//
// The triple store is era_data.nt.gz from the era_data release RELEASE, checked against SHA256, the SHA-256 of the
// N-Triples text in it, as the python/ and rust/ packages check theirs; `mise run pin` writes both values here too.
// Set ERA_DATA_NT to the path of a local copy, such as the pipeline's build/era_data.nt.gz, to use that unchecked.

import { Buffer } from "node:buffer";
import { createHash } from "node:crypto";
import { createReadStream } from "node:fs";
import { cp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import process from "node:process";
import { Readable } from "node:stream";
import { pipeline } from "node:stream/promises";
import { fileURLToPath } from "node:url";
import { createGunzip } from "node:zlib";

const RELEASE = "data-v4";
const SHA256 = "bc68654497e876d01b82efea1fbf30cc8f75320d98ecc742cc9b87d764bcf5d6";
const FILE = "era_data.nt.gz";
const URL = `https://github.com/jayvdb/era_data/releases/download/${RELEASE}/${FILE}`;

const WEB = dirname(fileURLToPath(import.meta.url));
const STATIC = join(WEB, "static");
const DIST = join(WEB, "dist");

// Return the SHA-256, in hex, of the text the gzipped bytes decompress to.
async function textSha256(gzipped) {
  const hash = createHash("sha256");
  await pipeline(Readable.from([gzipped]), createGunzip(), hash);
  return hash.digest("hex");
}

// Return the gzipped triple store, and a description of where it came from for the page to show.
async function tripleStore() {
  const local = process.env.ERA_DATA_NT;
  if (local) {
    const chunks = [];
    for await (const chunk of createReadStream(local)) {
      chunks.push(chunk);
    }
    return [Buffer.concat(chunks), `a local copy of the triple store, ${local}`];
  }
  console.log(`Downloading ${URL}`);
  const response = await fetch(URL);
  if (!response.ok) {
    throw new Error(`${URL}: ${response.status} ${response.statusText}`);
  }
  const gzipped = Buffer.from(await response.arrayBuffer());
  const sha256 = await textSha256(gzipped);
  if (sha256 !== SHA256) {
    throw new Error(`${URL} holds N-Triples with SHA-256 ${sha256}, not ${SHA256}`);
  }
  return [gzipped, `the era_data release ${RELEASE}`];
}

const [gzipped, source] = await tripleStore();
await rm(DIST, { recursive: true, force: true });
await mkdir(DIST, { recursive: true });
await cp(STATIC, DIST, { recursive: true });
const index = join(DIST, "index.html");
await writeFile(index, (await readFile(index, "utf8")).replaceAll("{{source}}", source));
await writeFile(join(DIST, FILE), gzipped);
console.log(`Wrote ${DIST}, with ${gzipped.length} bytes of triple store from ${source}`);
