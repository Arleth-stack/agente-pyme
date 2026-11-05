// Ayudantes compartidos de las funciones de Vercel (el guion bajo hace que
// Vercel NO lo publique como dirección). Las llaves secretas viven solo en
// las variables de entorno de Vercel; nunca llegan a la página.

const SB_URL = process.env.VITE_SUPABASE_URL;
const SB_SECRETA = process.env.SUPABASE_SECRET_KEY;
const STRIPE_SECRETA = process.env.STRIPE_SECRET_KEY;
export const PRECIO_ID = process.env.STRIPE_PRICE_ID;
export const DIAS_PRUEBA = 7;

export const json = (datos, status = 200) => new Response(JSON.stringify(datos), {
  status,
  headers: { 'content-type': 'application/json', 'cache-control': 'no-store' },
});

// --- Stripe (llamadas directas, sin librerías) ------------------------------

function aFormulario(obj, prefijo = '', partes = []) {
  for (const [k, v] of Object.entries(obj)) {
    if (v === undefined || v === null) continue;
    const llave = prefijo ? `${prefijo}[${k}]` : k;
    if (typeof v === 'object') aFormulario(v, llave, partes);
    else partes.push(`${encodeURIComponent(llave)}=${encodeURIComponent(v)}`);
  }
  return partes;
}

export async function stripe(ruta, { metodo = 'GET', datos } = {}) {
  const r = await fetch(`https://api.stripe.com/v1/${ruta}`, {
    method: metodo,
    headers: {
      authorization: `Bearer ${STRIPE_SECRETA}`,
      'content-type': 'application/x-www-form-urlencoded',
    },
    body: datos ? aFormulario(datos).join('&') : undefined,
  });
  const cuerpo = await r.json();
  if (!r.ok) throw new Error(`stripe ${ruta}: ${cuerpo.error?.message ?? r.status}`);
  return cuerpo;
}

// --- Supabase con la llave secreta (salta las reglas por fila: usar con cuidado)

async function sb(ruta, { metodo = 'GET', datos, token } = {}) {
  const r = await fetch(`${SB_URL}${ruta}`, {
    method: metodo,
    headers: {
      apikey: SB_SECRETA,
      ...(token ? { authorization: `Bearer ${token}` } : {}),
      'content-type': 'application/json',
      prefer: 'return=representation',
    },
    body: datos ? JSON.stringify(datos) : undefined,
  });
  if (!r.ok) throw new Error(`supabase ${ruta}: ${r.status} ${await r.text()}`);
  return r.status === 204 ? null : r.json();
}

const COLUMNAS = 'id,slug,nombre,es_demo,plan_estado,prueba_termina,stripe_cliente,stripe_suscripcion';

// Quién hace la petición: se valida su sesión con Supabase y se busca SU negocio.
export async function negocioDeSesion(request) {
  const token = (request.headers.get('authorization') ?? '').replace(/^Bearer\s+/i, '');
  if (!token) return null;
  let usuario;
  try {
    usuario = await sb('/auth/v1/user', { token });
  } catch (e) {
    console.error(e.message);
    return null;
  }
  if (!usuario?.id) return null;
  const filas = await sb(`/rest/v1/miembros?usuario_id=eq.${usuario.id}&select=negocios(${COLUMNAS})&limit=1`);
  const negocio = filas?.[0]?.negocios;
  return negocio ? { negocio, correo: usuario.email } : null;
}

// Estado de Stripe → estado que entiende el panel.
export function estadoDe(suscripcion) {
  switch (suscripcion.status) {
    case 'trialing': return 'prueba';
    case 'active': return 'activa';
    case 'past_due':
    case 'unpaid':
    case 'incomplete': return 'pago_pendiente';
    default: return 'cancelada';
  }
}

// Guarda en la base lo que dice Stripe. Si el negocio ya tiene OTRA suscripción
// más nueva, un aviso viejo (por ejemplo, la cancelación de la anterior) no la pisa.
export async function guardarPlan(negocioId, suscripcion) {
  const estado = estadoDe(suscripcion);
  const vigente = estado === 'prueba' || estado === 'activa';
  const filtro = vigente
    ? `id=eq.${negocioId}`
    : `id=eq.${negocioId}&or=(stripe_suscripcion.is.null,stripe_suscripcion.eq.${suscripcion.id})`;
  const filas = await sb(`/rest/v1/negocios?${filtro}&select=${COLUMNAS}`, {
    metodo: 'PATCH',
    datos: {
      plan_estado: estado,
      prueba_termina: suscripcion.trial_end ? new Date(suscripcion.trial_end * 1000).toISOString() : null,
      stripe_cliente: typeof suscripcion.customer === 'string' ? suscripcion.customer : suscripcion.customer?.id,
      stripe_suscripcion: suscripcion.id,
      plan_actualizado: new Date().toISOString(),
    },
  });
  return filas?.[0] ?? null;
}

export const resumenPlan = (n) => ({
  es_demo: n.es_demo,
  estado: n.plan_estado,
  prueba_termina: n.prueba_termina,
  // La prueba gratis se da una sola vez por negocio.
  puede_probar: !n.stripe_suscripcion,
});
