// POST /api/prueba → abre la página segura de Stripe para registrar la tarjeta.
// Primera vez: 7 días gratis y al día 7 se cobra el primer mes.
// Si ya usó su prueba (por ejemplo, la canceló), se cobra desde hoy.
import { json, stripe, negocioDeSesion, PRECIO_ID, DIAS_PRUEBA } from './_lib.js';

export async function POST(request) {
  const sesion = await negocioDeSesion(request);
  if (!sesion) return json({ error: 'sin_sesion' }, 401);
  const { negocio, correo } = sesion;

  if (negocio.es_demo) return json({ error: 'demo' }, 400);
  if (negocio.plan_estado === 'prueba' || negocio.plan_estado === 'activa') {
    return json({ url: '/panel' });
  }

  const origen = new URL(request.url).origin;
  const primeraVez = !negocio.stripe_suscripcion;
  try {
    const pago = await stripe('checkout/sessions', {
      metodo: 'POST',
      datos: {
        mode: 'subscription',
        locale: 'es-419',
        client_reference_id: negocio.id,
        ...(negocio.stripe_cliente ? { customer: negocio.stripe_cliente } : { customer_email: correo }),
        line_items: { 0: { price: PRECIO_ID, quantity: 1 } },
        payment_method_collection: 'always',
        metadata: { negocio_id: negocio.id },
        subscription_data: {
          metadata: { negocio_id: negocio.id, negocio: negocio.slug },
          ...(primeraVez ? { trial_period_days: DIAS_PRUEBA } : {}),
        },
        success_url: `${origen}/panel?plan=listo&s={CHECKOUT_SESSION_ID}`,
        cancel_url: `${origen}/panel?plan=cancelado`,
      },
    });
    return json({ url: pago.url });
  } catch (e) {
    console.error(e);
    return json({ error: 'stripe' }, 502);
  }
}
