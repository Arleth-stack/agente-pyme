import { textos } from './textos.js';
import { crearEditorHorario, describirHorario } from './horario.js';

const t = textos.crear;
const $form = document.getElementById('formulario');
const $error = document.getElementById('error');
const $atras = document.getElementById('atras');
const $siguiente = document.getElementById('siguiente');
const $pasos = document.getElementById('pasos');
const $nombre = document.getElementById('nombre');
const $giro = document.getElementById('giro');
const $telefono = document.getElementById('telefono');
const $direccion = document.getElementById('direccion');

// Todo lo capturado vive aquí mientras se llena el formulario: "Atrás" no borra nada.
const datos = { nombre: '', giro: '', telefono: '', direccion: '', horario: null, preguntas: [] };
let paso = 1;

const horarioInicial = {
  lun: { abre: '09:00', cierra: '18:00' }, mar: { abre: '09:00', cierra: '18:00' },
  mie: { abre: '09:00', cierra: '18:00' }, jue: { abre: '09:00', cierra: '18:00' },
  vie: { abre: '09:00', cierra: '18:00' }, sab: { abre: '09:00', cierra: '14:00' }, dom: null,
};
const editorHorario = crearEditorHorario(document.getElementById('horario'), horarioInicial);

function texto(id, valor) {
  document.getElementById(id).textContent = valor;
}

function pintarTextos() {
  document.title = t.titulo;
  texto('volver-inicio', t.volver);
  texto('titulo', t.titulo);
  texto('subtitulo', t.subtitulo);
  texto('p1-titulo', t.p1.titulo);
  texto('p1-ayuda', t.p1.ayuda);
  texto('nombre-etiqueta', t.p1.nombre);
  texto('giro-etiqueta', t.p1.giro);
  texto('telefono-etiqueta', t.p1.telefono);
  texto('direccion-etiqueta', t.p1.direccion);
  texto('p2-titulo', t.p2.titulo);
  texto('p2-ayuda', t.p2.ayuda);
  texto('p3-titulo', t.p3.titulo);
  texto('p3-ayuda', t.p3.ayuda);
  texto('agregar-pregunta', t.p3.agregar);
  $atras.textContent = t.atras;
  $giro.replaceChildren(new Option(t.p1.eligeGiro, ''), ...Object.entries(t.giros).map(([v, e]) => new Option(e, v)));
}

function mostrarError(mensaje) {
  $error.textContent = mensaje;
  $error.hidden = !mensaje;
}

function irA(n) {
  paso = n;
  for (const $f of $form.querySelectorAll('fieldset[data-paso]')) {
    $f.hidden = Number($f.dataset.paso) !== paso;
  }
  $pasos.replaceChildren(...t.pasos.map((nombre, i) => {
    const $li = document.createElement('li');
    $li.textContent = nombre;
    $li.className = i + 1 < paso ? 'hecho' : i + 1 === paso ? 'actual' : '';
    if (i + 1 === paso) $li.setAttribute('aria-current', 'step');
    return $li;
  }));
  $pasos.setAttribute('aria-label', t.pasoDe(paso));
  $atras.hidden = paso === 1;
  $siguiente.textContent = t.siguiente;
  mostrarError('');
  $form.querySelector(`fieldset[data-paso="${paso}"] input, fieldset[data-paso="${paso}"] select`)?.focus();
}

// Cada paso se valida antes de avanzar; regresa un mensaje si algo falta.
const validar = {
  1() {
    datos.nombre = $nombre.value.trim();
    datos.giro = $giro.value;
    datos.telefono = $telefono.value.replace(/\D/g, '');
    datos.direccion = $direccion.value.trim();
    if (datos.nombre.length < 2) return t.faltaNombre;
    if (!datos.giro) return t.faltaGiro;
    if (datos.telefono.length !== 10) return t.telefonoMal;
    return '';
  },
  2() {
    const { horario, error } = editorHorario.leer();
    if (error) return error;
    datos.horario = horario;
    return '';
  },
};

// T12 · Paso 3: preguntas sugeridas según el giro --------------------------

const $listaPreguntas = document.getElementById('lista-preguntas');
let giroSugerido = null;

