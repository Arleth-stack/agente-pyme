// Prueba las interacciones de la página de inicio en un navegador real (sin pantalla).
import { createRequire } from 'node:module';
const require = createRequire('/Users/arleth/.npm/_npx/d537ee5ee2a13f03/node_modules/');
const { chromium } = require('playwright');
const base = process.argv[2] || 'http://127.0.0.1:8000';
const browser = await chromium.launch({ executablePath: process.env.HOME + '/Library/Caches/ms-playwright/chromium_headless_shell-1194/chrome-mac/headless_shell' });
const ok = (nombre, valor) => console.log(`${valor ? '✓' : '✗'} ${nombre}`);

// Celular: el menú se abre, y al elegir una sección se cierra y baja hasta ella.
let p = await (await browser.newContext({ viewport: { width: 390, height: 800 } })).newPage();
await p.goto(base + '/', { waitUntil: 'networkidle' });
await p.click('.barra-menu');
await p.waitForTimeout(500);
ok('Celular: «Menú» abre el menú lateral', await p.evaluate(() => document.getElementById('lateral').classList.contains('show')));
await p.click('#menu-secciones a[href="#preguntas"]');
await p.waitForTimeout(1200);
ok('Celular: elegir «Preguntas» cierra el menú', await p.evaluate(() => !document.getElementById('lateral').classList.contains('show')));
ok('Celular: y baja hasta la sección', await p.evaluate(() => Math.abs(document.getElementById('preguntas').getBoundingClientRect().top) < 140));
await p.click('.barra-menu'); await p.waitForTimeout(400); await p.keyboard.press('Escape'); await p.waitForTimeout(500);
ok('Celular: Esc cierra el menú', await p.evaluate(() => !document.getElementById('lateral').classList.contains('show')));
ok('Celular: el QR no se muestra (ya estás en el celular)', await p.evaluate(() => getComputedStyle(document.querySelector('.demo-celular')).display === 'none'));

// Computadora: chat de ejemplo, hora simulada, negocio, QR, preguntas y copiar.
p = await (await browser.newContext({ viewport: { width: 1440, height: 900 } })).newPage();
await p.goto(base + '/', { waitUntil: 'networkidle' });
await p.evaluate(() => document.getElementById('prueba').scrollIntoView());
await p.waitForTimeout(1500);
ok('Chat de ejemplo: carga la bienvenida', (await p.textContent('#demo-mensajes')).includes('Gracias por escribir'));
await p.click('label[for="hora-2342"]'); await p.waitForTimeout(1500);
ok('Hora 11:42 p. m.: el negocio aparece cerrado', (await p.textContent('#demo-estado')).startsWith('Cerrado'));
await p.click('label:has(input[value="taller-rapido"])'); await p.waitForTimeout(1500);
ok('Cambiar a Taller Rápido: cambia el nombre', (await p.textContent('#demo-nombre')) === 'Taller Rápido');
ok('Cambiar a Taller Rápido: cambia el QR', await p.evaluate(() => !document.querySelector('[data-qr="taller-rapido"]').hidden && document.querySelector('[data-qr="salon-bella"]').hidden));
ok('«Abrir el chat completo» apunta a Taller Rápido con la hora', (await p.getAttribute('#demo-abrir', 'href')) === '/chat/taller-rapido/?hora=23:42');
await p.click('.pista[data-texto="me pueden comunicar con alguien"]'); await p.waitForTimeout(2500);
ok('Pista «me pueden comunicar con alguien»: avisa al equipo', (await p.textContent('#demo-mensajes')).includes('ya le avisé a alguien del equipo'));
await p.hover('#lista-preguntas li:nth-child(7) button'); await p.waitForTimeout(400);
ok('Preguntas: «¿Cuánto cuesta?» muestra su respuesta grande', (await p.textContent('#respuesta-grande')).startsWith('Los primeros 7 días son gratis'));
await p.click('#dialogo-crear button[type="submit"]'); await p.waitForTimeout(800);
ok('«Empieza con tu nombre» lleva a Crear con nombre y giro', p.url().includes('/crear/?nombre=Est') && p.url().includes('giro=salon'));
await browser.close();
