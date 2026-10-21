-- Mejora pedida por Arleth el 21 oct, después de probar con su propio negocio:
-- 1. El saludo cambia según el giro y las preguntas que tiene cada negocio.
-- 2. Entiende más formas de preguntar: sinónimos, preguntas generales
--    ("¿qué precios tienen?", "¿qué ofrecen?"), varias preguntas en un mensaje
--    y "quiero hacer una cita" sin día.
-- 3. Después de avisar al equipo sigue contestando lo que sí sabe.
-- 4. Cuando no sabe, además de avisar ofrece opciones numeradas para que el
--    cliente no se quede esperando. Contestar "2" elige la opción 2.
-- Sigue sin redactar: todo lo que contesta sale del texto exacto del dueño o
-- de frases fijas del sistema.

alter table public.mensajes add column opciones jsonb
  check (opciones is null or jsonb_typeof(opciones) = 'array');

-- Más palabras que no distinguen una pregunta de otra.
create or replace function public.palabras_relleno() returns text[]
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
    'hoy','semana','ahorita','ahora','luego','todo','todos','toda','todas',
    -- 21 oct
    'hacer','hago','sacar','pedir','necesito','necesitaria','ocupo','gustaria','tendran','tendra','manejas',
    'tienes','haces','ofreces','cobras','vale','valen','cotizacion','tarifa','tarifas','aproximadamente',
    'mismo','misma','van','son','era','seria','fuera','alguno','algunos','mio','mia'
  ];
$$;

-- Sinónimos: cada grupo se reduce a una sola palabra para comparar.
create or replace function public.sinonimo(p text) returns text
language sql immutable as $$
  select case
    when p in ('ubicado','ubicados','ubicada','ubicacion','direccion','llego','llegar','mapa','localizo') then 'donde'
    when p in ('cita','citas','agendar','agendo','agende','agenda','reservar','reservo','reservacion','reserva',
               'apartar','aparto','turno') then 'cita'
    when p in ('pago','pagos','pagar','pago','tarjeta','tarjetas','efectivo','transferencia','transferencias',
               'deposito','credito','debito') then 'pago'
    when p in ('horario','horarios','abren','abre','cierran','cierra','abierto','abiertos','abierta','hora','horas',
               'lunes','martes','miercoles','jueves','viernes','sabado','sabados','domingo','domingos','festivos') then 'horario'
    when p in ('telefono','numero','celular','whatsapp','contacto') then 'telefono'
    when p in ('domicilio','envio','envios','entrega','entregas','reparto','delivery','llevan','mandan') then 'domicilio'
    when p in ('carro','carros','auto','autos','coche','coches','camioneta','vehiculo','vehiculos') then 'auto'
    when p in ('nino','ninos','nina','ninas','hijo','hijos','hija','hijas','infantil','bebe','bebes','chamacos') then 'nino'
    when p in ('cabello','pelo') then 'cabello'
    when p in ('diente','dientes','muela','muelas') then 'diente'
    else p
  end;
$$;

create or replace function public.palabras(t text, ignorar text[] default '{}') returns text[]
language sql stable set search_path = '' as $$
  select coalesce(array_agg(distinct public.sinonimo(p)), '{}')
  from unnest(string_to_array(public.normalizar(t), ' ')) as p
  where char_length(p) >= 3
    and p <> all (public.palabras_relleno())
    and p <> all (ignorar);
$$;

-- Palabras de una pregunta general: "¿qué servicios ofrecen?", "¿cómo agendo una cita?".
create function public.palabras_generales() returns text[]
language sql immutable as $$
  select array['servicio','servicios','producto','productos','menu','catalogo','lista','general','opciones',
               'ofrece','venden','vende','dedican','cosas','tipo','tipos','informes','ayuda','manejan',
               'cita','pago','donde','horario','telefono','aceptan','aceptar','formas','forma','trabajos'];
$$;

