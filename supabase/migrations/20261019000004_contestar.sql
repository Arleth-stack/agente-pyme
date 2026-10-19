-- T02: el chat contesta con las preguntas frecuentes del negocio.
-- Nunca redacta: regresa el texto exacto que escribió el dueño. Si duda,
-- prefiere no contestar (T03 convierte ese "no sé" en un aviso).

-- Minúsculas, sin acentos, sin signos y con un solo espacio.
create function public.normalizar(t text) returns text
language sql stable set search_path = '' as $$
  select btrim(regexp_replace(
    regexp_replace(lower(extensions.unaccent('extensions.unaccent'::regdictionary, coalesce(t, ''))), '[^a-z0-9]+', ' ', 'g'),
    '\s+', ' ', 'g'));
$$;

-- Raíz aproximada para que "cortan" y "corte", o "pagar" y "pago", se reconozcan.
create function public.raiz(w text) returns text
language sql immutable set search_path = '' as $$
  select regexp_replace(regexp_replace(w, '(es|s)$', ''), '(ar|er|ir|an|en|as|os|a|e|o)$', '');
$$;

-- Palabras que no distinguen una pregunta de otra (relleno, cortesía, tiempo).
create function public.palabras_relleno() returns text[]
language sql immutable as $$
  select array[
    'al','algo','alguien','algun','alguna','ante','aqui','asi','bien','bueno','buena','buenas','buenos','buen',
    'cada','como','con','cual','cuales','cuando','cuanto','cuanta','cuantos','cuantas','cuesta','cuestan',
    'costo','costos','cobran','cobra','precio','precios','sale','salen','del','dia','dias','tardes','noches',
    'esta','estan','este','esto','eso','esa','ese','estos','esas','esos','hay','hola','las','los','les',
    'mas','muy','mucho','mucha','muchas','muchos','para','por','pero','que','quisiera','quiero','queria',
    'saber','sea','ser','sin','sus','tus','una','unos','unas','uno','usted','ustedes','favor','gracias',
    'oiga','disculpe','pregunta','informacion','info','puedo','pueden','puede','podria','podrian',
    'tienen','tiene','tengo','hacen','hace','ofrecen','manejan','dan','trabajan','encuentran','encuentra',
    'queda','quedan','ahi','alli','nos','sobre','entre','hasta','desde','tambien','otra','otro','okey',
    'hoy','semana','ahorita','ahora','luego','todo','todos','toda','todas'
  ];
$$;

-- Palabras con significado de un texto. Las palabras del nombre del negocio
-- se ignoran ("¿dónde queda el taller?" en Taller Rápido).
create function public.palabras(t text, ignorar text[] default '{}') returns text[]
language sql stable set search_path = '' as $$
  select coalesce(array_agg(distinct
           case when p in ('ubicado','ubicados','ubicada','ubicacion','direccion','domicilio') then 'donde' else p end),
         '{}')
  from unnest(string_to_array(public.normalizar(t), ' ')) as p
  where char_length(p) >= 3
    and p <> all (public.palabras_relleno())
    and p <> all (ignorar);
$$;

create function public.se_parecen(a text, b text) returns boolean
language sql stable set search_path = '' as $$
  select a = b
      or (char_length(public.raiz(a)) >= 3 and public.raiz(a) = public.raiz(b))
      or extensions.similarity(a, b) >= 0.5;
$$;

