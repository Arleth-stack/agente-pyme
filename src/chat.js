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

function burbuja({ autor, texto, creado_en }) {
  const $b = document.createElement('div');
  $b.className = `burbuja ${autor === 'cliente' ? 'burbuja-cliente' : 'burbuja-negocio'}`;
  const $texto = document.createElement('p');
  $texto.textContent = texto;
  const $hora = document.createElement('span');
  $hora.className = 'burbuja-hora';
  $hora.textContent = horaDe(creado_en ?? Date.now());
  $b.append($texto, $hora);
  $mensajes.append($b);
  $mensajes.scrollTop = $mensajes.scrollHeight;
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
    const { data, error } = await supabase.rpc('chat_enviar', { p_token: token, p_texto: texto });
    if (error) throw error;
    // La burbuja temporal se cambia por lo que la base confirmó que guardó.
    $pendiente.remove();
    mostrarMensajes(data);
  } catch {
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

  const { data: negocio, error } = await supabase.rpc('chat_negocio', { p_slug: slug });
  if (error) return mostrarAviso(t.sinConexion);
  if (!negocio) return mostrarAviso(t.noEncontrado);

  document.title = negocio.nombre;
  document.getElementById('nombre-negocio').textContent = negocio.nombre;
  document.getElementById('avatar').textContent = iniciales(negocio.nombre);

  burbuja({ autor: 'asistente', texto: t.bienvenida(negocio.nombre), creado_en: Date.now() });

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
}

arrancar();
