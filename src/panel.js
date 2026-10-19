import { supabase } from './supabase.js';
import { textos } from './textos.js';

const t = textos.panel;
const $mensaje = document.getElementById('mensaje');
const $salir = document.getElementById('salir');
const $verChat = document.getElementById('ver-chat');
const $pestanas = document.getElementById('pestanas');
let negocioActual = null;

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
}

async function cargarDetalle(primeraVez) {
  if (!abierta) return;
  const id = abierta;
  const [{ data: conv }, { data: mensajes }] = await Promise.all([
    supabase.from('conversaciones')
      .select('id, estado, cliente_nombre, cliente_telefono, interes, avisos(motivo, estado)')
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
  $pForm.hidden = false;
  $pForm.scrollIntoView({ behavior: 'smooth', block: 'start' });
  $pfPregunta.focus();
}

function cerrarFormulario() {
  editando = null;
  $pForm.hidden = true;
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
  cerrarFormulario();
  cargarPreguntas();
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
    negocioActual = negocio;
    iniciarPestanas();
    iniciarConversaciones();
    iniciarPreguntas();
  }
}

arrancar();
