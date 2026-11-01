// Rend une page HTML animée image par image et l'encode en MP4 (via ffmpeg).
// usage: node render.js page.html sortie.mp4 fps duree_s
const { chromium } = require('playwright');
const { spawn } = require('child_process');
(async () => {
  const [html, out, fpsS, totalS] = process.argv.slice(2);
  const fps = Number(fpsS), total = Number(totalS);
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + html);
  await page.waitForFunction('window.ready === true');
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-vcodec', 'mjpeg',
    '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((res, rej) => { ff.on('close', c => c === 0 ? res() : rej(new Error('ffmpeg ' + c))); });
  const n = Math.round(total * fps);
  for (let i = 0; i < n; i++) {
    await page.evaluate(t => window.setTime(t), i / fps);
    const buf = await page.screenshot({ type: 'jpeg', quality: 90 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await done;
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
