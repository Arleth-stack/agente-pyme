// Prueba P5: ningún texto que ve el dueño o el cliente usa palabras técnicas.
// Revisa los textos de pantalla (src/textos.js), los textos fijos del HTML y
// las respuestas que arma el chat dentro de la base (frases en las funciones SQL).
//
//   node pruebas/lenguaje.mjs

import { readFileSync, readdirSync, writeFileSync, mkdirSync } from 'node:fs';

const raiz = new URL('..', import.meta.url).pathname;
const prohibidas = [
  /\bIA\b/, /inteligencia artificial/i, /automatiz/i, /autom[aá]tic/i, /\bmodelos?\b/i, /\bentren/i,
  /\bbots?\b/i, /\bprompts?\b/i, /\btokens?\b/i, /\bAPI\b/, /\bservidor/i, /\berror \d{3}/i,
];

const hallazgos = [];
const revisar = (origen, texto) => {
  for (const p of prohibidas) if (p.test(texto)) hallazgos.push(`${origen}: «${texto.trim().slice(0, 100)}» (${p})`);
};

// 1. Textos de pantalla: todas las cadenas de textos.js (sin comentarios).
const textosJs = readFileSync(`${raiz}src/textos.js`, 'utf8').replace(/\/\/.*$/gm, '');
const cadenas = [...textosJs.matchAll(/'((?:[^'\\]|\\.)*)'|`((?:[^`\\]|\\.)*)`/g)].map((m) => m[1] ?? m[2]);
cadenas.forEach((c) => revisar('textos.js', c));

// 2. Texto fijo de las páginas (lo que queda fuera de las etiquetas y los atributos visibles).
const paginas = readdirSync(raiz).filter((f) => f.endsWith('.html'));
for (const pagina of paginas) {
  const html = readFileSync(`${raiz}${pagina}`, 'utf8')
    .replace(/<script[\s\S]*?<\/script>/g, '').replace(/<style[\s\S]*?<\/style>/g, '').replace(/<!--[\s\S]*?-->/g, '');
  const visibles = [
    ...html.replace(/<[^>]+>/g, '\n').split('\n'),
    ...[...html.matchAll(/(?:title|placeholder|aria-label|alt|content)="([^"]*)"/g)].map((m) => m[1]),
  ].filter((s) => s.trim());
  visibles.forEach((s) => revisar(pagina, s));
}

// 3. Frases que el chat le contesta al cliente (literales SQL con espacios, sin comentarios).
// Los datos de los negocios demo (sus preguntas y respuestas) los escribe el dueño:
// la regla de lenguaje aplica a los textos del sistema, no a lo que escribe cada negocio.
const datosDeNegocios = ['20261019000003_negocios_demo.sql'];
const migraciones = readdirSync(`${raiz}supabase/migrations`).filter((f) => f.endsWith('.sql') && !datosDeNegocios.includes(f));
let frasesSql = 0;
for (const archivo of migraciones) {
  const sql = readFileSync(`${raiz}supabase/migrations/${archivo}`, 'utf8').replace(/--.*$/gm, '');
  for (const m of sql.matchAll(/'((?:[^']|'')*)'/g)) {
    const frase = m[1];
    // Solo frases en español para personas (no nombres de columnas, catálogos ni expresiones).
    if (!/\s/.test(frase) || !/[a-záéíóúñ]{3,}\s[a-záéíóúñ]{2,}/i.test(frase) || /[\\^$|]/.test(frase)) continue;
    frasesSql++;
    revisar(archivo, frase);
  }
}

const reporte = [
  `# Resultado P5 · Lenguaje — ${new Date().toLocaleString('es-MX', { timeZone: 'America/Mexico_City' })}`,
  '',
  `Revisado: ${cadenas.length} textos de pantalla, ${paginas.length} páginas y ${frasesSql} frases del chat en la base.`,
  '',
  `**Palabras prohibidas encontradas: ${hallazgos.length}** (meta 0)`,
  ...hallazgos.map((h) => `- ${h}`),
];
console.log(reporte.join('\n'));
mkdirSync(`${raiz}pruebas/resultados`, { recursive: true });
writeFileSync(`${raiz}pruebas/resultados/${new Date().toISOString().slice(0, 10)}_P5_lenguaje.md`, `${reporte.join('\n')}\n`);
process.exit(hallazgos.length ? 1 : 0);
