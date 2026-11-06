import { supabase } from './supabase.js';
import { textos } from './textos.js';
import { crearEditorHorario } from './horario.js';
import { abrirPago, abrirPortal, leerPlan, diasRestantes } from './plan.js';
import qrcode from 'qrcode-generator';

const t = textos.panel;
const $mensaje = document.getElementById('mensaje');
const $salir = document.getElementById('salir');
const $verChat = document.getElementById('ver-chat');
const $pestanas = document.getElementById('pestanas');
let negocioActual = null;

// Menú lateral -------------------------------------------------------------
// En computadora siempre está a la vista; en celular se abre con ☰ y se
// cierra al elegir una sección, al tocar fuera o con Esc.

const $menu = document.getElementById('menu');
const $menuAbrir = document.getElementById('menu-abrir');
const $menuFondo = document.getElementById('menu-fondo');
const alAbrirSeccion = {};

function menuAbierto(abierto) {
  $menu.classList.toggle('abierto', abierto);
  $menuFondo.hidden = !abierto;
  $menuAbrir.setAttribute('aria-expanded', abierto);
  document.body.classList.toggle('menu-abierto', abierto);
  if (abierto) $menu.querySelector('.menu-item.activa')?.focus();
}

function iniciarPestanas() {
  for (const $b of $pestanas.querySelectorAll('[data-seccion]')) {
    $b.querySelector('[data-etiqueta]').textContent = t.pestanas[$b.dataset.seccion];
    $b.addEventListener('click', () => mostrarSeccion($b.dataset.seccion));
  }
  document.getElementById('menu-abrir-texto').textContent = t.menu.abrir;
  document.getElementById('menu-cerrar').setAttribute('aria-label', t.menu.cerrar);
  document.getElementById('menu-cerrar').addEventListener('click', () => menuAbierto(false));
  $menuAbrir.addEventListener('click', () => menuAbierto(true));
  $menuFondo.addEventListener('click', () => menuAbierto(false));
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && $menu.classList.contains('abierto')) {
      menuAbierto(false);
      $menuAbrir.focus();
    }
  });
  $menuAbrir.hidden = false;
  $pestanas.hidden = false;
  mostrarSeccion('conversaciones');
}

function mostrarSeccion(nombre) {
  for (const $b of $pestanas.querySelectorAll('[data-seccion]')) {
    const activa = $b.dataset.seccion === nombre;
    $b.classList.toggle('activa', activa);
    if (activa) $b.setAttribute('aria-current', 'page');
    else $b.removeAttribute('aria-current');
  }
  for (const $s of document.querySelectorAll('[id^="seccion-"]')) {
    $s.hidden = $s.id !== `seccion-${nombre}`;
  }
  menuAbierto(false);
  alAbrirSeccion[nombre]?.();
  pintarPasos();
  window.scrollTo({ top: 0, behavior: 'instant' });
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
  queueMicrotask(pintarPasos);
  // Las que necesitan atención van arriba; dentro de cada grupo, la más reciente primero.
  conversaciones = data.sort((a, b) => ordenEstado[a.estado] - ordenEstado[b.estado]);
  pintarFiltros();
  pintarLista();
}

function pintarFiltros() {
  const cuenta = (estado) => conversaciones.filter((c) => estado === 'todas' || c.estado === estado).length;
  // En el menú, cuántas conversaciones te necesitan ahora.
  const $urgentes = document.getElementById('menu-urgentes');
  const urgentes = cuenta('te_necesita');
  $urgentes.textContent = urgentes;
  $urgentes.hidden = !urgentes;
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

function pintarVacio(visibles) {
  $vacio.hidden = visibles.length > 0;
  if (visibles.length) return;
  // Negocio recién creado: en lugar de un panel vacío, qué hacer para recibir clientes.
  if (!conversaciones.length && negocioActual) {
    const enlace = `${location.origin}/chat/${negocioActual.slug}`;
    const $texto = document.createElement('span');
    $texto.textContent = `${t.primerosPasos} `;
    const $enlace = document.createElement('a');
    $enlace.href = enlace;
    $enlace.target = '_blank';
    $enlace.rel = 'noopener';
    $enlace.textContent = enlace;
    const $copiar = document.createElement('button');
    $copiar.type = 'button';
    $copiar.className = 'boton-chico';
    $copiar.textContent = t.copiarEnlace;
    $copiar.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(enlace);
        marcarCompartido();
        $copiar.textContent = t.enlaceCopiado;
      } catch { /* el enlace queda a la vista para copiarlo a mano */ }
    });
    $vacio.className = 'primeros-pasos';
    $vacio.replaceChildren($texto, $enlace, $copiar);
    return;
  }
  $vacio.className = 'suave';
  $vacio.textContent = t.sinConversaciones;
}

