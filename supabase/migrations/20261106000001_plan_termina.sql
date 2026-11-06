-- Si el dueño cancela desde la página de Stripe, su plan sigue hasta el fin
-- del periodo pagado (o de la prueba). Aquí se guarda esa fecha para que el
-- panel diga "Tu plan termina el …". Nulo = no ha cancelado.
alter table public.negocios add column plan_termina timestamptz;
