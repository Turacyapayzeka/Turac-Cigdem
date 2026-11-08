#!/usr/bin/env node
/* Drone Shield filmi için kare render betiği.
 * Kullanım:
 *   node render/render.mjs                      -> render/out/drone-shield.mp4 (1080p, 30 fps)
 *   node render/render.mjs --stills 2,9,20,30   -> verilen saniyelerde PNG kareler (render/out/stills/)
 *   node render/render.mjs --start 34 --end 48  -> yalnızca bir aralığı render eder
 * Gereksinim: Playwright (Chromium) ve ffmpeg. Görseller yerel bir HTTP sunucusundan servis edilir
 * (file:// altında canvas "tainted" olur ve toDataURL çalışmaz).
 */
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright'); // require: NODE_PATH ile kurulu global Playwright da bulunur
import { spawn } from 'node:child_process';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const opt = (name, def) => { const i = args.indexOf('--' + name); return i >= 0 ? args[i + 1] : def; };
const OUT = path.resolve(ROOT, opt('out', 'render/out/drone-shield.mp4'));
const FPS = +opt('fps', 30);
const START = +opt('start', 0);
const END = opt('end', null);
const STILLS = opt('stills', null);
const CRF = opt('crf', '18');
const MIME = { '.html': 'text/html; charset=utf-8', '.jpg': 'image/jpeg', '.png': 'image/png', '.js': 'text/javascript', '.css': 'text/css' };

const server = http.createServer((req, res) => {
  const p = decodeURIComponent(req.url.split('?')[0]);
  const file = path.join(ROOT, 'animasyon', p === '/' ? 'index.html' : p);
  if (!file.startsWith(path.join(ROOT, 'animasyon')) || !fs.existsSync(file)) { res.statusCode = 404; return res.end('yok'); }
  res.setHeader('Content-Type', MIME[path.extname(file)] || 'application/octet-stream');
  fs.createReadStream(file).pipe(res);
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const port = server.address().port;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
page.on('pageerror', e => console.error('sayfa hatası:', e.message));
await page.goto(`http://127.0.0.1:${port}/index.html?render=1`);
await page.waitForFunction(() => window.__film && (window.__film.ready || window.__film.error), null, { timeout: 60000 });
const film = await page.evaluate(() => ({ DUR: window.__film.DUR, error: window.__film.error }));
if (film.error) { console.error(film.error); process.exit(1); }
const DUR = film.DUR;
const frameAt = async t => Buffer.from((await page.evaluate(t => window.__film.renderFrame(t), t)).split(',')[1], 'base64');

if (STILLS) {
  const dir = path.resolve(ROOT, 'render/out/stills'); fs.mkdirSync(dir, { recursive: true });
  for (const s of STILLS.split(',')) { const t = +s; const f = path.join(dir, `t${t.toFixed(2).replace('.', '_')}.png`); fs.writeFileSync(f, await frameAt(t)); console.log('kare', t, '->', f); }
} else {
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  const end = END == null ? DUR : +END;
  const total = Math.round((end - START) * FPS);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', CRF, '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-r', String(FPS), OUT], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let i = 0; i < total; i++) {
    const t = START + i / FPS;
    const buf = await frameAt(t);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) console.log(`kare ${i}/${total}  (${t.toFixed(1)} sn)  ${((Date.now() - t0) / 1000).toFixed(0)} sn geçti`);
  }
  ff.stdin.end();
  await new Promise((res, rej) => ff.on('close', c => c === 0 ? res() : rej(new Error('ffmpeg çıkış kodu ' + c))));
  console.log('tamam ->', OUT, (fs.statSync(OUT).size / 1048576).toFixed(1), 'MB');
}
await browser.close(); server.close();
