import { supabase } from './supabase.js';
import { textos } from './textos.js';

const t = textos.inicio;
const texto = (id, valor) => { document.getElementById(id).textContent = valor; };

texto('titulo', t.titulo);
texto('texto', t.texto);
texto('boton-crear', t.crear);
texto('boton-entrar', t.entrar);
texto('como-funciona', t.comoFunciona);
texto('ejemplos', t.ejemplos);

document.getElementById('beneficios').replaceChildren(...t.beneficios.map(([titulo, detalle]) => {
  const $b = document.createElement('article');
  $b.className = 'beneficio';
  const $h = document.createElement('h3');
  $h.textContent = titulo;
  const $p = document.createElement('p');
  $p.textContent = detalle;
  $b.append($h, $p);
  return $b;
}));

document.getElementById('pasos').replaceChildren(...t.pasos.map((paso) => {
  const $li = document.createElement('li');
  $li.textContent = paso;
  return $li;
}));

// Los chats de ejemplo salen de la base (los negocios demo).
const { data } = await supabase.rpc('negocios_demo');
document.getElementById('lista-negocios').replaceChildren(...(data ?? []).map((n) => {
  const $li = document.createElement('li');
  const $a = document.createElement('a');
  $a.href = `/chat/${n.slug}`;
  $a.textContent = n.nombre;
  $li.append($a);
  return $li;
}));
