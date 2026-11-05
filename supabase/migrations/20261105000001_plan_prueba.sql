-- Prueba gratis de 7 días y plan mensual (pedido de Carlos, 5 nov 2026).
-- El cobro lo hace Stripe; aquí solo se guarda en qué va cada negocio.
-- El dueño puede LEER estas columnas (reglas por fila de negocios), pero no
-- cambiarlas: solo tiene permiso de editar nombre, teléfono, dirección y
-- horario. Las escriben las funciones de Vercel con la llave secreta.

alter table public.negocios
  add column plan_estado text not null default 'sin_activar'
    check (plan_estado in ('sin_activar', 'prueba', 'activa', 'pago_pendiente', 'cancelada')),
  add column prueba_termina timestamptz,
  add column stripe_cliente text,
  add column stripe_suscripcion text unique,
  add column plan_actualizado timestamptz;

comment on column public.negocios.plan_estado is
  'sin_activar: no ha registrado tarjeta · prueba: 7 días gratis · activa: ya pagó · pago_pendiente: no se pudo cobrar · cancelada';
