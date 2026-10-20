import { supabase } from './supabase.js';
import { textos } from './textos.js';

const t = textos.entrar;
const $form = document.getElementById('formulario');
const $correo = document.getElementById('correo');
const $contrasena = document.getElementById('contrasena');
const $error = document.getElementById('error');
const $boton = document.getElementById('boton');

document.title = t.titulo;
document.getElementById('titulo').textContent = t.titulo;
document.getElementById('texto').textContent = t.texto;
document.getElementById('etiqueta-correo').textContent = t.correo;
document.getElementById('etiqueta-contrasena').textContent = t.contrasena;
$boton.textContent = t.boton;
document.getElementById('enlace-crear').textContent = t.crear;

// Si ya hay sesión, directo al panel.
const { data: { session } } = await supabase.auth.getSession();
if (session) location.replace('/panel');

function mostrarError(texto) {
  $error.textContent = texto;
  $error.hidden = !texto;
}

$form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const correo = $correo.value.trim();
  const contrasena = $contrasena.value;
  if (!correo || !contrasena) return mostrarError(t.faltanDatos);

  mostrarError('');
  $boton.disabled = true;
  $boton.textContent = t.entrando;

  const { error } = await supabase.auth.signInWithPassword({ email: correo, password: contrasena });
  if (!error) return location.replace('/panel');

  $boton.disabled = false;
  $boton.textContent = t.boton;
  // Sin respuesta del servicio = sin conexión; cualquier otro rechazo = datos equivocados.
  mostrarError(error.status ? t.incorrectos : t.sinConexion);
});
