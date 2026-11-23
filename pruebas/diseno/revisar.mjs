// Revisión de diseño automática: desborde horizontal, texto fuera de su caja o de la pantalla,
// textos encimados y errores de consola, en varios anchos. Guarda capturas por sección.
//   node pruebas/diseno/revisar.mjs http://127.0.0.1:8000 /ruta/capturas / "#prueba,#avisa"
import { createRequire } from 'node:module';
const require = createRequire('/Users/arleth/.npm/_npx/d537ee5ee2a13f03/node_modules/');
const { chromium } = require('playwright');
const [,, base, salida, ruta = '/', secciones = ''] = process.argv;
const anchos = [360, 390, 768, 1024, 1180, 1440, 1920];
const browser = await chromium.launch({ executablePath: process.env.HOME + '/Library/Caches/ms-playwright/chromium_headless_shell-1194/chrome-mac/headless_shell' });

const revisar = () => {
  const W = innerWidth, out = [];
  const desc = (el) => `${el.tagName.toLowerCase()}${el.id ? '#' + el.id : ''}${typeof el.className === 'string' && el.className ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : ''} «${(el.textContent || '').trim().slice(0, 40)}»`;
  const visible = (el) => { const s = getComputedStyle(el); return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && el.getClientRects().length; };
  const recorte = (el) => { let p = el.parentElement, r = Infinity; while (p && p !== document.documentElement) { const s = getComputedStyle(p); if (/(hidden|clip|auto|scroll)/.test(s.overflowX)) r = Math.min(r, p.getBoundingClientRect().right); p = p.parentElement; } return r; };
  if (document.documentElement.scrollWidth > W + 1) out.push(['scroll-horizontal', `${document.documentElement.scrollWidth}px en ${W}`]);
  const textos = [];
  for (const el of document.querySelectorAll('body *')) {
    if (!visible(el) || el.closest('svg')) continue;
    const r = el.getBoundingClientRect();
    if (!r.width) continue;
    const conTexto = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    if (r.right > W + 1 && recorte(el) > W + 1) out.push(['sale-de-pantalla', desc(el), Math.round(r.right)]);
    const s = getComputedStyle(el);
    if (conTexto && s.overflowX === 'visible' && el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 2 && s.textOverflow !== 'ellipsis') out.push(['texto-fuera-de-su-caja', desc(el)]);
    if (conTexto) for (const n of el.childNodes) {
      if (n.nodeType !== 3 || !n.textContent.trim()) continue;
      const rg = document.createRange(); rg.selectNodeContents(n);
      for (const q of rg.getClientRects()) if (q.width > 2 && q.height > 2) textos.push([el, q]);
    }
  }
  const vistos = new Set();
  for (let i = 0; i < textos.length; i++) for (let j = i + 1; j < textos.length; j++) {
    const [a, ra] = textos[i], [b, rb] = textos[j];
    if (a === b || a.contains(b) || b.contains(a)) continue;
    const ix = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left), iy = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
    if (ix > 4 && iy > 4) { const k = desc(a) + '|' + desc(b); if (!vistos.has(k)) { vistos.add(k); out.push(['texto-encimado', desc(a), desc(b)]); } }
  }
  return out;
};

for (const ancho of anchos) {
  const ctx = await browser.newContext({ viewport: { width: ancho, height: ancho < 500 ? 800 : 900 }, reducedMotion: 'reduce' });
  const p = await ctx.newPage();
  const errores = [];
  p.on('pageerror', (e) => errores.push(String(e)));
  p.on('console', (m) => { if (m.type() === 'error') errores.push(m.text()); });
  await p.goto(base + ruta, { waitUntil: 'networkidle' });
  await p.waitForTimeout(1200);
  const r = await p.evaluate(revisar);
  for (const x of r.slice(0, 10)) console.log(`@${ancho}`, x.join(' · '));
  for (const e of [...new Set(errores)]) console.log(`@${ancho} consola ·`, e.slice(0, 160));
  await p.screenshot({ path: `${salida}/arriba_${ancho}.png` });
  for (const s of secciones.split(',').filter(Boolean)) {
    await p.evaluate((sel) => document.querySelector(sel)?.scrollIntoView({ block: 'start' }), s);
    await p.waitForTimeout(250);
    await p.screenshot({ path: `${salida}/${s.replace(/\W/g, '')}_${ancho}.png` });
  }
  await ctx.close();
}
await browser.close();
console.log('Revisión terminada.');