function pintarLista() {
  const visibles = conversaciones.filter((c) => filtro === 'todas' || c.estado === filtro);
  pintarVacio(visibles);
  $lista.replaceChildren(...visibles.map((c) => {
    const ultimo = c.mensajes[0];
    const aviso = c.avisos.find((a) => a.estado === 'pendiente');
    const $li = document.createElement('li');
    $li.className = `conversacion estado-${c.estado}${c.id === abierta ? ' abierta' : ''}`;
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

// T08 · Atender a un cliente ----------------------------------------------

const $seccion = document.getElementById('seccion-conversaciones');
const $detalle = document.getElementById('detalle');
const $detMensajes = document.getElementById('detalle-mensajes');
const $detAviso = document.getElementById('detalle-aviso');
const $detForm = document.getElementById('detalle-form');
const $detTexto = document.getElementById('detalle-texto');
const $detError = document.getElementById('detalle-error');
const $detEnviar = document.getElementById('detalle-enviar');
const $detResolver = document.getElementById('detalle-resolver');
const $detSugerencia = document.getElementById('detalle-sugerencia');
const $detAgregar = document.getElementById('detalle-agregar');
let abierta = null;
let ultimoMensaje = 0;

$lista.addEventListener('click', (e) => {
  const $li = e.target.closest('[data-id]');
  if ($li) abrirConversacion($li.dataset.id);
});

document.getElementById('volver').addEventListener('click', cerrarConversacion);

function cerrarConversacion() {
  abierta = null;
  $detalle.hidden = true;
  $seccion.classList.remove('con-detalle');
  pintarLista();
  pintarPasos();
}

function horaCorta(fecha) {
  return new Date(fecha).toLocaleTimeString('es-MX', { hour: 'numeric', minute: '2-digit' });
}

function pintarMensaje(m) {
  const $m = document.createElement('div');
  $m.className = `globo globo-${m.autor}`;
  const $autor = document.createElement('span');
  $autor.className = 'globo-autor';
  $autor.textContent = `${t.autores[m.autor]} · ${horaCorta(m.creado_en)}`;
  const $texto = document.createElement('p');
  $texto.textContent = m.texto;
  $m.append($autor, $texto);
  $detMensajes.append($m);
  ultimoMensaje = Math.max(ultimoMensaje, m.id);
}

function pintarEncabezado(c) {
  document.getElementById('detalle-nombre').textContent = c.cliente_nombre || t.clienteSinNombre;
  document.getElementById('detalle-datos').textContent = t.datosCliente(c.cliente_telefono, t.intereses[c.interes]);
  const aviso = c.avisos.find((a) => a.estado === 'pendiente');
  if (c.estado === 'te_necesita' && aviso) {
    $detAviso.textContent = t.avisoDetalle(t.motivos[aviso.motivo]);
    $detAviso.className = 'detalle-aviso aviso-te_necesita';
    $detAviso.hidden = false;
  } else if (c.estado === 'la_atiendes_tu') {
    $detAviso.textContent = t.atiendesTu;
    $detAviso.className = 'detalle-aviso aviso-la_atiendes_tu';
    $detAviso.hidden = false;
  } else {
    $detAviso.hidden = true;
  }
  $detResolver.hidden = c.estado === 'al_dia';

  // Lo último que el chat no supo contestar en esta conversación → pregunta nueva.
  const noSabe = c.avisos
    .filter((a) => a.motivo === 'no_la_sabe' && !yaEsPregunta(a.mensaje_cliente))
    .sort((a, b) => new Date(b.creado_en) - new Date(a.creado_en))[0];
  $detSugerencia.hidden = !noSabe;
  if (noSabe) {
    document.getElementById('detalle-sugerencia-texto').textContent = t.agregar.sugerencia(noSabe.mensaje_cliente);
    $detAgregar.onclick = () => agregarComoPregunta(noSabe.mensaje_cliente);
  }
}

async function cargarDetalle(primeraVez) {
  if (!abierta) return;
  const id = abierta;
  const [{ data: conv }, { data: mensajes }] = await Promise.all([
    supabase.from('conversaciones')
      .select('id, estado, cliente_nombre, cliente_telefono, interes, avisos(motivo, estado, mensaje_cliente, creado_en)')
      .eq('id', id).single(),
    supabase.from('mensajes').select('id, autor, texto, creado_en')
      .eq('conversacion_id', id).gt('id', primeraVez ? 0 : ultimoMensaje).order('id'),
  ]);
  if (abierta !== id || !conv) return;
  pintarEncabezado(conv);
  const abajo = $detMensajes.scrollTop + $detMensajes.clientHeight >= $detMensajes.scrollHeight - 40;
  (mensajes ?? []).forEach(pintarMensaje);
  if (primeraVez || abajo) $detMensajes.scrollTop = $detMensajes.scrollHeight;
}

async function abrirConversacion(id) {
  abierta = id;
  ultimoMensaje = 0;
  $detMensajes.replaceChildren();
  $detError.hidden = true;
  $detTexto.value = '';
  $detalle.hidden = false;
  $seccion.classList.add('con-detalle');
  pintarLista();
  pintarPasos();
  await cargarDetalle(true);
  $detTexto.focus();
}

$detForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const texto = $detTexto.value.trim();
  if (!texto || !abierta) return;
  $detError.hidden = true;
  $detEnviar.disabled = true;
  $detEnviar.textContent = t.enviando;
  const { error } = await supabase.rpc('responder', { p_conversacion: abierta, p_texto: texto });
  $detEnviar.disabled = false;
  $detEnviar.textContent = t.enviar;
  if (error) {
    // El texto se queda en la caja para reintentar.
    $detError.textContent = t.noSeEnvio;
    $detError.hidden = false;
    return;
  }
  $detTexto.value = '';
  await Promise.all([cargarDetalle(false), cargarConversaciones()]);
  $detMensajes.scrollTop = $detMensajes.scrollHeight;
});

$detResolver.addEventListener('click', async () => {
  if (!abierta) return;
  $detResolver.disabled = true;
  const { error } = await supabase.rpc('resolver', { p_conversacion: abierta });
  $detResolver.disabled = false;
  if (error) {
    $detError.textContent = t.noSeResolvio;
    $detError.hidden = false;
    return;
  }
  await Promise.all([cargarDetalle(false), cargarConversaciones()]);
});

function iniciarConversaciones() {
  document.getElementById('volver').textContent = t.volver;
  $detTexto.placeholder = t.escribeRespuesta;
  $detEnviar.textContent = t.enviar;
  $detResolver.textContent = t.resolver;
  $detAgregar.textContent = t.agregar.boton;
  setInterval(() => cargarDetalle(false), 4000);
  cargarConversaciones();
  // Así aparecen solos los mensajes y avisos nuevos (RF-PAN-09: ≤ 10 s).
  setInterval(cargarConversaciones, 5000);
}

// T09 · Mis preguntas frecuentes -----------------------------------------

const tp = t.preguntas;
const $pForm = document.getElementById('pregunta-form');
const $pfTema = document.getElementById('pf-tema');
const $pfPregunta = document.getElementById('pf-pregunta');
const $pfOtras = document.getElementById('pf-otras');
const $pfRespuesta = document.getElementById('pf-respuesta');
const $pfError = document.getElementById('pf-error');
const $pfGuardar = document.getElementById('pf-guardar');
const $listaPreguntas = document.getElementById('lista-preguntas');
let preguntas = [];
let editando = null;

function errorPregunta(texto) {
  $pfError.textContent = texto;
  $pfError.hidden = !texto;
}

function abrirFormulario(p) {
  editando = p?.id ?? null;
  document.getElementById('pregunta-form-titulo').textContent = p ? tp.tituloEditar : tp.tituloNueva;
  $pfTema.value = p?.tema ?? 'precios';
  $pfPregunta.value = p?.pregunta ?? '';
  $pfOtras.value = p?.otras_formas ?? '';
  $pfRespuesta.value = p?.respuesta ?? '';
  errorPregunta('');
  $pfOrigen.hidden = true;
  $pfOk.hidden = true;
  $pForm.hidden = false;
  $pForm.scrollIntoView({ behavior: 'smooth', block: 'start' });
  $pfPregunta.focus();
}

function cerrarFormulario() {
  editando = null;
  $pForm.hidden = true;
  $pfOrigen.hidden = true;
}

const $pfOrigen = document.getElementById('pf-origen');
const $pfOk = document.getElementById('pf-ok');
const normalizar = (s) => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ¿?¡!.,]/g, '').replace(/\s+/g, ' ').trim();

