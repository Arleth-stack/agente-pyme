-- T05: abierto o cerrado según el horario y la zona del negocio.
-- El encabezado del chat lo muestra, "¿están abiertos?" se contesta con él
-- y, fuera de horario, los avisos dicen cuándo le escriben al cliente.
-- La hora simulada (para la demo) solo aplica a los negocios demo.

create function public.dia_clave(dow int) returns text
language sql immutable as $$
  select (array['dom','lun','mar','mie','jue','vie','sab'])[dow + 1];
$$;

create function public.dia_nombre(dow int) returns text
language sql immutable as $$
  select (array['domingo','lunes','martes','miércoles','jueves','viernes','sábado'])[dow + 1];
$$;

-- 10:00 → "las 10:00 a. m."; 13:00 → "la 1:00 p. m."
create function public.las(h time) returns text
language sql immutable as $$
  select case when to_char(h, 'FMHH12') = '1' then 'la ' else 'las ' end
      || to_char(h, 'FMHH12:MI') || case when h < '12:00' then ' a. m.' else ' p. m.' end;
$$;

-- abierto; si está abierto, a qué hora cierra; si no, qué día y a qué hora abre
-- (dia: 'hoy', 'mañana' o 'el martes'; null si nunca abre).
create function public.estado_horario(p_negocio uuid, p_momento timestamptz,
  out abierto boolean, out cierra time, out dia text, out abre time)
language plpgsql stable set search_path = '' as $$
declare
  v_horario jsonb;
  v_local timestamp;
  v_dow int;
  v_hoy jsonb;
  v_otro jsonb;
  i int;
begin
  select n.horario, p_momento at time zone n.zona_horaria into v_horario, v_local
  from public.negocios n where n.id = p_negocio;

  v_dow := extract(dow from v_local);
  v_hoy := v_horario -> public.dia_clave(v_dow);
  abierto := false;

  if jsonb_typeof(v_hoy) = 'object' then
    if v_local::time >= (v_hoy ->> 'abre')::time and v_local::time < (v_hoy ->> 'cierra')::time then
      abierto := true;
      cierra := (v_hoy ->> 'cierra')::time;
      return;
    end if;
    if v_local::time < (v_hoy ->> 'abre')::time then
      dia := 'hoy';
      abre := (v_hoy ->> 'abre')::time;
      return;
    end if;
  end if;

  for i in 1..7 loop
    v_otro := v_horario -> public.dia_clave((v_dow + i) % 7);
    if jsonb_typeof(v_otro) = 'object' then
      dia := case i when 1 then 'mañana' else 'el ' || public.dia_nombre((v_dow + i) % 7) end;
      abre := (v_otro ->> 'abre')::time;
      return;
    end if;
  end loop;
end $$;

-- Momento a usar: la hora simulada solo vale en negocios demo.
create function public.momento(p_negocio uuid, p_hora timestamptz) returns timestamptz
language sql stable set search_path = '' as $$
  select case when p_hora is not null and n.es_demo then p_hora else now() end
  from public.negocios n where n.id = p_negocio;
$$;

-- Encabezado del chat: "Abierto · cierra a las 8:00 p. m." / "Cerrado · abre mañana a las 10:00 a. m."
create function public.texto_estado(abierto boolean, cierra time, dia text, abre time) returns text
language sql immutable as $$
  select case
    when abierto then 'Abierto · cierra a ' || public.las(cierra)
    when dia is null then 'Cerrado'
    else 'Cerrado · abre ' || dia || ' a ' || public.las(abre)
  end;
$$;

-- Cuándo le contestan al cliente después de un aviso.
create function public.texto_cuando(abierto boolean, dia text, abre time) returns text
language sql immutable as $$
  select case
    when abierto or dia is null then 'Te escriben en cuanto puedan.'
    else 'Ahorita estamos cerrados; te escriben ' || dia || ' a partir de ' || public.las(abre) || '.'
  end;
$$;

drop function public.chat_negocio(text);

create function public.chat_negocio(p_slug text, p_hora timestamptz default null) returns json
language plpgsql stable security definer set search_path = '' as $$
declare
  v_neg public.negocios%rowtype;
  h record;
begin
  select * into v_neg from public.negocios where slug = p_slug;
  if v_neg.id is null then
    return null;
  end if;
  h := public.estado_horario(v_neg.id, public.momento(v_neg.id, p_hora));
  return json_build_object(
    'nombre', v_neg.nombre,
    'giro', v_neg.giro,
    'abierto', h.abierto,
    'estado', public.texto_estado(h.abierto, h.cierra, h.dia, h.abre)
  );
end $$;

drop function public.chat_decidir(uuid, text);

create function public.chat_decidir(p_negocio uuid, p_texto text, p_momento timestamptz,
  out tipo text, out texto text, out pregunta_id uuid, out tema text, out motivo text, out abierto boolean)
language plpgsql stable set search_path = '' as $$
declare
  v_nombre text;
  v_norm text := public.normalizar(p_texto);
  h record;
  v_cuando text;
