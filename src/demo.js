import { supabase } from './supabase.js';
import { textos } from './textos.js';

const t = textos.demo;
const $negocio = document.getElementById('demo-negocio');
const $hora = document.getElementById('demo-hora');
const $reiniciar = document.getElementById('demo-reiniciar');
const $estado = document.getElementById('demo-estado');
const $chat = document.getElementById('demo-chat');
const $panel = document.getElementById('demo-panel');
const $avisoPanel = document.getElementById('demo-aviso-panel');
const $lados = document.getElementById('demo-lados');
let demo = [];

document.title = t.titulo;
document.getElementById('demo-negocio-etiqueta').textContent = t.negocio;
document.getElementById('demo-hora-etiqueta').textContent = t.hora;
document.getElementById('demo-titulo-cliente').textContent = t.tituloCliente;
document.getElementById('demo-titulo-dueno').textContent = t.tituloDueno;
$reiniciar.textContent = t.reiniciar;
$hora.replaceChildren(...Object.entries(t.horas).map(([v, e]) => new Option(e, v)));
for (const $b of document.querySelectorAll('button[data-vista]')) {
  $b.textContent = t[$b.dataset.vista];
  $b.addEventListener('click', () => {
    $lados.dataset.vista = $b.dataset.vista;
    for (const $o of document.querySelectorAll('button[data-vista]')) $o.classList.toggle('activa', $o === $b);
  });
}

function cargarChat() {
  const hora = $hora.value === 'real' ? '' : `?hora=${$hora.value}`;
  $chat.src = `/chat/${$negocio.value}${hora}`;
}

// El panel usa la sesión de quien entró; si es de otro negocio, se avisa.
async function revisarPanel() {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) return ($avisoPanel.hidden = true);
  const { data } = await supabase.from('negocios').select('slug, nombre').limit(1);
  const actual = data?.[0];
  const elegido = demo.find((n) => n.slug === $negocio.value);
  $avisoPanel.hidden = !actual || actual.slug === elegido?.slug;
  if (actual && elegido) $avisoPanel.textContent = t.otraSesion(actual.nombre, elegido.nombre);
}

$negocio.addEventListener('change', () => { cargarChat(); revisarPanel(); });
$hora.addEventListener('change', cargarChat);
$panel.addEventListener('load', revisarPanel);

$reiniciar.addEventListener('click', async () => {
  if (!confirm(t.confirmar)) return;
  $reiniciar.disabled = true;
  $reiniciar.textContent = t.reiniciando;
  $estado.textContent = '';
  const { error } = await supabase.rpc('reiniciar_demo');
  $reiniciar.disabled = false;
  $reiniciar.textContent = t.reiniciar;
  if (error) return ($estado.textContent = t.noSeReinicio);
  // Las conversaciones que este navegador tenía abiertas ya no existen.
  try {
    for (const clave of Object.keys(localStorage)) if (clave.startsWith('conversacion:')) localStorage.removeItem(clave);
  } catch { /* sin almacenamiento */ }
  $estado.textContent = t.reiniciado;
  cargarChat();
  $panel.contentWindow?.location.reload();
});

const { data } = await supabase.rpc('negocios_demo');
demo = data ?? [];
$negocio.replaceChildren(...demo.map((n) => new Option(n.nombre, n.slug)));
const inicial = new URLSearchParams(location.search).get('negocio');
if (demo.some((n) => n.slug === inicial)) $negocio.value = inicial;
cargarChat();
