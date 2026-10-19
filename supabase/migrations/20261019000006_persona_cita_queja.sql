-- T04: reglas fijas que se revisan ANTES de buscar en las preguntas:
-- queja o urgencia, pide una persona y pide una cita con día u hora.
-- Si ya hay un aviso pendiente, no se crea otro; solo sube de importancia
-- (queja > cita > persona > no la sabe).

create function public.detectar_motivo(p_texto text) returns text
language sql stable set search_path = '' as $$
  with t as (select public.normalizar(p_texto) as n)
  select case
    -- Queja, dolor o algo que salió mal.
    when n ~ '\m(duele|dolor|sangra\w*|hinchad\w*|molest[ao]s?|enojad[ao]s?|queja\w*|reclam\w*|inconforme|pesimo|horrible|urgente)\M'
      or n ~ '\m(cobraron de mas|dejaron mal|quedo mal|quedo peor|salio mal|hicieron mal|me lastimaron)\M'
      then 'queja_o_urgencia'
    -- Quiere hablar con alguien.
    when n ~ '\m(hablar|comunicarme|comunicar|platicar|contactar|llamen|llamar|marquen)\M'
      or n ~ '^(con )?(una |un |el |la )?(persona|humano|alguien|asesor|asesora|encargado|encargada|duena|dueno)$'
      then 'pidio_persona'
    -- Pide una cita con día u hora concretos ("¿necesito cita?" no cuenta).
    when n ~ '\m(cita|citas|agendar|agendo|agenda|agendarme|apartar|aparto|reservar|reservo|turno|espacio|lugar|llevar|llevo|ir|pasar|paso|verme|ver|atender|atiendan|atienden)\M'
     and n ~ '(\m(lunes|martes|miercoles|jueves|viernes|sabado|domingo|hoy|manana|pasado manana)\M|\ma las \d|\m\d{1,2}( ?(am|pm|hrs|horas))\M|\men la (manana|tarde|noche)\M)'
      then 'pide_cita'
  end
  from t;
$$;

create function public.prioridad_motivo(m text) returns int
language sql immutable as $$
  select case m when 'queja_o_urgencia' then 4 when 'pide_cita' then 3
                when 'pidio_persona' then 2 when 'no_la_sabe' then 1 else 0 end;
$$;

create or replace function public.chat_decidir(p_negocio uuid, p_texto text,
  out tipo text, out texto text, out pregunta_id uuid, out tema text, out motivo text)
language plpgsql stable set search_path = '' as $$
declare
  v_nombre text;
  v_norm text := public.normalizar(p_texto);
begin
  select n.nombre into v_nombre from public.negocios n where n.id = p_negocio;

  motivo := public.detectar_motivo(p_texto);
  if motivo is not null then
    tipo := 'aviso';
    texto := case motivo
      when 'queja_o_urgencia' then 'Lamento mucho lo que pasó. Ya le avisé al equipo para que te atienda en cuanto pueda.'
      when 'pidio_persona' then 'Claro, ya le avisé a alguien del equipo para que te conteste. Te escribe en cuanto pueda.'
      when 'pide_cita' then '¡Con gusto! Ya le pasé tu solicitud al equipo para que te confirme el lugar. Te escriben en cuanto puedan.'
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
  texto := 'Esa te la contesta mejor alguien del equipo. Ya le avisé y te escribe en cuanto pueda.';
end $$;

create or replace function public.chat_enviar(p_token uuid, p_texto text) returns json
language plpgsql security definer set search_path = '' as $$
declare
  v_conv public.conversaciones%rowtype;
  v_texto text := btrim(coalesce(p_texto, ''));
  v_cliente public.mensajes%rowtype;
  v_resp public.mensajes%rowtype;
  v_ya_habia boolean := false;
  d record;
begin
  select * into v_conv from public.conversaciones where token = p_token;
  if v_conv.id is null then
    raise exception 'conversacion_no_existe';
  end if;
  if char_length(v_texto) < 1 or char_length(v_texto) > 1000 then
    raise exception 'texto_invalido';
  end if;

  insert into public.mensajes (conversacion_id, autor, texto)
  values (v_conv.id, 'cliente', v_texto)
  returning * into v_cliente;

  d := public.chat_decidir(v_conv.negocio_id, v_texto);

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
            -- Si ya había un aviso de "no la sabe", no se repite el mismo texto.
            case when d.tipo = 'aviso' and v_ya_habia and d.motivo = 'no_la_sabe'
                 then 'Ya le avisé al equipo; te contestan en cuanto puedan.'
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
    'tipo', d.tipo, 'motivo', d.motivo
  ))) end)::json;
end $$;

revoke execute on function public.detectar_motivo(text), public.prioridad_motivo(text)
  from public, anon, authenticated;