begin
  select n.nombre into v_nombre from public.negocios n where n.id = p_negocio;
  h := public.estado_horario(p_negocio, p_momento);
  v_cuando := public.texto_cuando(h.abierto, h.dia, h.abre);

  motivo := public.detectar_motivo(p_texto);
  if motivo is not null then
    tipo := 'aviso';
    texto := case motivo
      when 'queja_o_urgencia' then 'Lamento mucho lo que pasó. Ya le avisé al equipo. '
      when 'pidio_persona' then 'Claro, ya le avisé a alguien del equipo para que te conteste. '
      when 'pide_cita' then '¡Con gusto! Ya le pasé tu solicitud al equipo para que te confirme el lugar. '
    end || v_cuando;
    return;
  end if;

  -- "¿Están abiertos?", "¿a qué hora cierran hoy?"
  if v_norm ~ '\m(abiert[oa]s?|atendiendo|ya abrieron)\M' or v_norm ~ '\m(abren|cierran|atienden) hoy\M' then
    tipo := 'horario';
    abierto := h.abierto;
    texto := case
      when h.abierto then 'Sí, ahorita estamos abiertos. Hoy cerramos a ' || public.las(h.cierra) || '.'
      when h.dia is null then 'Ahorita estamos cerrados.'
      else 'Ahorita estamos cerrados. Abrimos ' || h.dia || ' a ' || public.las(h.abre) || '.'
    end;
    return;
  end if;

  if public.es_saludo(p_texto) then
    tipo := 'saludo';
    texto := case
      when v_norm ~ '(gracias|adios|bye|luego|gusto|amable)'
        then '¡Con gusto! Aquí estoy si necesitas algo más.'
      else format('¡Hola! ¿En qué te puedo ayudar? Te doy precios, horarios y más información de %s.', v_nombre)
    end;
    return;
  end if;

  select q.id, q.respuesta, q.tema into pregunta_id, texto, tema
  from public.buscar_pregunta(p_negocio, p_texto) b
  join public.preguntas q on q.id = b.pregunta_id;

  if pregunta_id is not null then
    tipo := 'faq';
    return;
  end if;

  tipo := 'aviso';
  motivo := 'no_la_sabe';
  texto := 'Esa te la contesta mejor alguien del equipo. Ya le avisé. ' || v_cuando;
end $$;

drop function public.chat_enviar(uuid, text);

create function public.chat_enviar(p_token uuid, p_texto text, p_hora timestamptz default null) returns json
language plpgsql security definer set search_path = '' as $$
declare
  v_conv public.conversaciones%rowtype;
  v_texto text := btrim(coalesce(p_texto, ''));
  v_momento timestamptz;
  v_cliente public.mensajes%rowtype;
  v_resp public.mensajes%rowtype;
  v_ya_habia boolean := false;
  d record;
  h record;
begin
  select * into v_conv from public.conversaciones where token = p_token;
  if v_conv.id is null then
    raise exception 'conversacion_no_existe';
  end if;
  if char_length(v_texto) < 1 or char_length(v_texto) > 1000 then
    raise exception 'texto_invalido';
  end if;
  v_momento := public.momento(v_conv.negocio_id, p_hora);

  insert into public.mensajes (conversacion_id, autor, texto)
  values (v_conv.id, 'cliente', v_texto)
  returning * into v_cliente;

  d := public.chat_decidir(v_conv.negocio_id, v_texto, v_momento);
  h := public.estado_horario(v_conv.negocio_id, v_momento);

  if d.tipo = 'aviso' then
    select exists (select 1 from public.avisos
                   where conversacion_id = v_conv.id and estado = 'pendiente') into v_ya_habia;

    insert into public.avisos (conversacion_id, motivo, mensaje_cliente)
    values (v_conv.id, d.motivo, v_texto)
    on conflict (conversacion_id) where estado = 'pendiente'
    do update set motivo = excluded.motivo, mensaje_cliente = excluded.mensaje_cliente
      where public.prioridad_motivo(excluded.motivo) > public.prioridad_motivo(public.avisos.motivo);
  end if;

  if d.tipo <> 'nada' then
    insert into public.mensajes (conversacion_id, autor, texto, pregunta_id)
    values (v_conv.id, 'asistente',
            -- Si ya había un aviso de "no la sabe", no se repite la explicación completa.
            case when d.tipo = 'aviso' and v_ya_habia and d.motivo = 'no_la_sabe'
                 then 'Ya le avisé al equipo. ' || public.texto_cuando(h.abierto, h.dia, h.abre)
                 else d.texto end,
            d.pregunta_id)
    returning * into v_resp;
  end if;

  update public.conversaciones set
    ultimo_mensaje_en = now(),
    estado = case when d.tipo = 'aviso' then 'te_necesita' else estado end,
    interes = case
      when d.motivo = 'queja_o_urgencia' then 'queja'
      when d.motivo = 'pide_cita' then 'cita'
      when d.tema = 'precios' then 'precio' when d.tema = 'citas' then 'cita'
      when d.tema = 'servicios' then 'servicio' when d.tema = 'ubicacion' then 'ubicacion'
      when d.tema is not null then 'otro'
      else interes end
  where id = v_conv.id;

  return (jsonb_build_array(
    jsonb_build_object('id', v_cliente.id, 'autor', 'cliente', 'texto', v_cliente.texto, 'creado_en', v_cliente.creado_en)
  ) || case when v_resp.id is null then '[]'::jsonb else jsonb_build_array(jsonb_strip_nulls(jsonb_build_object(
    'id', v_resp.id, 'autor', 'asistente', 'texto', v_resp.texto, 'creado_en', v_resp.creado_en,
    'tipo', d.tipo, 'motivo', d.motivo, 'abierto', d.abierto
  ))) end)::json;
end $$;

revoke execute on function public.chat_negocio(text, timestamptz), public.chat_enviar(uuid, text, timestamptz) from public;
grant execute on function public.chat_negocio(text, timestamptz), public.chat_enviar(uuid, text, timestamptz) to anon, authenticated;

revoke execute on function public.dia_clave(int), public.dia_nombre(int), public.las(time),
  public.estado_horario(uuid, timestamptz), public.momento(uuid, timestamptz),
  public.texto_estado(boolean, time, text, time), public.texto_cuando(boolean, text, time),
  public.chat_decidir(uuid, text, timestamptz) from public, anon, authenticated;
