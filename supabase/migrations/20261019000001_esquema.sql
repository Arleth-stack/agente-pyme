-- Esquema multiempresa (Modelo de datos v2).
-- Cada tabla lleva negocio_id y reglas por fila. El cliente del chat (anon)
-- no lee ninguna tabla: solo usa las funciones chat_*.

create extension if not exists unaccent with schema extensions;
create extension if not exists pg_trgm with schema extensions;

-- 1. negocios ---------------------------------------------------------------
create table public.negocios (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique check (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$' and char_length(slug) <= 70),
  nombre text not null check (char_length(btrim(nombre)) between 2 and 60),
  giro text not null check (giro in ('consultorio','salon','gimnasio','inmobiliaria','taller','otro')),
  telefono text not null check (telefono ~ '^[0-9]{10}$'),
  direccion text check (direccion is null or char_length(direccion) <= 120),
  zona_horaria text not null default 'America/Mexico_City',
  -- {"lun": {"abre": "09:00", "cierra": "19:00"}, "dom": null, ...}; null = cerrado
  horario jsonb not null,
  es_demo boolean not null default false,
  merkatics_org_id text,
  creado_en timestamptz not null default now()
);

-- 2. miembros ---------------------------------------------------------------
create table public.miembros (
  negocio_id uuid not null references public.negocios on delete cascade,
  usuario_id uuid not null references auth.users on delete cascade,
  rol text not null default 'dueno' check (rol in ('dueno','encargado')),
  creado_en timestamptz not null default now(),
  primary key (negocio_id, usuario_id)
);

-- 3. preguntas --------------------------------------------------------------
create table public.preguntas (
  id uuid primary key default gen_random_uuid(),
  negocio_id uuid not null references public.negocios on delete cascade,
  tema text not null check (tema in ('horarios','precios','servicios','citas','pagos','ubicacion','otros')),
  pregunta text not null check (char_length(btrim(pregunta)) between 3 and 150),
  otras_formas text check (otras_formas is null or char_length(otras_formas) <= 300),
  respuesta text not null check (char_length(btrim(respuesta)) between 1 and 500),
  activa boolean not null default true,
  orden int not null default 0,
  actualizado_en timestamptz not null default now()
);
create unique index preguntas_sin_repetir on public.preguntas (negocio_id, lower(btrim(pregunta)));

-- 4. conversaciones ---------------------------------------------------------
create table public.conversaciones (
  id uuid primary key default gen_random_uuid(),
  negocio_id uuid not null references public.negocios on delete cascade,
  token uuid not null unique default gen_random_uuid(),
  cliente_nombre text check (cliente_nombre is null or char_length(cliente_nombre) <= 60),
  cliente_telefono text check (cliente_telefono is null or cliente_telefono ~ '^[0-9]{10}$'),
  estado text not null default 'al_dia' check (estado in ('al_dia','te_necesita','la_atiendes_tu')),
  interes text check (interes in ('precio','cita','servicio','ubicacion','queja','otro')),
  resumen text check (resumen is null or char_length(resumen) <= 200),
  creada_en timestamptz not null default now(),
  ultimo_mensaje_en timestamptz not null default now()
);
create index conversaciones_por_negocio on public.conversaciones (negocio_id, ultimo_mensaje_en desc);

-- 5. mensajes ---------------------------------------------------------------
create table public.mensajes (
  id bigint generated always as identity primary key,
  negocio_id uuid not null references public.negocios on delete cascade,
  conversacion_id uuid not null references public.conversaciones on delete cascade,
  autor text not null check (autor in ('cliente','asistente','dueno')),
  texto text not null check (char_length(btrim(texto)) between 1 and 1000),
  pregunta_id uuid references public.preguntas on delete set null,
  creado_en timestamptz not null default now()
);
create index mensajes_por_conversacion on public.mensajes (conversacion_id, id);

-- 6. avisos -----------------------------------------------------------------
create table public.avisos (
  id uuid primary key default gen_random_uuid(),
  negocio_id uuid not null references public.negocios on delete cascade,
  conversacion_id uuid not null references public.conversaciones on delete cascade,
  motivo text not null check (motivo in ('no_la_sabe','pidio_persona','pide_cita','queja_o_urgencia')),
  mensaje_cliente text not null,
  estado text not null default 'pendiente' check (estado in ('pendiente','resuelto')),
  creado_en timestamptz not null default now(),
  resuelto_en timestamptz
);
-- Un solo aviso pendiente por conversación.
create unique index un_aviso_pendiente on public.avisos (conversacion_id) where estado = 'pendiente';

-- El negocio_id de mensajes y avisos siempre es el de su conversación.
create function public.copiar_negocio_de_conversacion() returns trigger
language plpgsql set search_path = '' as $$
begin
  select c.negocio_id into new.negocio_id
  from public.conversaciones c where c.id = new.conversacion_id;
  return new;
end $$;

create trigger mensajes_negocio before insert on public.mensajes
  for each row execute function public.copiar_negocio_de_conversacion();
create trigger avisos_negocio before insert on public.avisos
  for each row execute function public.copiar_negocio_de_conversacion();

-- Reglas por fila -----------------------------------------------------------
create function public.es_miembro(n uuid) returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (
    select 1 from public.miembros m
    where m.negocio_id = n and m.usuario_id = (select auth.uid())
  );
$$;

alter table public.negocios enable row level security;
alter table public.miembros enable row level security;
alter table public.preguntas enable row level security;
alter table public.conversaciones enable row level security;
alter table public.mensajes enable row level security;
alter table public.avisos enable row level security;

create policy ver_mi_negocio on public.negocios
  for select to authenticated using (public.es_miembro(id));
create policy editar_mi_negocio on public.negocios
  for update to authenticated using (public.es_miembro(id)) with check (public.es_miembro(id));

create policy ver_mis_membresias on public.miembros
  for select to authenticated using (usuario_id = (select auth.uid()));

create policy solo_mi_negocio on public.preguntas
  for all to authenticated using (public.es_miembro(negocio_id)) with check (public.es_miembro(negocio_id));
create policy solo_mi_negocio on public.conversaciones
  for all to authenticated using (public.es_miembro(negocio_id)) with check (public.es_miembro(negocio_id));
create policy solo_mi_negocio on public.mensajes
  for all to authenticated using (public.es_miembro(negocio_id)) with check (public.es_miembro(negocio_id));
create policy solo_mi_negocio on public.avisos
  for all to authenticated using (public.es_miembro(negocio_id)) with check (public.es_miembro(negocio_id));

-- El cliente sin sesión no toca tablas, ni siquiera con reglas.
revoke all on public.negocios, public.miembros, public.preguntas,
  public.conversaciones, public.mensajes, public.avisos from anon;
revoke execute on function public.es_miembro(uuid) from anon, public;
grant execute on function public.es_miembro(uuid) to authenticated;
