-- T03: si no encuentra la respuesta entre las preguntas del negocio, no
-- inventa: le dice al cliente que alguien del equipo le contesta y deja un
-- aviso "no la sabe" para el dueño.

drop function public.chat_decidir(uuid, text);

create function public.chat_decidir(p_negocio uuid, p_texto text,
  out tipo text, out texto text, out pregunta_id uuid, out tema text, out motivo text)
language plpgsql stable set search_path = '' as $$
declare
  v_nombre text;
  v_norm text := public.normalizar(p_texto);
begin
  select n.nombre into v_nombre from public.negocios n where n.id = p_negocio;

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

revoke execute on function public.chat_decidir(uuid, text) from public, anon, authenticated;

create or replace function public.chat_enviar(p_token uuid, p_texto text) returns json
language plpgsql security definer set search_path = '' as $$
declare
  v_conv public.conversaciones%rowtype;
  v_texto text := btrim(coalesce(p_texto, ''));
  v_cliente public.mensajes%rowtype;
  v_resp public.mensajes%rowtype;
  v_aviso_nuevo boolean := false;
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
    -- Un solo aviso pendiente por conversación.
    insert into public.avisos (conversacion_id, motivo, mensaje_cliente)
    values (v_conv.id, d.motivo, v_texto)
    on conflict (conversacion_id) where estado = 'pendiente' do nothing;
    v_aviso_nuevo := found;
  end if;

  if d.tipo <> 'nada' then
    insert into public.mensajes (conversacion_id, autor, texto, pregunta_id)
    values (v_conv.id, 'asistente',
            case when d.tipo = 'aviso' and not v_aviso_nuevo
                 then 'Ya le avisé al equipo; te contestan en cuanto puedan.'
                 else d.texto end,
            d.pregunta_id)
    returning * into v_resp;
  end if;

  update public.conversaciones set
    ultimo_mensaje_en = now(),
    estado = case when d.tipo = 'aviso' then 'te_necesita' else estado end,
    interes = case
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
