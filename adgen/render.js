// Renders one ad from a JSON spec with headless Chromium: a full-HD photo and an animated reel.
// Usage: node render.js spec.json photo.jpg [reel.mp4 music.wav seconds]
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { chromium } = require('playwright');

const PHOTO_AT_MS = 4500; // every element has animated in by now and the shine sweeps are off the text
const FPS = 30;

async function main() {
  const [specPath, photo, reel, wav, seconds = '8'] = process.argv.slice(2);
  const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.join(__dirname, 'template.html'));
  await page.evaluate((d) => window.render(d), spec);
  await page.evaluate(() => document.fonts.ready);

  await page.evaluate((t) => window.seek(t), PHOTO_AT_MS);
  await page.screenshot({ path: photo, type: 'jpeg', quality: 95 });

  if (reel) {
    const total = Math.round(Number(seconds) * FPS);
    const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-i', wav, '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
      '-vf', `fade=t=out:st=${Number(seconds) - 0.6}:d=0.6`, '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', reel],
      { stdio: ['pipe', 'inherit', 'inherit'] });
    const done = new Promise((res, rej) => ff.on('close', (c) => (c === 0 ? res() : rej(new Error('ffmpeg ' + c)))));
    for (let i = 0; i < total; i++) {
      await page.evaluate((t) => window.seek(t), (i * 1000) / FPS);
      const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    }
    ff.stdin.end();
    await done;
  }
  await browser.close();
}

main().catch((e) => { console.error(e); process.exit(1); });
