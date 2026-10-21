import { supabase } from './supabase.js';
import { textos } from './textos.js';

const t = textos.inicio;
const sinMovimiento = matchMedia('(prefers-reduced-motion: reduce)').matches;

// Entradas: cada parte de una sección aparece un poco después de la anterior.
const observador = new IntersectionObserver((entradas) => {
  for (const e of entradas) {
    if (!e.isIntersecting) continue;
    e.target.classList.add('visible');
    observador.unobserve(e.target);
  }
}, { rootMargin: '0px 0px -8% 0px' });
document.querySelectorAll('main > section').forEach(($s) => {
  $s.querySelectorAll('.revelar').forEach(($r, i) => {
    $r.style.setProperty('--retraso', `${Math.min(i, 6) * 80}ms`);
    observador.observe($r);
  });
});

// Portada: el escenario se abre y los mensajes de las 11:42 p. m. llegan uno por uno.
const $escenario = document.getElementById('escenario');
const $pasos = [...document.querySelectorAll('.portada [data-paso]')]
  .sort((a, b) => a.dataset.paso - b.dataset.paso);
const $escribiendo = document.querySelector('.portada .wa-escribiendo');
const espera = (ms) => new Promise((r) => setTimeout(r, ms));

async function animarPortada() {
  requestAnimationFrame(() => $escenario.classList.add('abierto'));
  if (sinMovimiento) return $pasos.forEach(($p) => $p.classList.add('visto'));
  await espera(1100);
  for (const $p of $pasos) {
    const esNegocio = $p.classList.contains('wa-negocio');
    if (esNegocio) {
      $p.before($escribiendo);
      $escribiendo.classList.add('activo');
      await espera(900);
      $escribiendo.classList.remove('activo');
    }
    $p.classList.add('visto');
    await espera(esNegocio ? 700 : 500);
  }
}
animarPortada();

// Demo viva: el chat real de los 3 negocios de ejemplo --------------------
const $demoMensajes = document.getElementById('demo-mensajes');
const $demoEntrada = document.getElementById('demo-entrada');
const $demoEstado = document.getElementById('demo-estado');
const $demoAbrir = document.getElementById('demo-abrir');
const demo = { slug: 'salon-bella', hora: '', token: null, version: 0 };

function horaSimulada() {
  if (!demo.hora) return undefined;
  const hoy = new Date().toLocaleDateString('en-CA', { timeZone: 'America/Mexico_City' });
  return `${hoy}T${demo.hora}:00-06:00`;
}

function horaVisible(fecha) {
  if (demo.hora) {
    const [h, m] = demo.hora.split(':').map(Number);
    return `${h % 12 || 12}:${String(m).padStart(2, '0')} ${h < 12 ? 'a. m.' : 'p. m.'}`;
  }
  return new Date(fecha ?? Date.now()).toLocaleTimeString('es-MX', { hour: 'numeric', minute: '2-digit' });
}

function quitarOpciones() {
  $demoMensajes.querySelectorAll('.wa-opciones').forEach(($o) => $o.remove());
  // La lista que mostraban los botones vuelve a escribirse en su burbuja.
  $demoMensajes.querySelectorAll('[data-completo]').forEach(($v) => {
    $v.firstChild.nodeValue = $v.dataset.completo;
    delete $v.dataset.completo;
  });
}

function burbujaDemo({ autor, texto, creado_en, opciones }) {
  quitarOpciones();
  const $b = document.createElement('p');
  $b.className = `wa-burbuja ${autor === 'cliente' ? 'wa-cliente' : 'wa-negocio'}`;
  // Con botones a la vista, la lista numerada sobra.
  $b.textContent = opciones?.length
    ? texto.split('\n').filter((l) => !/^\d{1,2}\. /.test(l) && l !== 'Escríbeme el número o tu pregunta.').join('\n').trim()
    : texto;
  if ($b.textContent !== texto) $b.dataset.completo = texto;
  const $h = document.createElement('span');
  $h.textContent = horaVisible(creado_en);
  $b.append($h);
  $demoMensajes.append($b);
  if (opciones?.length) {
    const $fila = document.createElement('div');
    $fila.className = 'wa-opciones';
    for (const { pregunta, enviar = pregunta } of opciones) {
      const $o = document.createElement('button');
      $o.type = 'button';
      $o.className = 'wa-opcion';
      $o.textContent = pregunta;
      $o.addEventListener('click', () => enviarDemo(enviar));
      $fila.append($o);
    }
    $demoMensajes.append($fila);
  }
  $demoMensajes.scrollTop = $demoMensajes.scrollHeight;
  return $b;
}

function iniciales(nombre) {
  return nombre.split(/\s+/).filter((p) => p.length > 2).slice(0, 2).map((p) => p[0].toUpperCase()).join('');
}

async function cargarDemo() {
  const version = ++demo.version;
  demo.token = null;
  $demoMensajes.replaceChildren();
  $demoAbrir.href = `/chat/${demo.slug}${demo.hora ? `?hora=${demo.hora}` : ''}`;
  const { data, error } = await supabase.rpc('chat_negocio', { p_slug: demo.slug, p_hora: horaSimulada() });
  if (version !== demo.version) return;
  if (error || !data) {
    $demoEstado.textContent = t.demo.sinConexion;
    return;
  }
  document.getElementById('demo-nombre').textContent = data.nombre;
  document.getElementById('demo-avatar').textContent = iniciales(data.nombre);
  $demoEstado.textContent = data.estado;
  burbujaDemo({
    autor: 'asistente',
    texto: data.bienvenida,
    opciones: [
      ...(data.sugerencias ?? []).map((pregunta) => ({ pregunta })),
      { pregunta: textos.chat.hablarConPersona, enviar: 'persona' },
    ],
  });
}

