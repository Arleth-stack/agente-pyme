import { supabase } from './supabase.js';
import { textos } from './textos.js';

const t = textos.panel;
const $mensaje = document.getElementById('mensaje');
const $salir = document.getElementById('salir');
const $verChat = document.getElementById('ver-chat');

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

if (error) {
  $mensaje.textContent = t.sinConexion;
} else if (!negocios.length) {
  $mensaje.textContent = t.sinNegocio;
} else {
  const negocio = negocios[0];
  document.title = negocio.nombre;
  document.getElementById('nombre-negocio').textContent = negocio.nombre;
  $verChat.textContent = t.verChat;
  $verChat.href = `/chat/${negocio.slug}`;
  $verChat.hidden = false;
  $mensaje.textContent = '';
}
