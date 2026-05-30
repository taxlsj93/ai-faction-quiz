// scripts/build-og.mjs
// Convert SVG OG cards → 1200×630 PNG using system Chrome (puppeteer-core).
// Why Chrome: native Korean font fallback + color emoji rendering.
// Run: `node scripts/build-og.mjs`
// Output: writes og-image.png + og/{claude,gpt,gemini,grok}.png
//
// D2 (v4.3 RALPLAN architect/critic gate):
// - Hard 200KB budget gate. If any output exceeds 200KB after sharp quality
//   step-down (none → 90 → 80 → 70), the script exits 1.
// - PNG is captured as full-quality from puppeteer first; only re-compressed
//   via sharp if oversized. This preserves text anti-aliasing for files that
//   already pass the budget.
// Note: dev-only. Vercel build is NOT affected.

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import puppeteer from 'puppeteer-core';
import sharp from 'sharp';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, '..');

const BUDGET_BYTES = 200 * 1024; // 200KB hard budget (FB / X / Kakao safe)
const QUALITY_STEPS = [null, 90, 80, 70]; // null = original puppeteer PNG

const TARGETS = [
  { src: 'og-image.svg',     out: 'og-image.png' },
  { src: 'og/claude.svg',    out: 'og/claude.png' },
  { src: 'og/gpt.svg',       out: 'og/gpt.png' },
  { src: 'og/gemini.svg',    out: 'og/gemini.png' },
  { src: 'og/grok.svg',      out: 'og/grok.png' },
];

function findBrowser() {
  const candidates = [
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
  ];
  for (const p of candidates) if (existsSync(p)) return p;
  throw new Error('No Chrome/Edge found. Install one or set CHROME_PATH env var.');
}

function wrap(svg) {
  return `<!doctype html>
<html><head><meta charset="utf-8"><style>
  html,body{margin:0;padding:0;background:#F5EFE6;}
  svg{display:block;width:1200px;height:630px;}
</style></head><body>${svg}</body></html>`;
}

// D2: Step down quality until under budget. Returns { buf, quality, attempts }.
async function compressUnderBudget(initialBuf) {
  if (initialBuf.length <= BUDGET_BYTES) {
    return { buf: initialBuf, quality: null, attempts: 1 };
  }
  for (let i = 1; i < QUALITY_STEPS.length; i++) {
    const q = QUALITY_STEPS[i];
    const compressed = await sharp(initialBuf).png({ quality: q, compressionLevel: 9, palette: true }).toBuffer();
    if (compressed.length <= BUDGET_BYTES) {
      return { buf: compressed, quality: q, attempts: i + 1 };
    }
  }
  // All steps failed
  return { buf: null, quality: null, attempts: QUALITY_STEPS.length };
}

async function main() {
  const browserPath = process.env.CHROME_PATH || findBrowser();
  console.log(`[build-og] browser: ${browserPath}`);
  console.log(`[build-og] budget: ${BUDGET_BYTES / 1024} KB per PNG`);

  const browser = await puppeteer.launch({
    executablePath: browserPath,
    headless: 'new',
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
    defaultViewport: { width: 1200, height: 630, deviceScaleFactor: 1 },
  });

  let failed = 0;

  try {
    for (const { src, out } of TARGETS) {
      const srcAbs = resolve(ROOT, src);
      const outAbs = resolve(ROOT, out);
      if (!existsSync(srcAbs)) {
        console.warn(`[build-og] skip missing: ${src}`);
        continue;
      }
      const svg = await readFile(srcAbs, 'utf8');
      const html = wrap(svg);

      const page = await browser.newPage();
      await page.setViewport({ width: 1200, height: 630, deviceScaleFactor: 1 });
      await page.setContent(html, { waitUntil: 'networkidle0' });
      await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));

      await mkdir(dirname(outAbs), { recursive: true });
      const rawBuf = await page.screenshot({
        type: 'png',
        clip: { x: 0, y: 0, width: 1200, height: 630 },
        omitBackground: false,
      });
      await page.close();

      const { buf, quality, attempts } = await compressUnderBudget(rawBuf);

      if (!buf) {
        const kb = (rawBuf.length / 1024).toFixed(1);
        console.error(`[build-og] ✗ ${out} (${kb} KB) — over budget after ${attempts} attempts. FAIL.`);
        failed++;
        continue;
      }

      await writeFile(outAbs, buf);
      const kb = (buf.length / 1024).toFixed(1);
      const note = quality === null
        ? '(original)'
        : `(sharp q=${quality}, ${attempts} attempts)`;
      console.log(`[build-og] ✓ ${out} (${kb} KB) ${note}`);
    }
  } finally {
    await browser.close();
  }

  if (failed > 0) {
    console.error(`[build-og] ${failed} file(s) exceeded ${BUDGET_BYTES / 1024}KB budget. Exit 1.`);
    process.exit(1);
  }
  console.log(`[build-og] all PNGs under budget. ✓`);
}

main().catch((e) => { console.error(e); process.exit(1); });