async function enviarDemo(texto) {
  texto = texto.trim();
  if (!texto) return;
  const version = demo.version;
  const $mio = burbujaDemo({ autor: 'cliente', texto });
  $mio.style.opacity = '0.6';
  $demoEstado.textContent = textos.chat.escribiendo;
  try {
    if (!demo.token) {
      const { data, error } = await supabase.rpc('chat_iniciar', { p_slug: demo.slug });
      if (error) throw error;
      demo.token = data;
    }
    const { data, error } = await supabase.rpc('chat_enviar', { p_token: demo.token, p_texto: texto, p_hora: horaSimulada() });
    if (error) throw error;
    if (version !== demo.version) return;
    $mio.style.opacity = '';
    const respuesta = data.find((m) => m.autor === 'asistente');
    if (respuesta) burbujaDemo(respuesta);
  } catch {
    if (version !== demo.version) return;
    $mio.style.opacity = '';
    burbujaDemo({ autor: 'asistente', texto: t.demo.noSeEnvio });
  }
  const { data } = await supabase.rpc('chat_negocio', { p_slug: demo.slug, p_hora: horaSimulada() });
  if (data && version === demo.version) $demoEstado.textContent = data.estado;
}

document.getElementById('demo-formulario').addEventListener('submit', (e) => {
  e.preventDefault();
  const texto = $demoEntrada.value;
  $demoEntrada.value = '';
  enviarDemo(texto);
});
document.querySelectorAll('input[name="negocio"]').forEach(($r) => $r.addEventListener('change', () => {
  demo.slug = $r.value;
  cargarDemo();
}));
document.querySelectorAll('input[name="hora"]').forEach(($r) => $r.addEventListener('change', () => {
  demo.hora = $r.value;
  cargarDemo();
}));
document.querySelectorAll('.pista').forEach(($p) => $p.addEventListener('click', () => enviarDemo($p.dataset.texto)));

// La demo se carga cuando el visitante se acerca, no al abrir la página.
new IntersectionObserver((entradas, obs) => {
  if (!entradas.some((e) => e.isIntersecting)) return;
  obs.disconnect();
  cargarDemo();
}, { rootMargin: '400px 0px' }).observe(document.getElementById('prueba'));

// Panel con notas: al pasar por una nota, se resalta su parte del panel.
const $panel = document.querySelector('.panel');
document.querySelectorAll('.nota').forEach(($n) => {
  $n.tabIndex = 0;
  const encender = () => {
    $panel.classList.add('enfocado');
    $panel.querySelectorAll('[data-parte]').forEach(($p) => $p.classList.toggle('foco', $p.dataset.parte === $n.dataset.apunta));
  };
  const apagar = () => $panel.classList.remove('enfocado');
  $n.addEventListener('mouseenter', encender);
  $n.addEventListener('focus', encender);
  $n.addEventListener('mouseleave', apagar);
  $n.addEventListener('blur', apagar);
});

// Copiar el enlace de ejemplo.
const $copiar = document.getElementById('copiar-enlace');
$copiar.addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(`${location.origin}/chat/salon-bella`);
    $copiar.textContent = t.copiado;
    setTimeout(() => { $copiar.textContent = t.copiar; }, 1800);
  } catch { /* sin permiso para copiar: el enlace sigue a la vista */ }
});

// Para quién: la foto cambia con el giro que se está leyendo.
const $fotos = document.querySelectorAll('.para-foto img');
function mostrarFoto(nombre) {
  $fotos.forEach(($f) => $f.classList.toggle('activa', $f.dataset.foto === nombre));
}
document.querySelectorAll('.grupo').forEach(($g) => {
  $g.addEventListener('mouseenter', () => mostrarFoto($g.dataset.foto));
});
const observaGrupos = new IntersectionObserver((entradas) => {
  for (const e of entradas) if (e.isIntersecting) mostrarFoto(e.target.dataset.foto);
}, { rootMargin: '-45% 0px -45% 0px' });
document.querySelectorAll('.grupo').forEach(($g) => observaGrupos.observe($g));

// Preguntas: una respuesta grande a la derecha (en celular, abajo de la pregunta).
const $grande = document.getElementById('respuesta-grande');
const $botones = [...document.querySelectorAll('#lista-preguntas button')];
function elegir($b) {
  if ($b.getAttribute('aria-expanded') === 'true') return;
  for (const $o of $botones) {
    const si = $o === $b;
    $o.setAttribute('aria-expanded', String(si));
    document.getElementById($o.getAttribute('aria-controls')).hidden = !si;
  }
  const texto = document.getElementById($b.getAttribute('aria-controls')).textContent;
  $grande.classList.add('cambiando');
  setTimeout(() => {
    $grande.textContent = texto;
    $grande.classList.remove('cambiando');
  }, sinMovimiento ? 0 : 150);
}
$botones.forEach(($b) => {
  $b.addEventListener('click', () => elegir($b));
  $b.addEventListener('focus', () => elegir($b));
  $b.addEventListener('mouseenter', () => { if (matchMedia('(hover: hover)').matches) elegir($b); });
});
