// scripts/build-og.mjs
// Convert SVG OG cards → 1200×630 PNG using system Chrome (puppeteer-core).
// Why Chrome: native Korean font fallback + color emoji rendering.
// Run: `node scripts/build-og.mjs`
// Output: writes og-image.png + og/{claude,gpt,gemini,grok}.png
// Note: dev-only. Vercel build is NOT affected.

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import puppeteer from 'puppeteer-core';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, '..');

const TARGETS = [
  { src: 'og-image.svg',     out: 'og-image.png' },
  { src: 'og/claude.svg',    out: 'og/claude.png' },
  { src: 'og/gpt.svg',       out: 'og/gpt.png' },
  { src: 'og/gemini.svg',    out: 'og/gemini.png' },
  { src: 'og/grok.svg',      out: 'og/grok.png' },
];

// Try to find a usable Chromium-based browser executable on Windows.
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

// Wrap SVG in a borderless HTML page so we can screenshot a 1200×630 viewport.
function wrap(svg) {
  return `<!doctype html>
<html><head><meta charset="utf-8"><style>
  html,body{margin:0;padding:0;background:#0A0A0F;}
  svg{display:block;width:1200px;height:630px;}
</style></head><body>${svg}</body></html>`;
}

async function main() {
  const browserPath = process.env.CHROME_PATH || findBrowser();
  console.log(`[build-og] browser: ${browserPath}`);

  const browser = await puppeteer.launch({
    executablePath: browserPath,
    headless: 'new',
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
    defaultViewport: { width: 1200, height: 630, deviceScaleFactor: 1 },
  });

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
      // Wait one frame so any font fallback has resolved.
      await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));

      await mkdir(dirname(outAbs), { recursive: true });
      const buf = await page.screenshot({
        type: 'png',
        clip: { x: 0, y: 0, width: 1200, height: 630 },
        omitBackground: false,
      });
      await writeFile(outAbs, buf);
      await page.close();

      const kb = (buf.length / 1024).toFixed(1);
      const flag = buf.length > 200 * 1024 ? ' ⚠ >200KB' : '';
      console.log(`[build-og] wrote ${out} (${kb} KB)${flag}`);
    }
  } finally {
    await browser.close();
  }
}

main().catch((e) => { console.error(e); process.exit(1); });