-- ¿De qué tema pregunta el cliente, aunque no diga nada más?
create function public.intencion(p_texto text) returns text
language sql immutable set search_path = '' as $$
  with t as (select public.normalizar(p_texto) as n)
  select case
    when n ~ '\m(precio|precios|costo|costos|cuesta|cuestan|cobran|cobra|tarifas?|cotiza\w*)\M'
      or n ~ '\mcuanto (sale|es|vale)\M' then 'precios'
    when n ~ '\m(citas?|agend\w*|reserv\w*|apart\w*|turno)\M' then 'citas'
    when n ~ '\m(pagos?|pagar|tarjetas?|efectivo|transferencias?|deposito)\M' then 'pagos'
    when n ~ '\m(donde|direccion|ubicacion|ubicados?|llego|llegar|mapa)\M' then 'ubicacion'
    when n ~ '\m(horarios?|abren|cierran|hora)\M' then 'horarios'
    when n ~ '\m(servicios?|ofrecen|ofrece|venden|vende|manejan|hacen|productos?|menu|catalogo|dedican)\M'
      or n ~ '\mque tienen\M' then 'servicios'
    when n ~ '\m(informacion|info|informes|ayuda|opciones|ayudar)\M' then 'general'
  end
  from t;
$$;

-- Lista numerada para el cliente: "1. ¿Cuánto cuesta…?"
create function public.lista_opciones(p_opciones jsonb) returns text
language sql immutable as $$
  select string_agg(o.n || '. ' || (o.v ->> 'pregunta'), E'\n' order by o.n)
  from jsonb_array_elements(p_opciones) with ordinality as o(v, n);
$$;

-- Hasta p_cuantas preguntas del negocio. Con texto: las que más palabras
-- comparten con el mensaje. Sin texto: una por tema (precios primero).
create function public.sugerir(p_negocio uuid, p_texto text, p_cuantas int default 3,
  p_temas text[] default null) returns jsonb
language sql stable set search_path = '' as $$
  with m as (select public.palabras(p_texto) as w),
  q as (
    select q.id, q.pregunta, q.orden, q.tema,
      (select count(*) from unnest((select w from m)) mw,
         unnest(public.palabras(q.pregunta || ',' || coalesce(q.otras_formas, ''))) vw
       where public.se_parecen(mw, vw)) as comunes,
      array_position(array['precios','servicios','citas','horarios','ubicacion','pagos','otros'], q.tema) as prio,
      row_number() over (partition by q.tema order by q.orden) as en_tema
    from public.preguntas q
    where q.negocio_id = p_negocio and q.activa
      and (p_temas is null or q.tema = any (p_temas))
  ),
  elegidas as (
    select * from q
    order by
      case when p_texto is null then (en_tema > 1)::int else 0 end,
      comunes desc,
      case when p_texto is null then prio else 0 end,
      orden
    limit p_cuantas
  )
  select coalesce(jsonb_agg(jsonb_build_object('id', id, 'pregunta', pregunta)), '[]'::jsonb) from elegidas;
$$;

-- Lo que el chat sabe contestar, dicho según el giro: "precios, tratamientos y citas".
create function public.temas_texto(p_negocio uuid) returns text
language sql stable set search_path = '' as $$
  with n as (select giro from public.negocios where id = p_negocio),
  t as (
    select distinct q.tema,
      array_position(array['precios','servicios','citas','horarios','ubicacion','pagos'], q.tema) as prio
    from public.preguntas q where q.negocio_id = p_negocio and q.activa and q.tema <> 'otros'
  ),
  e as (
    select prio, case t.tema
      when 'precios' then case n.giro when 'gimnasio' then 'precios y mensualidades' else 'precios' end
      when 'servicios' then case n.giro
        when 'consultorio' then 'tratamientos' when 'taller' then 'reparaciones y servicios'
        when 'gimnasio' then 'clases' when 'inmobiliaria' then 'propiedades' else 'servicios' end
      when 'citas' then case n.giro when 'inmobiliaria' then 'visitas' else 'citas' end
      when 'horarios' then 'horario'
      when 'ubicacion' then 'cómo llegar'
      when 'pagos' then 'formas de pago'
    end as etiqueta
    from t, n
  ),
  l as (select array_agg(etiqueta order by prio) as a from e)
  select case
    when a is null then 'lo que necesites'
    when cardinality(a) = 1 then a[1]
    else array_to_string(a[1:cardinality(a) - 1], ', ') || ' y ' || a[cardinality(a)]
  end
  from l;
$$;