// ¿Ese texto ya está guardado como pregunta (o como otra forma de preguntarla)?
function yaEsPregunta(texto) {
  const buscado = normalizar(texto ?? '');
  return preguntas.some((p) => normalizar(p.pregunta) === buscado
    || (p.otras_formas ?? '').split(',').some((o) => normalizar(o) === buscado));
}

// Idea tomada de Darwin: lo que el chat no supo se vuelve pregunta frecuente.
function agregarComoPregunta(texto) {
  mostrarSeccion('preguntas');
  abrirFormulario(null);
  $pfPregunta.value = texto.trim().slice(0, 150);
  $pfTema.value = 'otros';
  $pfOrigen.textContent = t.agregar.origen(texto.trim());
  $pfOrigen.hidden = false;
  $pfRespuesta.focus();
}

async function cargarPreguntas() {
  const { data, error } = await supabase.from('preguntas')
    .select('id, tema, pregunta, otras_formas, respuesta, activa, orden')
    .order('orden').order('pregunta');
  if (error) return;
  preguntas = data;
  pintarPreguntas();
}

function boton(texto, clase, accion) {
  const $b = document.createElement('button');
  $b.type = 'button';
  $b.className = clase;
  $b.textContent = texto;
  $b.addEventListener('click', accion);
  return $b;
}

function pintarPreguntas() {
  if (!preguntas.length) {
    const $p = document.createElement('p');
    $p.className = 'suave';
    $p.textContent = tp.vacio;
    return $listaPreguntas.replaceChildren($p);
  }
  const grupos = Object.keys(t.temas)
    .map((tema) => [tema, preguntas.filter((p) => p.tema === tema)])
    .filter(([, lista]) => lista.length);

  $listaPreguntas.replaceChildren(...grupos.map(([tema, lista]) => {
    const $grupo = document.createElement('section');
    $grupo.className = 'grupo-preguntas';
    const $h = document.createElement('h3');
    $h.textContent = t.temas[tema];
    $grupo.append($h, ...lista.map((p) => {
      const $c = document.createElement('article');
      $c.className = `pregunta${p.activa ? '' : ' pausada'}`;
      const $q = document.createElement('strong');
      $q.textContent = p.pregunta;
      const $r = document.createElement('p');
      $r.textContent = p.respuesta;
      $c.append($q, $r);
      if (p.otras_formas) {
        const $o = document.createElement('p');
        $o.className = 'suave pregunta-otras';
        $o.textContent = tp.otrasFormas + p.otras_formas;
        $c.append($o);
      }
      if (!p.activa) {
        const $e = document.createElement('span');
        $e.className = 'etiqueta';
        $e.textContent = tp.pausada;
        $c.append($e);
      }
      const $acciones = document.createElement('div');
      $acciones.className = 'pregunta-acciones';
      $acciones.append(
        boton(tp.editar, 'boton-chico', () => abrirFormulario(p)),
        boton(p.activa ? tp.pausar : tp.activar, 'boton-chico', () => cambiarActiva(p)),
        boton(tp.quitar, 'boton-chico boton-peligro', () => quitar(p)),
      );
      $c.append($acciones);
      return $c;
    }));
    return $grupo;
  }));
}

async function cambiarActiva(p) {
  const { error } = await supabase.from('preguntas')
    .update({ activa: !p.activa, actualizado_en: new Date().toISOString() }).eq('id', p.id);
  if (!error) cargarPreguntas();
}

async function quitar(p) {
  if (!confirm(tp.confirmarQuitar(p.pregunta))) return;
  const { error } = await supabase.from('preguntas').delete().eq('id', p.id);
  if (!error) {
    if (editando === p.id) cerrarFormulario();
    cargarPreguntas();
  }
}

$pForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const datos = {
    tema: $pfTema.value,
    pregunta: $pfPregunta.value.trim(),
    otras_formas: $pfOtras.value.trim() || null,
    respuesta: $pfRespuesta.value.trim(),
  };
  if (datos.pregunta.length < 3) return errorPregunta(tp.faltaPregunta);
  if (!datos.respuesta) return errorPregunta(tp.faltaRespuesta);
  errorPregunta('');
  $pfGuardar.disabled = true;
  $pfGuardar.textContent = tp.guardando;

  const consulta = editando
    ? supabase.from('preguntas').update({ ...datos, actualizado_en: new Date().toISOString() }).eq('id', editando)
    : supabase.from('preguntas').insert({
        ...datos,
        negocio_id: negocioActual.id,
        orden: Math.max(0, ...preguntas.map((p) => p.orden)) + 1,
      });
  const { error } = await consulta;

  $pfGuardar.disabled = false;
  $pfGuardar.textContent = tp.guardar;
  if (error) return errorPregunta(error.code === '23505' ? tp.repetida : tp.noSeGuardo);
  const veniaDeCliente = !$pfOrigen.hidden;
  cerrarFormulario();
  await cargarPreguntas();
  // Solo se dice "guardada" después de que la base respondió sin error.
  if (veniaDeCliente) {
    $pfOk.textContent = t.agregar.guardada;
    $pfOk.hidden = false;
  }
});

function iniciarPreguntas() {
  document.getElementById('preguntas-ayuda').textContent = tp.ayuda;
  const $agregar = document.getElementById('preguntas-agregar');
  $agregar.textContent = tp.agregar;
  $agregar.addEventListener('click', () => abrirFormulario(null));
  document.getElementById('pf-tema-etiqueta').textContent = tp.tema;
  document.getElementById('pf-pregunta-etiqueta').textContent = tp.pregunta;
  document.getElementById('pf-otras-etiqueta').textContent = tp.otras;
  document.getElementById('pf-respuesta-etiqueta').textContent = tp.respuesta;
  $pfGuardar.textContent = tp.guardar;
  const $cancelar = document.getElementById('pf-cancelar');
  $cancelar.textContent = tp.cancelar;
  $cancelar.addEventListener('click', cerrarFormulario);
  $pfTema.replaceChildren(...Object.entries(t.temas).map(([valor, etiqueta]) => new Option(etiqueta, valor)));
  cargarPreguntas();
}

// T10 · Mi negocio ---------------------------------------------------------

const tn = t.negocio;
const $nForm = document.getElementById('negocio-form');
const $nfNombre = document.getElementById('nf-nombre');
const $nfTelefono = document.getElementById('nf-telefono');
const $nfDireccion = document.getElementById('nf-direccion');
const $nfError = document.getElementById('nf-error');
const $nfOk = document.getElementById('nf-ok');
const $nfGuardar = document.getElementById('nf-guardar');
let editorHorario = null;

function avisoNegocio($p, texto) {
  $p.textContent = texto;
  $p.hidden = !texto;
}

async function iniciarNegocio() {
  document.getElementById('negocio-ayuda').textContent = tn.ayuda;
  document.getElementById('nf-nombre-etiqueta').textContent = tn.nombre;
  document.getElementById('nf-telefono-etiqueta').textContent = tn.telefono;
  document.getElementById('nf-direccion-etiqueta').textContent = tn.direccion;
  document.getElementById('nf-horario-titulo').textContent = tn.horario;
  $nfGuardar.textContent = tn.guardar;

  const { data, error } = await supabase.from('negocios')
    .select('nombre, telefono, direccion, horario').eq('id', negocioActual.id).single();
  if (error) return avisoNegocio($nfError, t.sinConexion);
  $nfNombre.value = data.nombre;
  $nfTelefono.value = data.telefono;
  $nfDireccion.value = data.direccion ?? '';
  editorHorario = crearEditorHorario(document.getElementById('nf-horario'), data.horario);
}

$nForm.addEventListener('input', () => avisoNegocio($nfOk, ''));

$nForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  avisoNegocio($nfOk, '');
  const nombre = $nfNombre.value.trim();
  const telefono = $nfTelefono.value.replace(/\D/g, '');
  if (nombre.length < 2) return avisoNegocio($nfError, tn.faltaNombre);
  if (telefono.length !== 10) return avisoNegocio($nfError, tn.telefonoMal);
  const { horario, error: errorHorario } = editorHorario.leer();
  if (errorHorario) return avisoNegocio($nfError, errorHorario);
  avisoNegocio($nfError, '');

  $nfGuardar.disabled = true;
  $nfGuardar.textContent = tn.guardando;
  const { data, error } = await supabase.from('negocios')
    .update({ nombre, telefono, direccion: $nfDireccion.value.trim() || null, horario })
    .eq('id', negocioActual.id)
    .select('nombre');
  $nfGuardar.disabled = false;
  $nfGuardar.textContent = tn.guardar;

  // Solo se dice "guardado" si la base regresó la fila cambiada.
  if (error || !data?.length) return avisoNegocio($nfError, tn.noSeGuardo);
  negocioActual.nombre = data[0].nombre;
  document.getElementById('nombre-negocio').textContent = data[0].nombre;
  document.getElementById('menu-negocio').textContent = data[0].nombre;
  document.title = data[0].nombre;
  avisoNegocio($nfOk, tn.guardado);
});

// Tu semana (reportes) -----------------------------------------------------
// Todo se cuenta con lo que las reglas por fila dejan ver: solo este negocio.

