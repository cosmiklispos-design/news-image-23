// news-image-20261123 entry (Node 22, standard library only).
//
// The bundled entry.png sums up the world's news of Monday 23 November
// 2026 as a newspaper front page, "The World Today". This program checks
// the file is a complete PNG inside the bounty limits, then copies those
// exact bytes to /output/entry.png, so the judge sees precisely the file
// the repository holds.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const SRC = new URL('./entry.png', import.meta.url);
const DEST_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const MAX_BYTES = 1048576;
const MAX_SIDE = 1024;

// PNG signature: the first eight bytes of every PNG file.
const SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function fail(message) {
  throw new Error(`entry.png rejected: ${message}`);
}

function crc32(bytes) {
  // CRC-32 (IEEE) table, built once at startup.
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) {
      c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    }
    table[n] = c >>> 0;
  }
  let crc = 0xffffffff;
  for (const byte of bytes) {
    crc = table[(crc ^ byte) & 0xff] ^ (crc >>> 8);
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function readDimensions(png) {
  // The IHDR chunk follows the 8-byte signature; its first eight data
  // bytes are the width and height, big-endian.
  if (png.toString('ascii', 12, 16) !== 'IHDR') {
    fail('no IHDR chunk where the PNG header belongs');
  }
  return { width: png.readUInt32BE(16), height: png.readUInt32BE(20) };
}

function checkChunks(png) {
  // Walk the chunk list from the first chunk to IEND, verifying every
  // chunk's length fits the file and every CRC matches, so a truncated
  // or damaged image never reaches the judge.
  let pos = 8;
  let closed = false;
  while (pos + 12 <= png.length) {
    const length = png.readUInt32BE(pos);
    const type = png.toString('ascii', pos + 4, pos + 8);
    if (pos + 12 + length > png.length) {
      fail(`chunk ${type} runs past the end of the file`);
    }
    const wanted = png.readUInt32BE(pos + 8 + length);
    const got = crc32(png.subarray(pos + 4, pos + 8 + length));
    if (wanted !== got) fail(`chunk ${type} fails its CRC check`);
    pos += 12 + length;
    if (type === 'IEND') {
      closed = true;
      break;
    }
  }
  if (!closed) fail('no IEND chunk: the image is incomplete');
  if (pos !== png.length) fail('trailing bytes after the IEND chunk');
}

const png = readFileSync(SRC);
if (png.length > MAX_BYTES) {
  fail(`is ${png.length} bytes, over the 1 MiB limit`);
}
if (!png.subarray(0, 8).equals(SIGNATURE)) {
  fail('does not start with the PNG signature');
}
const { width, height } = readDimensions(png);
if (width > MAX_SIDE || height > MAX_SIDE) {
  fail(`is ${width}x${height}, over the 1024x1024 limit`);
}
checkChunks(png);

mkdirSync(DEST_DIR, { recursive: true });
copyFileSync(SRC, join(DEST_DIR, 'entry.png'));
console.log(`entry.png: ${width}x${height}, ${png.length} bytes -> ${join(DEST_DIR, 'entry.png')}`);
