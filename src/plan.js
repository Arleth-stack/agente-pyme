// Prueba gratis y plan mensual: habla con las funciones de Vercel (/api/…),
// que son las únicas que tienen las llaves de Stripe.
import { supabase } from './supabase.js';

async function llamar(ruta, cuerpo = {}) {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) throw new Error('sin_sesion');
  const r = await fetch(ruta, {
    method: 'POST',
    headers: { authorization: `Bearer ${session.access_token}`, 'content-type': 'application/json' },
    body: JSON.stringify(cuerpo),
  });
  if (!r.ok) throw new Error(`plan ${r.status}`);
  return r.json();
}

// Lleva al dueño a la página segura de Stripe para registrar su tarjeta.
export async function abrirPago() {
  const { url } = await llamar('/api/prueba');
  if (!url) throw new Error('sin_url');
  location.assign(url);
}

// Estado del plan confirmado con Stripe. `s` = id del pago al volver de Stripe.
export const leerPlan = (s) => llamar('/api/plan', s ? { s } : {});

export function diasRestantes(iso) {
  return Math.max(1, Math.ceil((new Date(iso) - Date.now()) / 86400000));
}