const tr = t.reportes;
const $repPeriodo = document.getElementById('rep-periodo');
const $repMensaje = document.getElementById('rep-mensaje');
const $repContenido = document.getElementById('rep-contenido');
let periodo = 7;
let cargandoReportes = false;

function el(etiqueta, clase, texto) {
  const $e = document.createElement(etiqueta);
  if (clase) $e.className = clase;
  if (texto !== undefined) $e.textContent = texto;
  return $e;
}

function avisoReportes(texto) {
  $repMensaje.textContent = texto;
  $repMensaje.hidden = !texto;
}

function pintarPeriodos() {
  document.getElementById('rep-titulo').textContent = tr.titulos[periodo];
  $repPeriodo.replaceChildren(...Object.entries(tr.periodos).map(([dias, etiqueta]) => {
    const $b = el('button', `filtro${Number(dias) === periodo ? ' activo' : ''}`, etiqueta);
    $b.type = 'button';
    $b.setAttribute('role', 'tab');
    $b.setAttribute('aria-selected', Number(dias) === periodo);
    $b.addEventListener('click', () => {
      periodo = Number(dias);
      pintarPeriodos();
      cargarReportes();
    });
    return $b;
  }));
}

async function cargarReportes() {
  if (cargandoReportes) return;
  cargandoReportes = true;
  avisoReportes(tr.cargando);
  const desde = new Date();
  desde.setHours(0, 0, 0, 0);
  desde.setDate(desde.getDate() - (periodo - 1));
  const iso = desde.toISOString();

  const [convs, avisos, respuestas] = await Promise.all([
    supabase.from('conversaciones').select('id, creada_en').gte('creada_en', iso),
    supabase.from('avisos').select('conversacion_id, motivo, mensaje_cliente, creado_en').gte('creado_en', iso),
    supabase.from('mensajes').select('pregunta_id, preguntas(pregunta)')
      .eq('autor', 'asistente').not('pregunta_id', 'is', null).gte('creado_en', iso),
  ]);
  cargandoReportes = false;
  if (convs.error || avisos.error || respuestas.error) {
    $repContenido.hidden = true;
    return avisoReportes(tr.sinConexion);
  }
  if (!convs.data.length && !respuestas.data.length) {
    $repContenido.hidden = true;
    return avisoReportes(tr.vacio);
  }
  avisoReportes('');
  $repContenido.hidden = false;
  pintarReportes(desde, convs.data, avisos.data, respuestas.data);
}

function pintarReportes(desde, convs, avisos, respuestas) {
  // Tarjetas con los números grandes.
  const conAviso = new Set(avisos.map((a) => a.conversacion_id));
  const necesitaron = convs.filter((c) => conAviso.has(c.id)).length;
  const soloChat = convs.length - necesitaron;
  const pct = convs.length ? Math.round((soloChat / convs.length) * 100) : 0;
  const tarjetas = [
    [tr.conversaciones, convs.length, tr.conversacionesNota],
    [tr.soloChat, soloChat, tr.soloChatNota(pct)],
    [tr.teNecesitaron, necesitaron, tr.teNecesitaronNota],
    [tr.respuestas, respuestas.length, tr.respuestasNota],
  ];
  document.getElementById('rep-tarjetas').replaceChildren(...tarjetas.map(([titulo, numero, nota]) => {
    const $t = el('div', 'rep-tarjeta');
    $t.append(el('span', 'rep-tarjeta-titulo', titulo), el('strong', 'rep-numero', numero.toLocaleString('es-MX')), el('span', 'suave', nota));
    return $t;
  }));

  // Conversaciones por día: una barra por día, con su número al pasar el dedo o el ratón.
  const dias = [];
  for (let i = 0; i < periodo; i++) {
    const d = new Date(desde);
    d.setDate(d.getDate() + i);
    dias.push({ fecha: d, n: 0 });
  }
  for (const c of convs) {
    const d = new Date(c.creada_en);
    d.setHours(0, 0, 0, 0);
    const i = Math.round((d - desde) / 86400000);
    if (dias[i]) dias[i].n += 1;
  }
  const max = Math.max(1, ...dias.map((d) => d.n));
  const $barras = document.getElementById('rep-dias');
  $barras.style.setProperty('--columnas', periodo);
  $barras.classList.toggle('rep-barras-mes', periodo > 7);
  $barras.replaceChildren(...dias.map(({ fecha, n }, i) => {
    const etiqueta = tr.porDiaTabla(tr.dia(fecha), n);
    const $col = el('div', 'rep-columna');
    $col.tabIndex = 0;
    $col.setAttribute('role', 'img');
    $col.setAttribute('aria-label', etiqueta);
    $col.title = etiqueta;
    const $valor = el('span', 'rep-valor', n ? String(n) : '');
    const $barra = el('span', `rep-barra${n ? '' : ' rep-barra-cero'}`);
    $barra.style.height = `${(n / max) * 100}%`;
    const $pista = el('span', 'rep-pista');
    $pista.append($valor, $barra);
    // En 30 días solo se rotula un día de cada semana para que no se encimen.
    const rotular = periodo <= 7 || (periodo - 1 - i) % 7 === 0;
    $col.append($pista, el('span', 'rep-dia', rotular ? tr.dia(fecha) : ''));
    return $col;
  }));

  // Lo que más preguntan (por pregunta frecuente usada).
  const cuenta = new Map();
  for (const r of respuestas) {
    const texto = r.preguntas?.pregunta;
    if (texto) cuenta.set(texto, (cuenta.get(texto) ?? 0) + 1);
  }
  const top = [...cuenta].sort((a, b) => b[1] - a[1]).slice(0, 5);
  const topMax = top[0]?.[1] ?? 1;
  const $top = document.getElementById('rep-top');
  $top.replaceChildren(...(top.length ? top.map(([texto, n]) => {
    const $li = el('li');
    const $fila = el('div', 'rep-top-fila');
    $fila.append(el('span', 'rep-top-texto', texto), el('span', 'rep-top-veces', tr.veces(n)));
    const $medida = el('span', 'rep-medida');
    $medida.style.width = `${(n / topMax) * 100}%`;
    $li.append($fila, $medida);
    return $li;
  }) : [el('li', 'suave rep-vacio', tr.topVacio)]));

  // Lo que no supo contestar, sin repetir, con su botón para agregarlo.
  const vistos = new Set();
  const noSabe = avisos
    .filter((a) => a.motivo === 'no_la_sabe')
    .sort((a, b) => new Date(b.creado_en) - new Date(a.creado_en))
    .filter((a) => {
      const llave = normalizar(a.mensaje_cliente);
      if (vistos.has(llave) || yaEsPregunta(a.mensaje_cliente)) return false;
      vistos.add(llave);
      return true;
    })
    .slice(0, 6);
  document.getElementById('rep-nosabe-ayuda').hidden = !noSabe.length;
  document.getElementById('rep-nosabe').replaceChildren(...(noSabe.length ? noSabe.map((a) => {
    const $li = el('li');
    $li.append(el('span', '', `«${a.mensaje_cliente}»`));
    const $b = el('button', 'boton-chico', t.agregar.boton);
    $b.type = 'button';
    $b.addEventListener('click', () => agregarComoPregunta(a.mensaje_cliente));
    $li.append($b);
    return $li;
  }) : [el('li', 'suave rep-vacio', tr.noSabeVacio)]));

  // Por qué te necesitaron.
  const motivos = Object.keys(t.motivos)
    .map((m) => [m, avisos.filter((a) => a.motivo === m).length])
    .filter(([, n]) => n)
    .sort((a, b) => b[1] - a[1]);
  document.getElementById('rep-motivos').replaceChildren(...(motivos.length ? motivos.map(([m, n]) => {
    const $li = el('li');
    $li.append(el('span', 'etiqueta etiqueta-motivo', t.motivos[m]), el('strong', '', String(n)));
    return $li;
  }) : [el('li', 'suave rep-vacio', tr.motivosVacio)]));
}

