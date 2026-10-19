import { supabase } from './supabase.js';
import { textos } from './textos.js';

const t = textos.panel;
const $mensaje = document.getElementById('mensaje');
const $salir = document.getElementById('salir');
const $verChat = document.getElementById('ver-chat');
const $pestanas = document.getElementById('pestanas');

$mensaje.textContent = t.cargando;

const { data: { session } } = await supabase.auth.getSession();
if (!session) location.replace('/entrar');

$salir.textContent = t.salir;
$salir.hidden = false;
$salir.addEventListener('click', async () => {
  await supabase.auth.signOut();
  location.replace('/entrar');
});

// Las reglas por fila solo dejan ver los negocios donde esta cuenta es miembro.
const { data: negocios, error } = await supabase.from('negocios').select('id, slug, nombre').limit(1);
const negocio = negocios?.[0];

if (error) {
  $mensaje.textContent = t.sinConexion;
} else if (!negocio) {
  $mensaje.textContent = t.sinNegocio;
} else {
  document.title = negocio.nombre;
  document.getElementById('nombre-negocio').textContent = negocio.nombre;
  $verChat.textContent = t.verChat;
  $verChat.href = `/chat/${negocio.slug}`;
  $verChat.hidden = false;
  $mensaje.textContent = '';
  iniciarPestanas();
  iniciarConversaciones();
}

function iniciarPestanas() {
  for (const $b of $pestanas.querySelectorAll('[data-seccion]')) {
    $b.textContent = t.pestanas[$b.dataset.seccion];
    $b.addEventListener('click', () => mostrarSeccion($b.dataset.seccion));
  }
  $pestanas.hidden = false;
  mostrarSeccion('conversaciones');
}

function mostrarSeccion(nombre) {
  for (const $b of $pestanas.querySelectorAll('[data-seccion]')) {
    $b.classList.toggle('activa', $b.dataset.seccion === nombre);
  }
  for (const $s of document.querySelectorAll('[id^="seccion-"]')) {
    $s.hidden = $s.id !== `seccion-${nombre}`;
  }
}

// T07 · Mis conversaciones -------------------------------------------------

const $filtros = document.getElementById('filtros');
const $lista = document.getElementById('lista-conversaciones');
const $vacio = document.getElementById('sin-conversaciones');
const ordenEstado = { te_necesita: 0, la_atiendes_tu: 1, al_dia: 2 };
let conversaciones = [];
let filtro = 'todas';
let firma = '';

// Un solo escucha para los filtros: así un clic nunca cae en un botón que se acaba de redibujar.
$filtros.addEventListener('click', (e) => {
  const $b = e.target.closest('[data-filtro]');
  if (!$b) return;
  filtro = $b.dataset.filtro;
  pintarFiltros();
  pintarLista();
});

async function cargarConversaciones() {
  const { data, error: e } = await supabase
    .from('conversaciones')
    .select('id, estado, cliente_nombre, ultimo_mensaje_en, mensajes(texto, autor, id), avisos(motivo, estado, mensaje_cliente)')
    .order('ultimo_mensaje_en', { ascending: false })
    .order('id', { referencedTable: 'mensajes', ascending: false })
    .limit(1, { referencedTable: 'mensajes' });
  if (e) return;
  // Solo se redibuja si algo cambió.
  const nueva = JSON.stringify(data);
  if (nueva === firma) return;
  firma = nueva;
  // Las que necesitan atención van arriba; dentro de cada grupo, la más reciente primero.
  conversaciones = data.sort((a, b) => ordenEstado[a.estado] - ordenEstado[b.estado]);
  pintarFiltros();
  pintarLista();
}

function pintarFiltros() {
  const cuenta = (estado) => conversaciones.filter((c) => estado === 'todas' || c.estado === estado).length;
  $filtros.replaceChildren(...Object.entries(t.filtros).map(([clave, etiqueta]) => {
    const $b = document.createElement('button');
    $b.className = `filtro${clave === filtro ? ' activo' : ''}${clave === 'te_necesita' && cuenta(clave) ? ' urgente' : ''}`;
    $b.setAttribute('role', 'tab');
    $b.setAttribute('aria-selected', clave === filtro);
    $b.dataset.filtro = clave;
    $b.textContent = `${etiqueta} (${cuenta(clave)})`;
    return $b;
  }));
}

function pintarLista() {
  const visibles = conversaciones.filter((c) => filtro === 'todas' || c.estado === filtro);
  $vacio.textContent = t.sinConversaciones;
  $vacio.hidden = visibles.length > 0;
  $lista.replaceChildren(...visibles.map((c) => {
    const ultimo = c.mensajes[0];
    const aviso = c.avisos.find((a) => a.estado === 'pendiente');
    const $li = document.createElement('li');
    $li.className = `conversacion estado-${c.estado}`;
    $li.dataset.id = c.id;

    const $arriba = document.createElement('div');
    $arriba.className = 'conversacion-arriba';
    const $nombre = document.createElement('strong');
    $nombre.textContent = c.cliente_nombre || t.clienteSinNombre;
    const $hace = document.createElement('span');
    $hace.className = 'suave';
    $hace.textContent = t.hace(c.ultimo_mensaje_en);
    $arriba.append($nombre, $hace);

    const $texto = document.createElement('p');
    $texto.className = 'conversacion-ultimo';
    // Si el cliente te necesita, se ve lo que preguntó; si no, el último mensaje.
    $texto.textContent = aviso && c.estado === 'te_necesita' ? `«${aviso.mensaje_cliente}»` : (ultimo?.texto ?? '');

    const $etiquetas = document.createElement('div');
    $etiquetas.className = 'conversacion-etiquetas';
    const $estado = document.createElement('span');
    $estado.className = `etiqueta etiqueta-${c.estado}`;
    $estado.textContent = t.estados[c.estado];
    $etiquetas.append($estado);
    if (aviso && c.estado === 'te_necesita') {
      const $motivo = document.createElement('span');
      $motivo.className = 'etiqueta etiqueta-motivo';
      $motivo.textContent = t.motivos[aviso.motivo];
      $etiquetas.append($motivo);
    }

    $li.append($arriba, $texto, $etiquetas);
    return $li;
  }));
}

function iniciarConversaciones() {
  cargarConversaciones();
  // Así aparecen solos los mensajes y avisos nuevos (RF-PAN-09: ≤ 10 s).
  setInterval(cargarConversaciones, 5000);
}
