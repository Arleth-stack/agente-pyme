-- Ajuste del 21 oct tras probar Gym Fit: "¿qué servicios tienen?" no encontraba
-- "¿Qué clases tienen?". Lo que cada giro ofrece (clases, tratamientos, propiedades…)
-- cuenta como pregunta general, y una pregunta de servicios que empieza con
-- "¿Qué…?" o "¿Cuáles…?" sirve para contestar "¿qué ofrecen?".
create or replace function public.palabras_generales() returns text[]
language sql immutable as $$
  select array['servicio','servicios','producto','productos','menu','catalogo','lista','general','opciones',
               'ofrece','venden','vende','dedican','cosas','tipo','tipos','informes','ayuda','manejan',
               'cita','pago','donde','horario','telefono','aceptan','aceptar','formas','forma','trabajos',
               'clases','clase','actividades','tratamientos','tratamiento','propiedades','disponibles',
               'paquetes','planes','platillos','comida','cursos','reparaciones','disciplinas'];
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

  -- Si lo último que se habló fue de citas y el cliente da día u hora
  -- ("el sábado a las 11"), es una solicitud de cita.
  if motivo is null and p_conversacion is not null and public.menciona_dia(p_texto) and exists (
    select 1 from (
      select m.pregunta_id, m.texto from public.mensajes m
      where m.conversacion_id = p_conversacion and m.autor = 'asistente'
      order by m.id desc limit 1
    ) u
    left join public.preguntas q on q.id = u.pregunta_id
    where q.tema = 'citas' or u.texto like '¡Claro! Dime qué día%'
  ) then
    motivo := 'pide_cita';
  end if;
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
        and (public.palabras(q.pregunta, v_ignorar) <@ public.palabras_generales()
             -- "¿Qué clases tienen?", "¿Qué propiedades tienen disponibles?": la lista del negocio.
             or (v_intencion = 'servicios' and public.normalizar(q.pregunta) ~ '^(que|cuales)\M'))
      order by (public.palabras(q.pregunta, v_ignorar) <@ public.palabras_generales()) desc, q.orden
      limit 1;
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