function iniciarReportes() {
  document.getElementById('rep-ayuda').textContent = tr.ayuda;
  document.getElementById('rep-dias-titulo').textContent = tr.porDia;
  document.getElementById('rep-top-titulo').textContent = tr.top;
  document.getElementById('rep-nosabe-titulo').textContent = tr.noSabe;
  document.getElementById('rep-nosabe-ayuda').textContent = tr.noSabeAyuda;
  document.getElementById('rep-motivos-titulo').textContent = tr.motivos;
  pintarPeriodos();
  // Se recalcula cada vez que se abre la sección.
  alAbrirSeccion.reportes = cargarReportes;
}

// Comparte tu chat (enlace, WhatsApp y código QR) ---------------------------

const tc = t.compartir;

function iniciarCompartir() {
  const url = `${location.origin}/chat/${negocioActual.slug}`;
  const nombre = () => negocioActual.nombre;
  document.getElementById('comp-titulo').textContent = tc.titulo;
  document.getElementById('comp-ayuda').textContent = tc.ayuda;
  document.getElementById('comp-url').value = url;
  const $copiar = document.getElementById('comp-copiar');
  $copiar.textContent = tc.copiar;
  $copiar.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(url);
      marcarCompartido();
      $copiar.textContent = tc.copiado;
      setTimeout(() => { $copiar.textContent = tc.copiar; }, 2000);
    } catch {
      document.getElementById('comp-url').select();
    }
  });
  const $whatsapp = document.getElementById('comp-whatsapp');
  $whatsapp.textContent = tc.whatsapp;
  $whatsapp.addEventListener('click', marcarCompartido);
  const $probar = document.getElementById('comp-probar');
  $probar.textContent = tc.probar;
  $probar.href = url;
  document.getElementById('comp-mensaje-titulo').textContent = tc.mensajeTitulo;
  document.getElementById('qr-titulo').textContent = tc.qrTitulo;
  document.getElementById('qr-ayuda').textContent = tc.qrAyuda;
  const $imprimir = document.getElementById('qr-imprimir');
  $imprimir.textContent = tc.imprimir;
  $imprimir.addEventListener('click', () => {
    marcarCompartido();
    document.body.classList.add('imprimiendo-qr');
    window.print();
  });
  window.addEventListener('afterprint', () => document.body.classList.remove('imprimiendo-qr'));

  // El código QR se arma aquí mismo, sin mandar el enlace a ningún otro sitio.
  const qr = qrcode(0, 'M');
  qr.addData(url);
  qr.make();
  const $qr = document.getElementById('qr');
  $qr.innerHTML = qr.createSvgTag({ cellSize: 6, margin: 2, scalable: true });

  // El nombre puede cambiar en "Mi negocio": el mensaje se arma al abrir la sección.
  alAbrirSeccion.compartir = () => {
    const mensaje = tc.mensaje(nombre(), url);
    $whatsapp.href = `https://wa.me/?text=${encodeURIComponent(mensaje)}`;
    document.getElementById('comp-mensaje').textContent = mensaje;
    document.getElementById('qr-nombre').textContent = tc.qrNombre(nombre());
    $qr.setAttribute('aria-label', tc.qrDescripcion(nombre()));
  };
}

