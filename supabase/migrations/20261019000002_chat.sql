-- Funciones del chat del cliente (T01). Son las únicas puertas que tiene
-- alguien sin sesión: trabajan solo con el negocio del enlace y con la
-- conversación de su token. Nunca regresan datos de otro negocio.

-- Datos públicos del negocio del enlace.
create function public.chat_negocio(p_slug text) returns json
language sql stable security definer set search_path = '' as $$
  select json_build_object(
    'nombre', n.nombre,
    'giro', n.giro,
    'horario', n.horario,
    'zona_horaria', n.zona_horaria
  )
  from public.negocios n
  where n.slug = p_slug;
$$;

-- Abre una conversación nueva y regresa su token secreto.
create function public.chat_iniciar(p_slug text) returns uuid
language plpgsql security definer set search_path = '' as $$
declare
  v_negocio uuid;
  v_token uuid;
begin
  select id into v_negocio from public.negocios where slug = p_slug;
  if v_negocio is null then
    raise exception 'negocio_no_existe';
  end if;

  insert into public.conversaciones (negocio_id)
  values (v_negocio)
  returning token into v_token;

  return v_token;
end $$;

-- Mensajes de la conversación del token (después del id indicado).
create function public.chat_mensajes(p_token uuid, p_despues_de bigint default 0) returns json
language sql stable security definer set search_path = '' as $$
  select coalesce(json_agg(json_build_object(
           'id', m.id, 'autor', m.autor, 'texto', m.texto, 'creado_en', m.creado_en
         ) order by m.id), '[]'::json)
  from public.mensajes m
  join public.conversaciones c on c.id = m.conversacion_id
  where c.token = p_token and m.id > p_despues_de;
$$;

-- Guarda el mensaje del cliente. En T01 todavía no contesta.
create function public.chat_enviar(p_token uuid, p_texto text) returns json
language plpgsql security definer set search_path = '' as $$
declare
  v_conversacion uuid;
  v_texto text := btrim(coalesce(p_texto, ''));
  v_id bigint;
begin
  select id into v_conversacion from public.conversaciones where token = p_token;
  if v_conversacion is null then
    raise exception 'conversacion_no_existe';
  end if;
  if char_length(v_texto) < 1 or char_length(v_texto) > 1000 then
    raise exception 'texto_invalido';
  end if;

  insert into public.mensajes (conversacion_id, autor, texto)
  values (v_conversacion, 'cliente', v_texto)
  returning id into v_id;

  update public.conversaciones set ultimo_mensaje_en = now() where id = v_conversacion;

  return public.chat_mensajes(p_token, v_id - 1);
end $$;

revoke execute on function public.chat_negocio(text), public.chat_iniciar(text),
  public.chat_mensajes(uuid, bigint), public.chat_enviar(uuid, text) from public;
grant execute on function public.chat_negocio(text), public.chat_iniciar(text),
  public.chat_mensajes(uuid, bigint), public.chat_enviar(uuid, text) to anon, authenticated;
