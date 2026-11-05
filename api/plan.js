// POST /api/plan → estado del plan del negocio de quien pregunta.
// Si viene de regreso de Stripe ({ s: id del pago }), confirma ese pago con
// Stripe y lo guarda. Si no, vuelve a preguntarle a Stripe por su suscripción
// para que el panel nunca muestre algo distinto a lo que Stripe tiene.
import { json, stripe, negocioDeSesion, guardarPlan, resumenPlan } from './_lib.js';

export async function POST(request) {
  const sesion = await negocioDeSesion(request);
  if (!sesion) return json({ error: 'sin_sesion' }, 401);
  let { negocio } = sesion;
  if (negocio.es_demo) return json(resumenPlan(negocio));

  let cuerpo = {};
  try { cuerpo = await request.json(); } catch { /* sin cuerpo */ }

  try {
    let suscripcion = null;
    if (typeof cuerpo.s === 'string' && /^cs_[A-Za-z0-9_]+$/.test(cuerpo.s)) {
      const pago = await stripe(`checkout/sessions/${cuerpo.s}?expand[]=subscription`);
      // Solo cuenta si ese pago es de ESTE negocio.
      if (pago.client_reference_id === negocio.id && pago.subscription?.id) suscripcion = pago.subscription;
    } else if (negocio.stripe_suscripcion) {
      suscripcion = await stripe(`subscriptions/${negocio.stripe_suscripcion}`);
    }
    if (suscripcion) negocio = (await guardarPlan(negocio.id, suscripcion)) ?? negocio;
  } catch (e) {
    // Si Stripe no responde, se muestra lo último guardado en la base.
    console.error(e);
  }
  return json(resumenPlan(negocio));
}