// Prueba gratis de 7 días y plan mensual ------------------------------------
// El estado vive fijo en el menú lateral. El aviso grande de arriba solo sale
// cuando hay algo que hacer (activar, pago fallido, cancelado) o al volver de Stripe.

const tpl = textos.plan;
const $plan = document.getElementById('plan');
const $planTexto = document.getElementById('plan-texto');
const $planBoton = document.getElementById('plan-boton');
const $planCerrar = document.getElementById('plan-cerrar');
const $planError = document.getElementById('plan-error');
const $menuPlan = document.getElementById('menu-plan');
const $menuPlanTexto = document.getElementById('menu-plan-texto');
const $menuPlanBarra = document.getElementById('menu-plan-barra');
const $menuPlanBoton = document.getElementById('menu-plan-boton');
let planActual = null;

// Qué hace cada botón del plan: registrar tarjeta o abrir la página de Stripe del plan.
async function accionPlan($boton, accion, $error) {
  const etiqueta = $boton.textContent;
  $boton.disabled = true;
  $boton.textContent = accion === 'portal' ? tpl.abriendoPortal : tpl.abriendo;
  if ($error) $error.hidden = true;
  try {
    await (accion === 'portal' ? abrirPortal() : abrirPago());
  } catch {
    $boton.disabled = false;
    $boton.textContent = etiqueta;
    const mensaje = accion === 'portal' ? tpl.noAbrioPortal : tpl.noAbrio;
    if ($error) {
      $error.textContent = mensaje;
      $error.hidden = false;
    } else {
      avisoPlan(mensaje, null);
    }
  }
}

function avisoPlan(texto, boton, { ok = false, cerrable = false } = {}) {
  $planTexto.textContent = texto;
  $plan.classList.toggle('plan-ok', ok);
  $planBoton.hidden = !boton;
  if (boton) {
    $planBoton.textContent = boton.texto;
    $planBoton.dataset.accion = boton.accion;
  }
  $planCerrar.hidden = !cerrable;
  $planError.hidden = true;
  $plan.hidden = false;
}

function pintarPlan(plan, { recienVuelve = false } = {}) {
  planActual = plan;
  // Los negocios de la demo no pagan.
  if (!plan || plan.es_demo) {
    $plan.hidden = true;
    $menuPlan.hidden = true;
    pintarPasos();
    return;
  }
  const tm = tpl.menu;
  let menu = '';
  let menuBoton = null;
  $menuPlanBarra.hidden = true;
  $plan.hidden = true;

  if (plan.estado === 'prueba' && !plan.plan_termina) {
    const dias = diasRestantes(plan.prueba_termina);
    menu = tm.prueba(dias);
    $menuPlanBarra.hidden = false;
    $menuPlanBarra.firstElementChild.style.width = `${Math.min(100, ((7 - dias) / 7) * 100 + 8)}%`;
    menuBoton = { texto: tpl.administrar, accion: 'portal' };
    if (recienVuelve) avisoPlan(tpl.bienvenida(tpl.fecha(plan.prueba_termina)), null, { ok: true, cerrable: true });
  } else if ((plan.estado === 'prueba' || plan.estado === 'activa') && plan.plan_termina) {
    menu = tm.termina(tpl.fecha(plan.plan_termina));
    menuBoton = { texto: tpl.administrar, accion: 'portal' };
    avisoPlan(tpl.termina(tpl.fecha(plan.plan_termina)), { texto: tpl.administrar, accion: 'portal' }, { cerrable: true });
  } else if (plan.estado === 'activa') {
    menu = tm.activa;
    menuBoton = { texto: tpl.administrar, accion: 'portal' };
  } else if (plan.estado === 'pago_pendiente') {
    menu = tm.pagoPendiente;
    menuBoton = { texto: tpl.actualizarTarjeta, accion: 'portal' };
    avisoPlan(tpl.pagoPendiente, { texto: tpl.actualizarTarjeta, accion: 'portal' });
  } else if (plan.estado === 'cancelada') {
    menu = tm.cancelada;
    menuBoton = { texto: tpl.activarPlan, accion: 'pago' };
    avisoPlan(tpl.cancelada, { texto: tpl.activarPlan, accion: 'pago' });
  } else {
    menu = tm.sinActivar;
    menuBoton = { texto: plan.puede_probar ? tpl.activar : tpl.activarPlan, accion: 'pago' };
    avisoPlan(plan.puede_probar ? tpl.explicacion : tpl.sinPrueba,
      { texto: plan.puede_probar ? tpl.activar : tpl.activarPlan, accion: 'pago' });
  }

  $menuPlan.className = `menu-plan plan-${plan.estado}`;
  $menuPlanTexto.textContent = menu;
  $menuPlanBoton.textContent = menuBoton.texto;
  $menuPlanBoton.dataset.accion = menuBoton.accion;
  $menuPlanBoton.disabled = false;
  $menuPlan.hidden = false;
  pintarPasos();
}

$planBoton.addEventListener('click', () => accionPlan($planBoton, $planBoton.dataset.accion, $planError));
$menuPlanBoton.addEventListener('click', () => accionPlan($menuPlanBoton, $menuPlanBoton.dataset.accion, null));
$planCerrar.addEventListener('click', () => { $plan.hidden = true; });

async function iniciarPlan() {
  $planCerrar.setAttribute('aria-label', tpl.cerrar);
  const params = new URLSearchParams(location.search);
  const s = params.get('s');
  const vuelta = params.get('plan');
  if (vuelta) history.replaceState(null, '', location.pathname);
  if (s) avisoPlan(tpl.confirmando, null);
  try {
    pintarPlan(await leerPlan(s), { recienVuelve: vuelta === 'listo' });
    if (vuelta === 'cancelado' && !$planBoton.hidden) {
      $planError.textContent = tpl.volvioSinTarjeta;
      $planError.hidden = false;
    }
  } catch {
    // Sin respuesta: no se inventa un estado.
    $plan.hidden = true;
  }
}