-- La pregunta frecuente activa del negocio que mejor explica el mensaje.
-- cobertura: qué parte de las palabras del cliente explica la pregunta.
-- frase: qué tan completa coincide la mejor forma de la pregunta (desempate).
create function public.buscar_pregunta(p_negocio uuid, p_texto text)
returns table (pregunta_id uuid, cobertura numeric, frase numeric)
language sql stable set search_path = '' as $$
  with ignorar as (
    select public.palabras(n.nombre) as w from public.negocios n where n.id = p_negocio
  ),
  mensaje as (
    select public.palabras(p_texto, (select w from ignorar)) as w
  ),
  formas as (
    select q.id, q.orden, public.palabras(f, (select w from ignorar)) as w
    from public.preguntas q,
         unnest(array[q.pregunta] || coalesce(string_to_array(q.otras_formas, ','), '{}')) as f
    where q.negocio_id = p_negocio and q.activa
  ),
  vocabulario as (
    select id, orden, array_agg(distinct x) as w
    from formas, unnest(formas.w) as x
    group by id, orden
  ),
  puntaje as (
    select v.id, v.orden,
      (select count(*) from unnest(m.w) as mw
        where exists (select 1 from unnest(v.w) as vw where public.se_parecen(mw, vw)))::numeric
        / nullif(cardinality(m.w), 0) as cobertura,
      (select max(
         (select count(*) from unnest(f.w) as fw
           where exists (select 1 from unnest(m.w) as mw where public.se_parecen(mw, fw)))::numeric
         / nullif(cardinality(f.w), 0))
       from formas f where f.id = v.id) as frase
    from vocabulario v, mensaje m
  )
  select id, cobertura, frase from puntaje
  where cobertura >= 0.6
  order by cobertura desc, frase desc nulls last, orden
  limit 1;
$$;

-- ¿El mensaje es solo saludo, gracias o despedida?
create function public.es_saludo(p_texto text) returns boolean
language sql stable set search_path = '' as $$
  select cardinality(string_to_array(public.normalizar(p_texto), ' ')) > 0
     and public.normalizar(p_texto) <> ''
     and string_to_array(public.normalizar(p_texto), ' ') <@ array[
       'hola','buenas','buenos','buen','dia','dias','tardes','noches','que','tal','saludos','gracias',
       'muchas','mil','ok','okey','va','sale','perfecto','excelente','adios','bye','hasta','luego',
       'gusto','igualmente','vale','listo','genial','muy','amable','bien'];
$$;

-- Decide qué contesta el asistente. Regresa tipo ('faq', 'saludo' o 'nada'),
-- el texto y la pregunta usada. Cada ticket siguiente agrega reglas aquí.
create function public.chat_decidir(p_negocio uuid, p_texto text,
  out tipo text, out texto text, out pregunta_id uuid, out tema text)
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

  tipo := case when pregunta_id is null then 'nada' else 'faq' end;
end $$;

-- chat_enviar ahora guarda el mensaje del cliente y, si sabe, la respuesta.
drop function public.chat_enviar(uuid, text);

create function public.chat_enviar(p_token uuid, p_texto text) returns json
language plpgsql security definer set search_path = '' as $$
declare
  v_conv public.conversaciones%rowtype;
  v_texto text := btrim(coalesce(p_texto, ''));
  v_cliente public.mensajes%rowtype;
  v_resp public.mensajes%rowtype;
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

  if d.tipo <> 'nada' then
    insert into public.mensajes (conversacion_id, autor, texto, pregunta_id)
    values (v_conv.id, 'asistente', d.texto, d.pregunta_id)
    returning * into v_resp;
  end if;

  update public.conversaciones set
    ultimo_mensaje_en = now(),
    interes = case
      when d.tema is null then interes
      when d.tema = 'precios' then 'precio' when d.tema = 'citas' then 'cita'
      when d.tema = 'servicios' then 'servicio' when d.tema = 'ubicacion' then 'ubicacion'
      else 'otro' end
  where id = v_conv.id;

  return (jsonb_build_array(
    jsonb_build_object('id', v_cliente.id, 'autor', 'cliente', 'texto', v_cliente.texto, 'creado_en', v_cliente.creado_en)
  ) || case when v_resp.id is null then '[]'::jsonb else jsonb_build_array(jsonb_build_object(
    'id', v_resp.id, 'autor', 'asistente', 'texto', v_resp.texto, 'creado_en', v_resp.creado_en, 'tipo', d.tipo
  )) end)::json;
end $$;

revoke execute on function public.chat_enviar(uuid, text) from public;
grant execute on function public.chat_enviar(uuid, text) to anon, authenticated;

-- Las funciones auxiliares no se llaman desde afuera.
revoke execute on function public.normalizar(text), public.raiz(text), public.palabras_relleno(),
  public.palabras(text, text[]), public.se_parecen(text, text), public.buscar_pregunta(uuid, text),
  public.es_saludo(text), public.chat_decidir(uuid, text) from public, anon, authenticated;
