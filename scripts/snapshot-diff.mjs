#!/usr/bin/env node
/**
 * snapshot-diff.mjs — Visual regression detection for Phase B design transitions.
 *
 * Target URLs:
 *   https://ai-faction-quiz.vercel.app/
 *   https://ai-faction-quiz.vercel.app/r/claude
 *   (append ?seed=fixed for shuffle stability — app ignores for now, documents intent)
 *
 * Usage:
 *   node scripts/snapshot-diff.mjs --url <url> --baseline <path> [--threshold 0.05]
 *
 * Modes:
 *   Baseline mode  (--baseline file absent): capture + save, exit 0
 *   Diff mode      (--baseline file exists): compare → print diff% → exit 1 if > threshold
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import puppeteer from 'puppeteer-core';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// ---------------------------------------------------------------------------
// Arg parsing
// ---------------------------------------------------------------------------
const argv = process.argv.slice(2);
function getArg(name) {
  const idx = argv.indexOf(name);
  return idx !== -1 ? argv[idx + 1] : null;
}

const url = getArg('--url');
const baselinePath = getArg('--baseline');
const threshold = parseFloat(getArg('--threshold') ?? '0.05');

if (!url || !baselinePath) {
  console.error('Usage: node scripts/snapshot-diff.mjs --url <url> --baseline <path> [--threshold 0.05]');
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Chrome executable detection (Win / Mac / Linux)
// ---------------------------------------------------------------------------
function findChrome() {
  const candidates = [
    // Windows
    'C:\Program Files\Google\Chrome\Application\chrome.exe',
    'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    process.env.LOCALAPPDATA + '\Google\Chrome\Application\chrome.exe',
    // macOS
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    // Linux
    '/usr/bin/google-chrome',
    '/usr/bin/chromium-browser',
    '/usr/bin/chromium',
    '/snap/bin/chromium',
  ];
  for (const c of candidates) {
    if (c && fs.existsSync(c)) return c;
  }
  return null;
}

// ---------------------------------------------------------------------------
// Screenshot helper
// ---------------------------------------------------------------------------
async function takeScreenshot(targetUrl) {
  const executablePath = findChrome();
  if (!executablePath) {
    throw new Error(
      'Chrome not found. Install Google Chrome or set CHROME_PATH environment variable.'
    );
  }

  const browser = await puppeteer.launch({
    executablePath: process.env.CHROME_PATH || executablePath,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
    headless: true,
  });

  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 2 });
    await page.goto(targetUrl, { waitUntil: 'networkidle2', timeout: 30000 });
    const buf = await page.screenshot({ fullPage: true });
    return buf;
  } finally {
    await browser.close();
  }
}

// ---------------------------------------------------------------------------
// Pixel diff using sharp (preferred) or fallback byte comparison
// ---------------------------------------------------------------------------
async function computeDiff(bufA, bufB) {
  try {
    const sharp = (await import('sharp')).default;

    const imgA = sharp(bufA);
    const imgB = sharp(bufB);

    const [metaA, metaB] = await Promise.all([imgA.metadata(), imgB.metadata()]);

    // Resize B to match A dimensions if needed
    const width = metaA.width;
    const height = metaA.height;

    const [rawA, rawB] = await Promise.all([
      imgA.raw().toBuffer(),
      imgB.resize(width, height).raw().toBuffer(),
    ]);

    let diff = 0;
    const totalPixels = width * height;
    // raw buffer = RGBA (4 channels)
    for (let i = 0; i < rawA.length; i += 4) {
      const dr = Math.abs(rawA[i] - rawB[i]);
      const dg = Math.abs(rawA[i + 1] - rawB[i + 1]);
      const db = Math.abs(rawA[i + 2] - rawB[i + 2]);
      if (dr + dg + db > 30) diff++;
    }

    return diff / totalPixels;
  } catch {
    // Fallback: simple byte comparison
    const len = Math.max(bufA.length, bufB.length);
    let diff = 0;
    for (let i = 0; i < len; i++) {
      if ((bufA[i] ?? 0) !== (bufB[i] ?? 0)) diff++;
    }
    return diff / len;
  }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
const snapshotsDir = path.join(__dirname, 'snapshots');
if (!fs.existsSync(snapshotsDir)) fs.mkdirSync(snapshotsDir, { recursive: true });

const resolvedBaseline = path.isAbsolute(baselinePath)
  ? baselinePath
  : path.resolve(process.cwd(), baselinePath);

console.log(`URL       : ${url}`);
console.log(`Baseline  : ${resolvedBaseline}`);
console.log(`Threshold : ${(threshold * 100).toFixed(1)}%`);
console.log('');

const screenshot = await takeScreenshot(url);

if (!fs.existsSync(resolvedBaseline)) {
  // Baseline mode
  fs.mkdirSync(path.dirname(resolvedBaseline), { recursive: true });
  fs.writeFileSync(resolvedBaseline, screenshot);
  console.log(`Baseline saved: ${resolvedBaseline}`);
  process.exit(0);
}

// Diff mode
const baseline = fs.readFileSync(resolvedBaseline);
const diffRatio = await computeDiff(baseline, screenshot);
const diffPct = (diffRatio * 100).toFixed(2);

console.log(`Diff: ${diffPct}%`);

if (diffRatio > threshold) {
  console.error(`FAIL: diff ${diffPct}% exceeds threshold ${(threshold * 100).toFixed(1)}%`);
  process.exit(1);
} else {
  console.log('PASS');
  process.exit(0);
}
