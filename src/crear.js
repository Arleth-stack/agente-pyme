import { textos } from './textos.js';
import { crearEditorHorario } from './horario.js';

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
const datos = { nombre: '', giro: '', telefono: '', direccion: '', horario: null };
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

$form.addEventListener('submit', (e) => {
  e.preventDefault();
  const mensaje = validar[paso]?.() ?? '';
  if (mensaje) return mostrarError(mensaje);
  if (paso < 2) irA(paso + 1);
});

$atras.addEventListener('click', () => irA(paso - 1));

pintarTextos();
irA(1);