function tarjetaPregunta({ tema = 'otros', pregunta = '', otras = '', respuesta = '' } = {}) {
  const $c = document.createElement('div');
  $c.className = 'crear-pregunta';
  $c.dataset.tema = tema;
  $c.dataset.otras = otras;
  const id = `p${Math.random().toString(36).slice(2, 8)}`;

  const $lp = document.createElement('label');
  $lp.htmlFor = `${id}-q`;
  $lp.textContent = t.p3.pregunta;
  const $p = document.createElement('input');
  $p.id = `${id}-q`;
  $p.className = 'cp-pregunta';
  $p.maxLength = 150;
  $p.value = pregunta;

  const $lr = document.createElement('label');
  $lr.htmlFor = `${id}-r`;
  $lr.textContent = t.p3.respuesta;
  const $r = document.createElement('textarea');
  $r.id = `${id}-r`;
  $r.className = 'cp-respuesta';
  $r.rows = 2;
  $r.maxLength = 500;
  $r.value = respuesta;

  const $quitar = document.createElement('button');
  $quitar.type = 'button';
  $quitar.className = 'boton-chico boton-peligro';
  $quitar.textContent = t.p3.quitar;
  $quitar.addEventListener('click', () => $c.remove());

  $c.append($lp, $p, $lr, $r, $quitar);
  return $c;
}

function hayRespuestasEscritas() {
  return [...$listaPreguntas.querySelectorAll('.cp-respuesta')].some(($r) => $r.dataset.auto !== 'si' && $r.value.trim());
}

// Al entrar al paso 3 se sugieren las preguntas del giro. Si el dueño ya
// escribió respuestas, no se le borran aunque regrese y cambie el giro.
function prepararPreguntas() {
  if (giroSugerido === datos.giro && $listaPreguntas.children.length) return actualizarAutomaticas();
  if (giroSugerido && hayRespuestasEscritas()) return actualizarAutomaticas();
  giroSugerido = datos.giro;
  $listaPreguntas.replaceChildren(...textos.sugeridas[datos.giro].map(([tema, pregunta, otras]) =>
    tarjetaPregunta({ tema, pregunta, otras })));
  actualizarAutomaticas();
}

// Horario y ubicación se contestan solos con lo que ya escribió (los puede cambiar).
function actualizarAutomaticas() {
  for (const $c of $listaPreguntas.children) {
    const $r = $c.querySelector('.cp-respuesta');
    if ($r.value.trim() && $r.dataset.auto !== 'si') continue;
    let valor = '';
    if ($c.dataset.tema === 'horarios') valor = t.p3.horario(describirHorario(datos.horario));
    if ($c.dataset.tema === 'ubicacion' && datos.direccion) valor = t.p3.ubicacion(datos.direccion);
    if (valor) {
      $r.value = valor;
      $r.dataset.auto = 'si';
    }
  }
}

$listaPreguntas.addEventListener('input', (e) => {
  if (e.target.classList.contains('cp-respuesta')) delete e.target.dataset.auto;
});

document.getElementById('agregar-pregunta').addEventListener('click', () => {
  const $nueva = tarjetaPregunta();
  $listaPreguntas.append($nueva);
  $nueva.querySelector('input').focus();
});

function normal(texto) {
  return texto.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
}

validar[3] = () => {
  const preguntas = [];
  for (const $c of $listaPreguntas.children) {
    const pregunta = $c.querySelector('.cp-pregunta').value.trim();
    const respuesta = $c.querySelector('.cp-respuesta').value.trim();
    if (!respuesta) continue;
    if (pregunta.length < 3) return t.p3.preguntaCorta;
    preguntas.push({ tema: $c.dataset.tema, pregunta, otras_formas: $c.dataset.otras || null, respuesta });
  }
  const vistas = new Set();
  for (const p of preguntas) {
    if (vistas.has(normal(p.pregunta))) return t.p3.repetidas(p.pregunta);
    vistas.add(normal(p.pregunta));
  }
  if (preguntas.length < 3) return t.p3.faltanRespuestas(preguntas.length);
  datos.preguntas = preguntas;
  return '';
};

$form.addEventListener('submit', (e) => {
  e.preventDefault();
  const mensaje = validar[paso]?.() ?? '';
  if (mensaje) return mostrarError(mensaje);
  if (paso < 3) irA(paso + 1);
  if (paso === 3) prepararPreguntas();
});

$atras.addEventListener('click', () => irA(paso - 1));

pintarTextos();
irA(1);
