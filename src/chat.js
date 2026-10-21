import { supabase } from './supabase.js';
import { textos } from './textos.js';

const t = textos.chat;
const $mensajes = document.getElementById('mensajes');
const $formulario = document.getElementById('formulario');
const $entrada = document.getElementById('entrada');
const $botonEnviar = document.getElementById('boton-enviar');

// /chat/salon-bella → "salon-bella" (también acepta /chat.html?n=salon-bella).
const slug =
  location.pathname.match(/^\/chat\/([a-z0-9-]+)\/?$/)?.[1] ??
  new URLSearchParams(location.search).get('n');

// Hora simulada para la demo (?hora=23:00). La base solo la acepta en los
// negocios demo; los 3 de la demo están en la zona de Ciudad de México.
const horaSimulada = (() => {
  const h = new URLSearchParams(location.search).get('hora');
  if (!/^\d{2}:\d{2}$/.test(h ?? '')) return undefined;
  const hoy = new Date().toLocaleDateString('en-CA', { timeZone: 'America/Mexico_City' });
  return `${hoy}T${h}:00-06:00`;
})();

const claveToken = `conversacion:${slug}`;
let token = leerToken();
let ultimoId = 0;

function leerToken() {
  try { return localStorage.getItem(claveToken); } catch { return null; }
}
function guardarToken(valor) {
  try { localStorage.setItem(claveToken, valor); } catch { /* sin almacenamiento: dura lo que dure la pestaña */ }
}

function horaDe(fecha) {
  return new Date(fecha).toLocaleTimeString('es-MX', { hour: 'numeric', minute: '2-digit' });
}

function iniciales(nombre) {
  return nombre.split(/\s+/).filter((p) => p.length > 2 || /^[A-ZÁÉÍÓÚÑ]/.test(p)).slice(0, 2)
    .map((p) => p[0].toUpperCase()).join('');
}

// Botones con preguntas para tocar: solo los de la última respuesta.
function mostrarOpciones(opciones) {
  const $fila = document.createElement('div');
  $fila.className = 'chat-opciones';
  for (const { pregunta, enviar: texto = pregunta } of opciones) {
    const $o = document.createElement('button');
    $o.type = 'button';
    $o.className = 'chat-opcion';
    $o.textContent = pregunta;
    $o.addEventListener('click', () => {
      if ($entrada.disabled) return;
      enviar(texto, burbuja({ autor: 'cliente', texto }));
    });
    $fila.append($o);
  }
  $mensajes.append($fila);
  $mensajes.scrollTop = $mensajes.scrollHeight;
}

function burbuja({ autor, texto, creado_en, opciones }) {
  // Al quitar los botones de la respuesta anterior, su lista vuelve a escribirse en la burbuja.
  $mensajes.querySelectorAll('.chat-opciones').forEach(($f) => $f.remove());
  $mensajes.querySelectorAll('[data-completo]').forEach(($v) => {
    $v.querySelector('p').textContent = $v.dataset.completo;
    delete $v.dataset.completo;
  });
  const $b = document.createElement('div');
  $b.className = `burbuja ${autor === 'cliente' ? 'burbuja-cliente' : 'burbuja-negocio'}`;
  const $texto = document.createElement('p');
  // Con botones a la vista, la lista numerada sobra (sirve en WhatsApp, donde no hay botones).
  $texto.textContent = opciones?.length && autor !== 'cliente'
    ? texto.split('\n').filter((l) => !/^\d{1,2}\. /.test(l) && l !== 'Escríbeme el número o tu pregunta.').join('\n').trim()
    : texto;
  if ($texto.textContent !== texto) $b.dataset.completo = texto;
  const $hora = document.createElement('span');
  $hora.className = 'burbuja-hora';
  $hora.textContent = horaDe(creado_en ?? Date.now());
  $b.append($texto, $hora);
  $mensajes.append($b);
  $mensajes.scrollTop = $mensajes.scrollHeight;
  if (autor !== 'cliente' && opciones?.length) mostrarOpciones(opciones);
  return $b;
}

function mostrarMensajes(lista) {
  for (const m of lista) {
    if (m.id <= ultimoId) continue;
    burbuja(m);
    ultimoId = m.id;
  }
}

function mostrarAviso(texto) {
  $mensajes.replaceChildren();
  const $p = document.createElement('p');
  $p.className = 'chat-aviso';
  $p.textContent = texto;
  $mensajes.append($p);
}