-- Mensaje de bienvenida del chat, distinto por giro y por negocio.
create function public.bienvenida(p_negocio uuid) returns text
language sql stable set search_path = '' as $$
  select format('¡Hola! Gracias por escribir a %s. %s Pregúntame por %s. Si prefieres hablar con alguien del equipo, escribe «persona».',
    n.nombre,
    case n.giro
      when 'consultorio' then 'Te ayudo a resolver tus dudas antes de tu consulta.'
      when 'salon' then 'Te ayudo a preparar tu próxima visita.'
      when 'taller' then 'Te ayudo con lo que necesite tu auto.'
      when 'gimnasio' then 'Te ayudo a elegir tu clase o tu membresía.'
      when 'inmobiliaria' then 'Te ayudo a encontrar la propiedad que buscas.'
      else 'Te ayudo con lo que necesites.'
    end,
    public.temas_texto(n.id))
  from public.negocios n where n.id = p_negocio;
$$;

-- Decide qué contesta el asistente. Ahora recibe la conversación para saber si
-- ya había un aviso pendiente y qué opciones se le ofrecieron al cliente.
drop function public.chat_decidir(uuid, text, timestamptz);

create function public.chat_decidir(p_negocio uuid, p_texto text, p_momento timestamptz,
  p_conversacion uuid default null,
  out tipo text, out texto text, out pregunta_id uuid, out tema text, out motivo text, out abierto boolean,
  out opciones jsonb)
language plpgsql stable set search_path = '' as $$
declare
  v_neg public.negocios%rowtype;
  v_norm text := public.normalizar(p_texto);
  v_ignorar text[];
  v_palabras text[];
  v_intencion text;
  v_ya_habia boolean := false;
  v_ultimas jsonb;
  v_n int;
  h record;
  v_cuando text;
  v_partes text[];
  v_parte text;
  v_encontradas uuid[] := '{}';
  v_sin_respuesta boolean := false;
  v_id uuid;
