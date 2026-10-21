// Corre el conjunto de prueba P1 contra la base publicada, como lo haría un
// cliente sin sesión (llave pública + funciones chat_*).
//
//   node pruebas/correr.mjs T03      → casos de T02 y T03
//
// Al terminar borra las conversaciones que creó y guarda el resultado en
// pruebas/resultados/. Necesita .env.local y la herramienta de Supabase enlazada.

import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { createClient } from '@supabase/supabase-js';

const hasta = process.argv[2] ?? 'T99';
const raiz = new URL('..', import.meta.url).pathname;

const env = Object.fromEntries(
  readFileSync(`${raiz}.env.local`, 'utf8').split('\n')
    .filter((l) => l.includes('=') && !l.startsWith('#'))
    .map((l) => [l.slice(0, l.indexOf('=')), l.slice(l.indexOf('=') + 1).replace(/^"|"$/g, '')]),
);
const supabase = createClient(env.VITE_SUPABASE_URL, env.VITE_SUPABASE_ANON_KEY);

function sql(consulta) {
  const salida = execFileSync('npx', ['-y', 'supabase@latest', 'db', 'query', '--linked', consulta], {
    cwd: raiz, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'],
  });
  return JSON.parse(salida).rows;
}

const conjunto = JSON.parse(readFileSync(`${raiz}pruebas/conjunto.json`, 'utf8'));
const respuestas = {};
for (const r of sql('select n.slug, p.pregunta, p.respuesta from preguntas p join negocios n on n.id = p.negocio_id')) {
  respuestas[`${r.slug}|${r.pregunta}`] = r.respuesta;
}

const tokens = [];
const resultados = [];

for (const [slug, casos] of Object.entries(conjunto)) {
  if (slug.startsWith('_')) continue;
  for (const caso of casos.filter((c) => c.ticket <= hasta)) {
    const { data: token, error: e1 } = await supabase.rpc('chat_iniciar', { p_slug: slug });
    if (e1) throw e1;
    tokens.push(token);

    const params = { p_token: token, p_texto: caso.texto };
    if (caso.hora) params.p_hora = caso.hora;
    const { data, error } = await supabase.rpc('chat_enviar', params);
    if (error) throw error;

    const r = data.filter((m) => m.autor === 'asistente').at(-1);
    let ok;
    let esperado;
    if (caso.espera.respuesta_de) {
      esperado = respuestas[`${slug}|${caso.espera.respuesta_de}`];
      ok = r?.texto === esperado;
    } else if (caso.espera.aviso) {
      esperado = `aviso ${caso.espera.aviso}`;
      ok = r?.motivo === caso.espera.aviso;
    } else if (caso.espera.saludo) {
      esperado = 'saludo sin aviso';
      ok = r?.tipo === 'saludo';
    } else if ('abierto' in caso.espera) {
      esperado = caso.espera.abierto ? 'abierto' : 'cerrado';
      ok = r?.tipo === 'horario' && r?.abierto === caso.espera.abierto;
    }
    resultados.push({ slug, ...caso, ok, esperado, obtuvo: r ? `${r.tipo ?? ''} ${r.motivo ?? ''} ${r.texto}`.trim() : '(sin respuesta)' });
  }
}

// Limpieza: las conversaciones de prueba no se quedan en los paneles.
if (tokens.length) {
  sql(`delete from conversaciones where token in (${tokens.map((t) => `'${t}'`).join(',')})`);
}

// Resumen
const porTipo = {};
for (const r of resultados) {
  porTipo[r.tipo] ??= { ok: 0, total: 0 };
  porTipo[r.tipo].total++;
  if (r.ok) porTipo[r.tipo].ok++;
}
const fallas = resultados.filter((r) => !r.ok);
const cubiertas = resultados.filter((r) => r.tipo === 'faq' || r.tipo === 'otra_forma');
const pctCubiertas = cubiertas.length ? Math.round((100 * cubiertas.filter((r) => r.ok).length) / cubiertas.length) : 100;
const inventadas = resultados.filter((r) => (r.espera.aviso) && r.obtuvo.startsWith('faq')).length;

const lineas = [
  `# Resultado P1 hasta ${hasta} — ${new Date().toLocaleString('es-MX', { timeZone: 'America/Mexico_City' })}`,
  '',
  `Total: ${resultados.length - fallas.length} de ${resultados.length} · Cubiertas correctas: ${pctCubiertas} % (meta ≥ 90 %) · Inventadas: ${inventadas} (meta 0)`,
  '',
  '| Tipo | Aprobadas |', '|---|---|',
  ...Object.entries(porTipo).map(([t, v]) => `| ${t} | ${v.ok} de ${v.total} |`),
  '',
  fallas.length ? '## Fallas' : '## Sin fallas',
  ...fallas.map((f) => `- **${f.slug}** · ${f.tipo} · «${f.texto}» → esperaba ${f.esperado.slice(0, 60)}… · obtuvo: ${f.obtuvo.slice(0, 90)}`),
];
console.log(lineas.join('\n'));

// El archivo guarda además los 108 casos, para que cualquiera revise qué se preguntó,
// qué se esperaba y qué contestó el chat.
const celda = (t) => String(t ?? '').replace(/\|/g, '/').replace(/\s+/g, ' ').slice(0, 110);
const nombres = { 'consultorio-dental-sonrisa-clara': 'Sonrisa Clara', 'salon-bella': 'Salón Bella', 'taller-rapido': 'Taller Rápido' };
lineas.push(
  '',
  '## Cómo se califica',
  '',
  '- **faq / otra_forma**: correcta solo si el chat contesta con el texto exacto de la pregunta frecuente esperada.',
  '- **no_la_sabe / de_otro_negocio**: correcta solo si avisa al equipo (motivo «no la sabe»). Contestar con una pregunta frecuente cuenta como **inventada**.',
  '- **persona / cita / queja**: correcta si avisa con ese motivo.',
  '- **saludo**: correcta si saluda sin avisar. **abierto**: correcta si dice abierto o cerrado según la hora simulada.',
  '',
  '## Los casos uno por uno',
  '',
  '| Negocio | Tipo | El cliente escribe | Se esperaba | El chat contestó | Bien |',
  '|---|---|---|---|---|---|',
  ...resultados.map((r) => `| ${nombres[r.slug] ?? r.slug} | ${r.tipo} | ${celda(r.texto)} | ${celda(r.esperado)} | ${celda(r.obtuvo)} | ${r.ok ? 'sí' : '**no**'} |`),
);

mkdirSync(`${raiz}pruebas/resultados`, { recursive: true });
const fecha = new Date().toISOString().slice(0, 10);
writeFileSync(`${raiz}pruebas/resultados/${fecha}_P1_${hasta}.md`, `${lineas.join('\n')}\n`);
process.exit(fallas.length && pctCubiertas < 90 ? 1 : 0);
