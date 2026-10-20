// Prueba P2 de aislamiento: entra como cada dueño de la demo (por la misma
// vía que la página, con la llave pública) e intenta leer y escribir en los
// otros negocios; luego intenta lo mismo sin sesión.
//
//   node pruebas/aislamiento.mjs
//
// Necesita .env.local, cuentas-demo.local.txt y la herramienta de Supabase enlazada.

import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { createClient } from '@supabase/supabase-js';

const raiz = new URL('..', import.meta.url).pathname;
const env = Object.fromEntries(
  readFileSync(`${raiz}.env.local`, 'utf8').split('\n')
    .filter((l) => l.includes('=') && !l.startsWith('#'))
    .map((l) => [l.slice(0, l.indexOf('=')), l.slice(l.indexOf('=') + 1).replace(/^"|"$/g, '')]),
);
const sql = (q) => JSON.parse(execFileSync('npx', ['-y', 'supabase@latest', 'db', 'query', '--linked', q],
  { cwd: raiz, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] })).rows;

// Contraseñas de la demo (solo en esta computadora).
const cuentas = {};
const lineas = readFileSync(`${raiz}cuentas-demo.local.txt`, 'utf8').split('\n');
lineas.forEach((l, i) => {
  const correo = l.match(/correo:\s+(\S+)/)?.[1];
  if (correo) cuentas[correo] = lineas[i + 1].match(/contraseña:\s+(\S+)/)[1];
});

const negocios = sql(`select n.id, n.slug, n.nombre, u.email,
  (select c.id from conversaciones c where c.negocio_id = n.id limit 1) as conversacion
  from negocios n join miembros m on m.negocio_id = n.id join auth.users u on u.id = m.usuario_id
  where n.es_demo order by n.nombre`);

const filas = [];
const marca = (ok) => (ok ? 'sí' : '**NO**');
let todoBien = true;

for (const a of negocios) {
  const s = createClient(env.VITE_SUPABASE_URL, env.VITE_SUPABASE_ANON_KEY, { auth: { persistSession: false } });
  const { error: e } = await s.auth.signInWithPassword({ email: a.email, password: cuentas[a.email] });
  if (e) throw new Error(`No se pudo entrar como ${a.email}: ${e.message}`);

  for (const b of negocios.filter((x) => x.id !== a.id)) {
    const lee = async (tabla) => (await s.from(tabla).select('*', { count: 'exact', head: true }).eq('negocio_id', b.id)).count ?? 0;
    const leidos = { conversaciones: await lee('conversaciones'), preguntas: await lee('preguntas'), mensajes: await lee('mensajes'), avisos: await lee('avisos') };
    const negocioVisto = (await s.from('negocios').select('id').eq('id', b.id)).data?.length ?? 0;
    const insertar = await s.from('preguntas').insert({ negocio_id: b.id, tema: 'otros', pregunta: 'prueba de aislamiento', respuesta: 'x' });
    const cambiar = await s.from('negocios').update({ telefono: '5599999999' }).eq('id', b.id).select('id');
    const responder = await s.rpc('responder', { p_conversacion: b.conversacion, p_texto: 'prueba de aislamiento' });
    const resolver = await s.rpc('resolver', { p_conversacion: b.conversacion });

    const ok = {
      leer: Object.values(leidos).every((n) => n === 0) && negocioVisto === 0,
      agregar: Boolean(insertar.error),
      cambiar: !cambiar.error && cambiar.data.length === 0,
      responder: Boolean(responder.error),
      resolver: Boolean(resolver.error),
    };
    const paso = Object.values(ok).every(Boolean);
    todoBien &&= paso;
    filas.push(`| ${a.nombre} | ${b.nombre} | ${marca(ok.leer)} | ${marca(ok.agregar)} | ${marca(ok.cambiar)} | ${marca(ok.responder && ok.resolver)} | ${paso ? 'Aprobada' : '**FALLA**'} |`);
  }
  await s.auth.signOut();
}

// Sin sesión: nada de tablas; solo funciones del chat.
const anon = createClient(env.VITE_SUPABASE_URL, env.VITE_SUPABASE_ANON_KEY, { auth: { persistSession: false } });
const filasAnon = [];
for (const tabla of ['negocios', 'miembros', 'preguntas', 'conversaciones', 'mensajes', 'avisos']) {
  const r = await anon.from(tabla).select('*').limit(1);
  const ok = Boolean(r.error) || r.data.length === 0;
  todoBien &&= ok;
  filasAnon.push(`| ${tabla} | ${ok ? 'No se pudo leer (bien)' : '**Se leyó información**'} |`);
}
const respAnon = await anon.rpc('responder', { p_conversacion: negocios[0].conversacion, p_texto: 'x' });
todoBien &&= Boolean(respAnon.error);
filasAnon.push(`| responder (función del panel) | ${respAnon.error ? 'Rechazado (bien)' : '**Se aceptó**'} |`);

// Nada de la prueba debió quedar escrito; se confirma en la base.
const quedo = sql(`select (select count(*) from preguntas where pregunta = 'prueba de aislamiento') as preguntas,
  (select count(*) from mensajes where texto in ('prueba de aislamiento', 'x')) as mensajes,
  (select count(*) from negocios where telefono = '5599999999') as telefonos`)[0];
const limpio = Object.values(quedo).every((n) => Number(n) === 0);
todoBien &&= limpio;

const reporte = [
  `# Resultado P2 · Aislamiento entre negocios — ${new Date().toLocaleString('es-MX', { timeZone: 'America/Mexico_City' })}`,
  '',
  `**Resultado general: ${todoBien ? 'APROBADA' : 'FALLA'}** · ${filas.filter((f) => f.includes('Aprobada')).length} de ${filas.length} combinaciones aprobadas`,
  '',
  'Cada dueño entró con su cuenta (llave pública, como la página) e intentó leer y escribir en los otros negocios.',
  '',
  '| Sesión de | Intenta tocar | Leer da 0 | Agregar pregunta rechazado | Cambiar datos: 0 filas | Responder/resolver rechazado | Resultado |',
  '|---|---|---|---|---|---|---|',
  ...filas,
  '',
  '## Sin sesión (cualquier persona con el enlace)',
  '',
  '| Tabla o función | Resultado |',
  '|---|---|',
  ...filasAnon,
  '',
  `Nada quedó escrito en la base por la prueba: ${limpio ? 'sí' : '**NO**'} (preguntas ${quedo.preguntas}, mensajes ${quedo.mensajes}, teléfonos ${quedo.telefonos}).`,
];
console.log(reporte.join('\n'));
mkdirSync(`${raiz}pruebas/resultados`, { recursive: true });
writeFileSync(`${raiz}pruebas/resultados/${new Date().toISOString().slice(0, 10)}_P2_aislamiento.md`, `${reporte.join('\n')}\n`);
process.exit(todoBien ? 0 : 1);
