// POST /api/stripe-aviso → Stripe avisa aquí cada cambio de una suscripción
// (empezó la prueba, se cobró el mes, falló el cobro, se canceló) y se guarda
// en la base aunque el dueño no abra su panel. Solo se acepta si la firma
// demuestra que el aviso viene de Stripe.
import { createHmac, timingSafeEqual } from 'node:crypto';
import { json, guardarPlan } from './_lib.js';

const SECRETO = process.env.STRIPE_WEBHOOK_SECRET;
const TOLERANCIA_S = 300;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;

function firmaValida(cuerpo, encabezado) {
  if (!SECRETO || !encabezado) return false;
  const partes = encabezado.split(',').map((p) => p.split('='));
  const t = partes.find(([k]) => k === 't')?.[1];
  const firmas = partes.filter(([k]) => k === 'v1').map(([, v]) => v);
  if (!t || !firmas.length || Math.abs(Date.now() / 1000 - Number(t)) > TOLERANCIA_S) return false;
  const esperada = Buffer.from(createHmac('sha256', SECRETO).update(`${t}.${cuerpo}`).digest('hex'));
  return firmas.some((f) => f.length === esperada.length && timingSafeEqual(Buffer.from(f), esperada));
}

export async function POST(request) {
  const cuerpo = await request.text();
  if (!firmaValida(cuerpo, request.headers.get('stripe-signature'))) {
    return json({ error: 'firma' }, 400);
  }
  const evento = JSON.parse(cuerpo);
  if (!evento.type?.startsWith('customer.subscription.')) return json({ ok: true });

  const suscripcion = evento.data.object;
  const negocioId = suscripcion.metadata?.negocio_id;
  if (!UUID.test(negocioId ?? '')) return json({ ok: true, ignorado: 'sin negocio' });

  try {
    await guardarPlan(negocioId, suscripcion);
  } catch (e) {
    console.error(e);
    // 500 → Stripe lo vuelve a intentar más tarde.
    return json({ error: 'base' }, 500);
  }
  return json({ ok: true });
}