// Tus primeros pasos ------------------------------------------------------
// Cada paso se marca con lo que ya está guardado (negocio, plan, conversaciones).
// Lo único que no está en la base es "compartí mi enlace": se recuerda en este
// navegador porque compartir pasa fuera de la página.

const tps = t.pasos;
const $pasosCaja = document.getElementById('pasos');
let pasosOcultos = false;
const llaveLocal = (cosa) => `agente-pyme:${cosa}:${negocioActual?.slug}`;
function leerLocal(cosa) { try { return localStorage.getItem(llaveLocal(cosa)) === '1'; } catch { return false; } }
function guardarLocal(cosa) { try { localStorage.setItem(llaveLocal(cosa), '1'); } catch { /* sin memoria del navegador */ } }

function marcarCompartido() {
  guardarLocal('compartio');
  pintarPasos();
}

function pintarPasos() {
  // Hasta saber en qué va su plan, para no ofrecer algo que ya hizo.
  if (!negocioActual || negocioActual.es_demo || !planActual || pasosOcultos || leerLocal('pasos-ocultos')) {
    $pasosCaja.hidden = true;
    return;
  }
  const conPlan = ['prueba', 'activa'].includes(planActual?.estado);
  const lista = [
    ['creado', true, null],
    ['prueba', conPlan, () => accionPlan(document.querySelector('[data-paso="prueba"] button'), 'pago', null)],
    ['probar', conversaciones.length > 0, () => window.open(`/chat/${negocioActual.slug}`, '_blank', 'noopener')],
    ['compartir', leerLocal('compartio'), () => mostrarSeccion('compartir')],
  ];
  const hechos = lista.filter(([, hecho]) => hecho).length;
  document.getElementById('pasos-titulo').textContent = hechos === lista.length ? tps.listo : tps.titulo;
  document.getElementById('pasos-progreso').textContent = tps.progreso(hechos, lista.length);
  document.getElementById('pasos-barra').style.width = `${(hechos / lista.length) * 100}%`;
  const $ocultar = document.getElementById('pasos-ocultar');
  $ocultar.textContent = tps.ocultar;
  document.getElementById('pasos-lista').replaceChildren(...lista.map(([clave, hecho, accion]) => {
    const [texto, etiqueta] = tps[clave];
    const $li = document.createElement('li');
    $li.className = hecho ? 'hecho' : '';
    $li.dataset.paso = clave;
    const $marca = document.createElement('span');
    $marca.className = 'primeros-marca';
    $marca.setAttribute('aria-hidden', 'true');
    $marca.textContent = hecho ? '✓' : '';
    const $texto = document.createElement('span');
    $texto.className = 'primeros-texto';
    $texto.textContent = texto;
    $li.append($marca, $texto);
    if (!hecho && accion) {
      const $b = document.createElement('button');
      $b.type = 'button';
      $b.className = 'boton-chico';
      $b.textContent = etiqueta;
      $b.addEventListener('click', accion);
      $li.append($b);
    }
    return $li;
  }));
  // En la sección de conversaciones y sin un cliente abierto.
  const enConversaciones = !document.getElementById('seccion-conversaciones').hidden;
  $pasosCaja.hidden = !enConversaciones || Boolean(abierta);
  // Si la lista ya ofrece activar la prueba, no se repite en el aviso de arriba.
  if (!$pasosCaja.hidden && planActual?.estado === 'sin_activar') $plan.hidden = true;
}

document.getElementById('pasos-ocultar').addEventListener('click', () => {
  pasosOcultos = true;
  guardarLocal('pasos-ocultos');
  pintarPasos();
});

// Arranque (al final, cuando todo lo de arriba ya está declarado) -----------

async function arrancar() {
  $mensaje.textContent = t.cargando;

  const { data: { session } } = await supabase.auth.getSession();
  if (!session) return location.replace('/entrar');

  $salir.textContent = t.salir;
  $salir.hidden = false;
  $salir.addEventListener('click', async () => {
    await supabase.auth.signOut();
    location.replace('/entrar');
  });

  // Las reglas por fila solo dejan ver los negocios donde esta cuenta es miembro.
  const { data: negocios, error } = await supabase.from('negocios').select('id, slug, nombre, es_demo').limit(1);
  const negocio = negocios?.[0];

  if (error) {
    $mensaje.textContent = t.sinConexion;
  } else if (!negocio) {
    // Tiene cuenta pero no negocio: el siguiente paso es crearlo.
    $mensaje.textContent = `${t.sinNegocio} `;
    const $crear = document.createElement('a');
    $crear.href = '/crear';
    $crear.className = 'boton-principal boton-enlace';
    $crear.textContent = t.crearNegocio;
    $mensaje.append($crear);
  } else {
    document.title = negocio.nombre;
    document.getElementById('nombre-negocio').textContent = negocio.nombre;
    document.getElementById('menu-negocio').textContent = negocio.nombre;
    $verChat.textContent = t.verChat;
    $verChat.href = `/chat/${negocio.slug}`;
    $verChat.hidden = false;
    const $nota = document.getElementById('nota-prueba');
    $nota.textContent = t.notaPrueba;
    $nota.hidden = false;
    $mensaje.textContent = '';
    negocioActual = negocio;
    iniciarPestanas();
    iniciarConversaciones();
    iniciarPreguntas();
    iniciarNegocio();
    iniciarReportes();
    iniciarCompartir();
    iniciarPlan();
  }
}

arrancar();
