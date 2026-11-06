// POST /api/portal → abre la página segura de Stripe donde el dueño cambia su
// tarjeta, ve sus cobros o cancela su plan. Al terminar vuelve a su panel.
import { json, stripe, negocioDeSesion, PORTAL_ID } from './_lib.js';

export async function POST(request) {
  const sesion = await negocioDeSesion(request);
  if (!sesion) return json({ error: 'sin_sesion' }, 401);
  const { negocio } = sesion;
  if (negocio.es_demo || !negocio.stripe_cliente) return json({ error: 'sin_tarjeta' }, 400);

  try {
    const portal = await stripe('billing_portal/sessions', {
      metodo: 'POST',
      datos: {
        customer: negocio.stripe_cliente,
        locale: 'es-419',
        return_url: `${new URL(request.url).origin}/panel?plan=volvio`,
        ...(PORTAL_ID ? { configuration: PORTAL_ID } : {}),
      },
    });
    return json({ url: portal.url });
  } catch (e) {
    console.error(e);
    return json({ error: 'stripe' }, 502);
  }
}
