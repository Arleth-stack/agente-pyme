-- Ajustes del 21 oct tras probar con Tacos El negro:
-- "servicio" no distingue una pregunta ("¿tienen servicio a domicilio?" = entregas);
-- si el cliente pregunta un tema que el negocio no tiene escrito (pagos), se avisa
-- en vez de mostrar el menú; el horario y la dirección salen de los datos del negocio
-- cuando no hay pregunta escrita; el menú respeta el orden de temas pedido.

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
    'servicio','servicios','mismo','misma','van','son','era','seria','fuera','alguno','algunos','mio','mia'
  ];
$$;

create or replace function public.sugerir(p_negocio uuid, p_texto text, p_cuantas int default 3,
  p_temas text[] default null) returns jsonb
language sql stable set search_path = '' as $$
  with m as (select public.palabras(p_texto) as w),
  q as (
    select q.id, q.pregunta, q.orden, q.tema,
      (select count(*) from unnest((select w from m)) mw,
         unnest(public.palabras(q.pregunta || ',' || coalesce(q.otras_formas, ''))) vw
       where public.se_parecen(mw, vw)) as comunes,
      array_position(coalesce(p_temas, array['precios','servicios','citas','horarios','ubicacion','pagos','otros']), q.tema) as prio,
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
      prio,
      orden
    limit p_cuantas
  )
  select coalesce(jsonb_agg(jsonb_build_object('id', id, 'pregunta', pregunta)), '[]'::jsonb) from elegidas;
$$;

create or replace function public.chat_decidir(p_negocio uuid, p_texto text, p_momento timestamptz,
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
      -- Sin pregunta escrita, el horario y la dirección salen de los datos del negocio.
      if v_intencion = 'horarios' then
        tipo := 'horario';
        abierto := h.abierto;
        tema := 'horarios';
        texto := case
          when h.abierto then 'Ahorita estamos abiertos. Hoy cerramos a ' || public.las(h.cierra)
          when h.dia is null then 'Ahorita estamos cerrados.'
          else 'Ahorita estamos cerrados. Abrimos ' || h.dia || ' a ' || public.las(h.abre)
        end;
        return;
      end if;
      if v_intencion = 'ubicacion' and coalesce(btrim(v_neg.direccion), '') <> '' then
        tipo := 'faq';
        tema := 'ubicacion';
        texto := 'Estamos en ' || regexp_replace(btrim(v_neg.direccion), '\.$', '') || '.';
        return;
      end if;
    end if;

    -- Menú: lo que sí sabe contestar, para que el cliente elija. Si preguntó
    -- un tema concreto que el negocio no tiene escrito, mejor se avisa (paso 4).
    if v_intencion is null or v_intencion in ('servicios', 'general') then
    opciones := public.sugerir(p_negocio, null, 6,
      case when v_intencion = 'servicios' then array['servicios','precios','otros'] end);
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