const $estado = document.getElementById('estado-negocio');
let estadoNegocio = '';

function escribiendo(si) {
  $estado.textContent = si ? t.escribiendo : estadoNegocio;
}

async function actualizarEstado() {
  const { data, error } = await supabase.rpc('chat_negocio', { p_slug: slug, p_hora: horaSimulada });
  if (error) throw error;
  if (data) {
    estadoNegocio = data.estado;
    if ($estado.textContent !== t.escribiendo) $estado.textContent = estadoNegocio;
  }
  return data;
}

async function enviar(texto, $pendiente) {
  $pendiente.classList.remove('burbuja-fallida');
  $pendiente.classList.add('burbuja-enviando');
  $pendiente.onclick = null;
  try {
    if (!token) {
      const { data, error } = await supabase.rpc('chat_iniciar', { p_slug: slug });
      if (error) throw error;
      token = data;
      guardarToken(token);
    }
    escribiendo(true);
    let { data, error } = await supabase.rpc('chat_enviar', { p_token: token, p_texto: texto, p_hora: horaSimulada });
    if (error?.message === 'conversacion_no_existe') {
      // La conversación guardada ya no existe (por ejemplo, se reinició la demo): se abre otra.
      const nueva = await supabase.rpc('chat_iniciar', { p_slug: slug });
      if (nueva.error) throw nueva.error;
      token = nueva.data;
      guardarToken(token);
      ultimoId = 0;
      ({ data, error } = await supabase.rpc('chat_enviar', { p_token: token, p_texto: texto, p_hora: horaSimulada }));
    }
    escribiendo(false);
    if (error) throw error;
    // La burbuja temporal se cambia por lo que la base confirmó que guardó.
    $pendiente.remove();
    mostrarMensajes(data);
  } catch {
    escribiendo(false);
    $pendiente.classList.remove('burbuja-enviando');
    $pendiente.classList.add('burbuja-fallida');
    const $nota = document.createElement('span');
    $nota.className = 'burbuja-nota';
    $nota.textContent = t.noSeEnvio;
    $pendiente.querySelector('.burbuja-nota')?.remove();
    $pendiente.append($nota);
    $pendiente.onclick = () => enviar(texto, $pendiente);
  }
}

$formulario.addEventListener('submit', (e) => {
  e.preventDefault();
  const texto = $entrada.value.trim();
  if (!texto) return;
  $entrada.value = '';
  enviar(texto, burbuja({ autor: 'cliente', texto }));
});

async function revisarNuevos() {
  if (!token) return;
  const { data, error } = await supabase.rpc('chat_mensajes', { p_token: token, p_despues_de: ultimoId });
  if (!error) mostrarMensajes(data);
}

async function arrancar() {
  if (!slug) return mostrarAviso(t.noEncontrado);

  let negocio;
  try {
    negocio = await actualizarEstado();
  } catch {
    return mostrarAviso(t.sinConexion);
  }
  if (!negocio) return mostrarAviso(t.noEncontrado);

  document.title = negocio.nombre;
  document.getElementById('nombre-negocio').textContent = negocio.nombre;
  document.getElementById('avatar').textContent = iniciales(negocio.nombre);

  // La bienvenida la arma la base según el giro y las preguntas del negocio.
  burbuja({
    autor: 'asistente',
    texto: negocio.bienvenida ?? t.bienvenida(negocio.nombre),
    creado_en: Date.now(),
    opciones: [
      ...(negocio.sugerencias ?? []).map((pregunta) => ({ pregunta })),
      { pregunta: t.hablarConPersona, enviar: 'persona' },
    ],
  });

  if (token) {
    const { data, error: errorMensajes } = await supabase.rpc('chat_mensajes', { p_token: token, p_despues_de: 0 });
    if (!errorMensajes) mostrarMensajes(data);
  }

  $entrada.placeholder = t.placeholder;
  $entrada.disabled = false;
  $botonEnviar.disabled = false;
  $botonEnviar.setAttribute('aria-label', t.enviar);
  $entrada.focus();

  // Así llegan las respuestas que el dueño escriba desde su panel.
  setInterval(revisarNuevos, 4000);
  setInterval(() => actualizarEstado().catch(() => {}), 60000);
}

arrancar();