begin
  select * into v_neg from public.negocios n where n.id = p_negocio;
  h := public.estado_horario(p_negocio, p_momento);
  v_cuando := public.texto_cuando(h.abierto, h.dia, h.abre);
  v_ignorar := public.palabras(v_neg.nombre);
  v_palabras := public.palabras(p_texto, v_ignorar);
  v_intencion := public.intencion(p_texto);

  if p_conversacion is not null then
    select exists (select 1 from public.avisos a
                   where a.conversacion_id = p_conversacion and a.estado = 'pendiente') into v_ya_habia;
    select m.opciones into v_ultimas from public.mensajes m
    where m.conversacion_id = p_conversacion and m.autor = 'asistente'
    order by m.id desc limit 1;
  end if;

  -- "2", "la 3", "opción 1": elige de la lista que se le acaba de ofrecer.
  if v_ultimas is not null and v_norm ~ '^(la |el |opcion |numero |la opcion |el numero )?\d{1,2}$' then
    v_n := (regexp_match(v_norm, '(\d{1,2})$'))[1]::int;
    if v_n between 1 and jsonb_array_length(v_ultimas) then
      select q.id, q.respuesta, q.tema into pregunta_id, texto, tema
      from public.preguntas q
      where q.id = (v_ultimas -> (v_n - 1) ->> 'id')::uuid and q.negocio_id = p_negocio and q.activa;
      if pregunta_id is not null then
        tipo := 'faq';
        return;
      end if;
    end if;
  end if;

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
      when h.abierto then 'Sí, ahorita estamos abiertos. Hoy cerramos a ' || public.las(h.cierra)
      when h.dia is null then 'Ahorita estamos cerrados.'
      else 'Ahorita estamos cerrados. Abrimos ' || h.dia || ' a ' || public.las(h.abre)
    end;
    return;
  end if;

  if public.es_saludo(p_texto) then
    tipo := 'saludo';
    if v_norm ~ '(gracias|adios|bye|luego|gusto|amable)' then
      texto := '¡Con gusto! Aquí estoy si necesitas algo más.';
    else
      opciones := public.sugerir(p_negocio, null, 4);
      texto := '¡Hola! ¿En qué te puedo ayudar? Pregúntame por ' || public.temas_texto(p_negocio) || '.';
      if jsonb_array_length(opciones) > 0 then
        texto := texto || E'\n\nPor ejemplo:\n' || public.lista_opciones(opciones);
      else
        opciones := null;
      end if;
    end if;
    return;
  end if;

  -- 1. La pregunta frecuente que mejor explica el mensaje completo.
  select q.id, q.respuesta, q.tema into pregunta_id, texto, tema
  from public.buscar_pregunta(p_negocio, p_texto) b
  join public.preguntas q on q.id = b.pregunta_id;
  if pregunta_id is not null then
    tipo := 'faq';
    return;
  end if;

  -- 2. Varias preguntas en un mensaje: "¿cuánto cuesta la limpieza? ¿y a qué hora abren?"
  v_partes := array_remove(regexp_split_to_array(p_texto, '[?¿!.\n]+|\s+y\s+(?=(a qué|a que|cuánto|cuanto|dónde|donde|qué|que|tienen|hacen|aceptan|atienden|cómo|como)\M)'), '');
  if cardinality(v_partes) >= 2 then
    foreach v_parte in array v_partes loop
      v_id := null;
      select b.pregunta_id into v_id from public.buscar_pregunta(p_negocio, v_parte) b;
      if v_id is not null then
        if not v_id = any (v_encontradas) then v_encontradas := v_encontradas || v_id; end if;
      elsif cardinality(public.palabras(v_parte, v_ignorar)) > 0 and not public.es_saludo(v_parte) then
        v_sin_respuesta := true;
      end if;
    end loop;
    if cardinality(v_encontradas) >= 1 then
      select string_agg(q.respuesta, E'\n\n' order by array_position(v_encontradas, q.id)),
             (array_agg(q.tema order by array_position(v_encontradas, q.id)))[1]
        into texto, tema
      from public.preguntas q where q.id = any (v_encontradas);
      pregunta_id := v_encontradas[1];
      if v_sin_respuesta then
        tipo := 'aviso';
        motivo := 'no_la_sabe';
        texto := texto || E'\n\n' || 'Lo demás se lo pasé al equipo. ' || v_cuando;
      else
        tipo := case when cardinality(v_encontradas) > 1 then 'varias' else 'faq' end;
      end if;
      return;
    end if;
  end if;

  -- 3. Pregunta general de un tema: "¿qué precios tienen?", "¿qué ofrecen?", "quiero una cita".
  if v_palabras <@ public.palabras_generales() then
    if v_intencion in ('precios', 'servicios') then
      -- Si el dueño escribió una pregunta general de ese tema, se usa esa.
      select q.id, q.respuesta, q.tema into pregunta_id, texto, tema
      from public.preguntas q
      where q.negocio_id = p_negocio and q.activa and q.tema = v_intencion
        and public.palabras(q.pregunta, v_ignorar) <@ public.palabras_generales()
      order by q.orden limit 1;
      if pregunta_id is not null then
        tipo := 'faq';
        return;
      end if;
    end if;

    if v_intencion = 'precios' then
      select count(*) into v_n from public.preguntas q
      where q.negocio_id = p_negocio and q.activa and q.tema = 'precios';
      if v_n = 1 then
        select q.id, q.respuesta, q.tema into pregunta_id, texto, tema from public.preguntas q
        where q.negocio_id = p_negocio and q.activa and q.tema = 'precios';
        tipo := 'faq';
        return;
      elsif v_n > 1 then
        select 'Estos son nuestros precios:' || E'\n' || string_agg('• ' || x.respuesta, E'\n' order by x.orden)
          into texto
        from (select q.respuesta, q.orden from public.preguntas q
              where q.negocio_id = p_negocio and q.activa and q.tema = 'precios'
              order by q.orden limit 8) x;
        tipo := 'temas';
        tema := 'precios';
        return;
      end if;
    elsif v_intencion in ('citas', 'pagos', 'ubicacion', 'horarios') then
      select q.id, q.respuesta, q.tema into pregunta_id, texto, tema
      from public.preguntas q
      where q.negocio_id = p_negocio and q.activa and q.tema = v_intencion
      order by q.orden limit 1;
      if pregunta_id is not null then
        tipo := 'faq';
        return;
      end if;
      if v_intencion = 'citas' then
        tipo := 'pide_dia';
        tema := 'citas';
        texto := '¡Claro! Dime qué día y a qué hora te gustaría, y se lo paso al equipo para que te confirme.';
        return;
      end if;
    end if;

    -- Menú: lo que sí sabe contestar, para que el cliente elija.
    opciones := public.sugerir(p_negocio, null, 6,
      case when v_intencion = 'servicios' then array['servicios','precios'] end);
    if jsonb_array_length(opciones) = 0 then
      opciones := public.sugerir(p_negocio, null, 6);
    end if;
    if jsonb_array_length(opciones) > 0 then
      tipo := 'menu';
      tema := case when v_intencion = 'servicios' then 'servicios' end;
      texto := format('En %s te puedo contar de esto:', v_neg.nombre) || E'\n' || public.lista_opciones(opciones)
        || E'\n\n' || 'Escríbeme el número o tu pregunta.';
      return;
    end if;
    opciones := null;
  end if;

  -- 4. No la sabe: avisa al equipo y, mientras, ofrece lo que sí sabe.
  tipo := 'aviso';
  motivo := 'no_la_sabe';
  texto := case when v_ya_habia
    then 'Esa también se la pasé al equipo. '
    else 'Esa no la tengo a la mano, pero ya le pasé tu pregunta al equipo. '
  end || v_cuando;
  opciones := public.sugerir(p_negocio, p_texto, 3);
  if jsonb_array_length(opciones) > 0 then
    texto := texto || E'\n\n' || 'Mientras, te puedo ayudar con esto:' || E'\n' || public.lista_opciones(opciones);
  else
    opciones := null;
  end if;
