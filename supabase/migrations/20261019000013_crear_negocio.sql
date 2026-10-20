-- T13: alta de un negocio desde el formulario. Una sola función crea el
-- negocio, la membresía de dueño y sus preguntas: o se guarda todo o nada.
-- Si la cuenta ya tiene un negocio (por ejemplo, se reintentó porque se
-- perdió la respuesta), regresa ese negocio en lugar de crear otro.

create function public.horario_valido(h jsonb) returns boolean
language sql immutable as $$
  select jsonb_typeof(h) = 'object'
     and (select count(*) from jsonb_object_keys(h) k
          where k not in ('lun','mar','mie','jue','vie','sab','dom')) = 0
     and (select bool_and(
            jsonb_typeof(v) = 'null'
            or (jsonb_typeof(v) = 'object'
                and (v ->> 'abre') ~ '^\d{2}:\d{2}$' and (v ->> 'cierra') ~ '^\d{2}:\d{2}$'
                and (v ->> 'abre')::time < (v ->> 'cierra')::time))
          from jsonb_each(h) as e(k, v))
     and exists (select 1 from jsonb_each(h) as e(k, v) where jsonb_typeof(v) = 'object');
$$;

create function public.crear_negocio(p_datos jsonb) returns json
language plpgsql security definer set search_path = '' as $$
declare
  v_uid uuid := auth.uid();
  v_nombre text := btrim(coalesce(p_datos ->> 'nombre', ''));
  v_giro text := p_datos ->> 'giro';
  v_telefono text := regexp_replace(coalesce(p_datos ->> 'telefono', ''), '\D', '', 'g');
  v_direccion text := nullif(btrim(coalesce(p_datos ->> 'direccion', '')), '');
  v_horario jsonb := p_datos -> 'horario';
  v_preguntas jsonb := coalesce(p_datos -> 'preguntas', '[]'::jsonb);
  v_existente record;
  v_base text;
  v_slug text;
  v_id uuid;
  v_n int := 1;
  p jsonb;
  i int := 0;
begin
  if v_uid is null then
    raise exception 'sin_sesion';
  end if;

  -- Un alta a la vez por cuenta (doble clic o reintento).
  perform pg_advisory_xact_lock(hashtext(v_uid::text));

  select n.slug, n.nombre into v_existente
  from public.miembros m join public.negocios n on n.id = m.negocio_id
  where m.usuario_id = v_uid limit 1;
  if found then
    return json_build_object('slug', v_existente.slug, 'nombre', v_existente.nombre, 'ya_existia', true);
  end if;

  -- Validaciones (las mismas que el formulario; aquí no se puede saltar).
  if char_length(v_nombre) not between 2 and 60 then raise exception 'datos_invalidos:nombre'; end if;
  if v_giro is null or v_giro not in ('consultorio','salon','gimnasio','inmobiliaria','taller','otro') then
    raise exception 'datos_invalidos:giro';
  end if;
  if v_telefono !~ '^[0-9]{10}$' then raise exception 'datos_invalidos:telefono'; end if;
  if char_length(coalesce(v_direccion, '')) > 120 then raise exception 'datos_invalidos:direccion'; end if;
  if not coalesce(public.horario_valido(v_horario), false) then raise exception 'datos_invalidos:horario'; end if;
  if jsonb_typeof(v_preguntas) <> 'array' or jsonb_array_length(v_preguntas) < 3 or jsonb_array_length(v_preguntas) > 60 then
    raise exception 'datos_invalidos:preguntas';
  end if;

  -- Enlace del chat a partir del nombre: "Salón Bella" → salon-bella (sin repetir).
  v_base := left(regexp_replace(public.normalizar(v_nombre), ' ', '-', 'g'), 60);
  v_base := btrim(v_base, '-');
  if v_base = '' then v_base := 'negocio'; end if;
  v_slug := v_base;
  while exists (select 1 from public.negocios where slug = v_slug) loop
    v_n := v_n + 1;
    v_slug := v_base || '-' || v_n;
  end loop;

  insert into public.negocios (slug, nombre, giro, telefono, direccion, horario)
  values (v_slug, v_nombre, v_giro, v_telefono, v_direccion, v_horario)
  returning id into v_id;

  insert into public.miembros (negocio_id, usuario_id, rol) values (v_id, v_uid, 'dueno');

  begin
    for p in select * from jsonb_array_elements(v_preguntas) loop
      i := i + 1;
      insert into public.preguntas (negocio_id, orden, tema, pregunta, otras_formas, respuesta)
      values (v_id, i,
              coalesce(p ->> 'tema', 'otros'),
              btrim(p ->> 'pregunta'),
              nullif(btrim(coalesce(p ->> 'otras_formas', '')), ''),
              btrim(p ->> 'respuesta'));
    end loop;
  exception
    when unique_violation then raise exception 'preguntas_repetidas';
    when check_violation or not_null_violation then raise exception 'datos_invalidos:preguntas';
  end;

  return json_build_object('slug', v_slug, 'nombre', v_nombre, 'ya_existia', false);
end $$;

revoke execute on function public.horario_valido(jsonb) from public, anon, authenticated;
revoke execute on function public.crear_negocio(jsonb) from public, anon;
grant execute on function public.crear_negocio(jsonb) to authenticated;