end $$;

-- chat_enviar: siempre contesta (aunque haya aviso o el dueño ya esté en la
-- conversación) y guarda las opciones que se le ofrecen al cliente.
create or replace function public.chat_enviar(p_token uuid, p_texto text, p_hora timestamptz default null) returns json
language plpgsql security definer set search_path = '' as $$
declare
  v_conv public.conversaciones%rowtype;
  v_texto text := btrim(coalesce(p_texto, ''));
  v_momento timestamptz;
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
  v_momento := public.momento(v_conv.negocio_id, p_hora);

  -- Se decide antes de guardar el mensaje para leer las opciones de la última respuesta.
  d := public.chat_decidir(v_conv.negocio_id, v_texto, v_momento, v_conv.id);

  insert into public.mensajes (conversacion_id, autor, texto)
  values (v_conv.id, 'cliente', v_texto)
  returning * into v_cliente;

  if d.tipo = 'aviso' then
    insert into public.avisos (conversacion_id, motivo, mensaje_cliente)
    values (v_conv.id, d.motivo, v_texto)
    on conflict (conversacion_id) where estado = 'pendiente'
    do update set motivo = excluded.motivo, mensaje_cliente = excluded.mensaje_cliente
      where public.prioridad_motivo(excluded.motivo) > public.prioridad_motivo(public.avisos.motivo);
  end if;

  insert into public.mensajes (conversacion_id, autor, texto, pregunta_id, opciones)
  values (v_conv.id, 'asistente', d.texto, d.pregunta_id, d.opciones)
  returning * into v_resp;

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
  ) || jsonb_build_array(jsonb_strip_nulls(jsonb_build_object(
    'id', v_resp.id, 'autor', 'asistente', 'texto', v_resp.texto, 'creado_en', v_resp.creado_en,
    'tipo', d.tipo, 'motivo', d.motivo, 'abierto', d.abierto, 'opciones', d.opciones
  ))))::json;
end $$;

create or replace function public.chat_mensajes(p_token uuid, p_despues_de bigint default 0) returns json
language sql stable security definer set search_path = '' as $$
  select coalesce(json_agg(json_strip_nulls(json_build_object(
           'id', m.id, 'autor', m.autor, 'texto', m.texto, 'creado_en', m.creado_en, 'opciones', m.opciones
         )) order by m.id), '[]'::json)
  from public.mensajes m
  join public.conversaciones c on c.id = m.conversacion_id
  where c.token = p_token and m.id > p_despues_de;
$$;

-- El chat muestra la bienvenida del negocio y preguntas para tocar.
create or replace function public.chat_negocio(p_slug text, p_hora timestamptz default null) returns json
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
    'estado', public.texto_estado(h.abierto, h.cierra, h.dia, h.abre),
    'bienvenida', public.bienvenida(v_neg.id),
    'sugerencias', (select coalesce(jsonb_agg(s ->> 'pregunta'), '[]'::jsonb)
                    from jsonb_array_elements(public.sugerir(v_neg.id, null, 4)) s)
  );
end $$;

revoke execute on function public.sinonimo(text), public.palabras_generales(), public.intencion(text),
  public.lista_opciones(jsonb), public.sugerir(uuid, text, int, text[]), public.temas_texto(uuid),
  public.bienvenida(uuid), public.chat_decidir(uuid, text, timestamptz, uuid)
  from public, anon, authenticated;
