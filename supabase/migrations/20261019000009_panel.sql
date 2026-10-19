-- Panel del dueño (T07–T10): permisos finos, atender y resolver, y las
-- conversaciones de ejemplo de las fichas para que el panel no esté vacío.

-- Permisos por columna: el dueño cambia lo de su negocio, no lo interno.
revoke insert, update, delete on public.negocios from authenticated;
grant update (nombre, telefono, direccion, horario, zona_horaria) on public.negocios to authenticated;

revoke insert, update, delete on public.miembros from authenticated;

revoke insert, update, delete on public.conversaciones from authenticated;
grant update (cliente_nombre, cliente_telefono, resumen) on public.conversaciones to authenticated;

-- Mensajes y avisos solo se escriben con las funciones (chat, responder, resolver).
revoke insert, update, delete on public.mensajes, public.avisos from authenticated;

-- Las preguntas sí las administra el dueño, pero no puede moverlas de negocio.
revoke update on public.preguntas from authenticated;
grant update (tema, pregunta, otras_formas, respuesta, activa, orden, actualizado_en) on public.preguntas to authenticated;

-- T08: el dueño contesta desde el panel. Mientras la atiende, el asistente calla.
create function public.responder(p_conversacion uuid, p_texto text) returns json
language plpgsql security definer set search_path = '' as $$
declare
  v_negocio uuid;
  v_texto text := btrim(coalesce(p_texto, ''));
  v_msg public.mensajes%rowtype;
begin
  select negocio_id into v_negocio from public.conversaciones where id = p_conversacion;
  if v_negocio is null or not public.es_miembro(v_negocio) then
    raise exception 'sin_permiso';
  end if;
  if char_length(v_texto) < 1 or char_length(v_texto) > 1000 then
    raise exception 'texto_invalido';
  end if;

  insert into public.mensajes (conversacion_id, autor, texto)
  values (p_conversacion, 'dueno', v_texto)
  returning * into v_msg;

  update public.conversaciones
  set estado = 'la_atiendes_tu', ultimo_mensaje_en = now()
  where id = p_conversacion;

  return json_build_object('id', v_msg.id, 'autor', v_msg.autor, 'texto', v_msg.texto, 'creado_en', v_msg.creado_en);
end $$;

-- T08: marcar como resuelta: el aviso se cierra y el asistente vuelve a contestar.
create function public.resolver(p_conversacion uuid) returns void
language plpgsql security definer set search_path = '' as $$
declare
  v_negocio uuid;
begin
  select negocio_id into v_negocio from public.conversaciones where id = p_conversacion;
  if v_negocio is null or not public.es_miembro(v_negocio) then
    raise exception 'sin_permiso';
  end if;

  update public.avisos set estado = 'resuelto', resuelto_en = now()
  where conversacion_id = p_conversacion and estado = 'pendiente';

  update public.conversaciones set estado = 'al_dia' where id = p_conversacion;
end $$;

revoke execute on function public.responder(uuid, text), public.resolver(uuid) from public, anon;
grant execute on function public.responder(uuid, text), public.resolver(uuid) to authenticated;

-- El chat ya no contesta mientras el dueño atiende la conversación.
create or replace function public.chat_enviar(p_token uuid, p_texto text, p_hora timestamptz default null) returns json
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

  if v_conv.estado = 'la_atiendes_tu' then
    update public.conversaciones set ultimo_mensaje_en = now() where id = v_conv.id;
    return json_build_array(json_build_object(
      'id', v_cliente.id, 'autor', 'cliente', 'texto', v_cliente.texto, 'creado_en', v_cliente.creado_en));
  end if;

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

-- Conversaciones de ejemplo de las fichas v2 (solo negocios demo). El botón
-- de la página de demo (T16) llamará a esta misma función.
create function public.reiniciar_demo() returns void
language plpgsql security definer set search_path = '' as $$
declare
  v_ejemplos jsonb := $json$
  {
    "consultorio-dental-sonrisa-clara": [
      {"nombre": "Laura Méndez", "tel": "5500001001", "estado": "al_dia", "interes": "precio", "min": 95, "mensajes": [
        ["cliente", "Hola, ¿cuánto cuesta una limpieza dental?"],
        ["asistente", "La limpieza dental cuesta $600 e incluye revisión."],
        ["cliente", "Perfecto, gracias"],
        ["asistente", "¡Con gusto! Aquí estoy si necesitas algo más."]]},
      {"nombre": "Jorge Ríos", "tel": "5500001002", "estado": "te_necesita", "interes": "queja", "min": 40, "aviso": "queja_o_urgencia", "mensajes": [
        ["cliente", "Me duele mucho una muela, ¿me pueden ver mañana temprano?"],
        ["asistente", "Lamento mucho lo que pasó. Ya le avisé al equipo. Te escriben en cuanto puedan."]]},
      {"nombre": "Ana Torres", "tel": "5500001003", "estado": "te_necesita", "interes": "cita", "min": 18, "aviso": "pide_cita", "mensajes": [
        ["cliente", "¿Atienden niños?"],
        ["asistente", "Sí, atendemos niños de todas las edades; los sábados tenemos dentista especialista en niños."],
        ["cliente", "Quiero una cita el sábado para mi hijo"],
        ["asistente", "¡Con gusto! Ya le pasé tu solicitud al equipo para que te confirme el lugar. Te escriben en cuanto puedan."]]},
      {"nombre": "Miguel Salas", "tel": "5500001004", "estado": "la_atiendes_tu", "interes": "otro", "min": 7, "aviso": "no_la_sabe", "mensajes": [
        ["cliente", "¿Hacen implantes?"],
        ["asistente", "Esa te la contesta mejor alguien del equipo. Ya le avisé. Te escriben en cuanto puedan."],
        ["dueno", "Hola Miguel, sí hacemos implantes. Primero necesitamos una valoración de $300. ¿Te agendo?"]]}
    ],
    "salon-bella": [
      {"nombre": "Sofía Cruz", "tel": "5500002001", "estado": "al_dia", "interes": "precio", "min": 120, "mensajes": [
        ["cliente", "¿Cuánto cuesta el manicure?"],
        ["asistente", "Manicure $200, pedicure $280 y uñas acrílicas desde $450."],
        ["cliente", "¿Tienen promociones?"],
        ["asistente", "Los martes tenemos 20 % de descuento en manicure."]]},
      {"nombre": "Daniela Pérez", "tel": "5500002002", "estado": "te_necesita", "interes": "cita", "min": 25, "aviso": "pide_cita", "mensajes": [
        ["cliente", "¿Hacen peinado y maquillaje para eventos?"],
        ["asistente", "Sí: peinado $500, maquillaje $600, o los dos por $1,000."],
        ["cliente", "Quiero cita el sábado a las 11 para peinado y maquillaje"],
        ["asistente", "¡Con gusto! Ya le pasé tu solicitud al equipo para que te confirme el lugar. Te escriben en cuanto puedan."]]},
      {"nombre": "Valeria Gómez", "tel": "5500002003", "estado": "te_necesita", "interes": "otro", "min": 12, "aviso": "no_la_sabe", "mensajes": [
        ["cliente", "¿Hacen extensiones de pestañas?"],
        ["asistente", "Esa te la contesta mejor alguien del equipo. Ya le avisé. Te escriben en cuanto puedan."]]},
      {"nombre": "Mariana López", "tel": "5500002004", "estado": "la_atiendes_tu", "interes": "queja", "min": 5, "aviso": "queja_o_urgencia", "mensajes": [
        ["cliente", "Me dejaron mal el tinte, estoy muy molesta"],
        ["asistente", "Lamento mucho lo que pasó. Ya le avisé al equipo. Te escriben en cuanto puedan."],
        ["dueno", "Mariana, lo siento mucho. Ven cuando puedas y te lo corregimos sin costo."]]}
    ],
    "taller-rapido": [
      {"nombre": "Ricardo Luna", "tel": "5500003001", "estado": "al_dia", "interes": "precio", "min": 150, "mensajes": [
        ["cliente", "¿Cuánto cuesta el cambio de aceite?"],
        ["asistente", "El cambio de aceite con filtro va desde $750 con aceite convencional y desde $1,100 con sintético, según el motor."],
        ["cliente", "¿Cuánto tarda?"],
        ["asistente", "Unos 40 minutos; puedes esperar en el taller."]]},
      {"nombre": "Fernando Díaz", "tel": "5500003002", "estado": "te_necesita", "interes": "cita", "min": 30, "aviso": "pide_cita", "mensajes": [
        ["cliente", "Quiero llevar mi carro el lunes para frenos"],
        ["asistente", "¡Con gusto! Ya le pasé tu solicitud al equipo para que te confirme el lugar. Te escriben en cuanto puedan."]]},
      {"nombre": "Patricia Vega", "tel": "5500003003", "estado": "te_necesita", "interes": "otro", "min": 15, "aviso": "no_la_sabe", "mensajes": [
        ["cliente", "¿Tienen grúa?"],
        ["asistente", "Esa te la contesta mejor alguien del equipo. Ya le avisé. Te escriben en cuanto puedan."]]},
      {"nombre": "Héctor Mora", "tel": "5500003004", "estado": "la_atiendes_tu", "interes": "queja", "min": 8, "aviso": "queja_o_urgencia", "mensajes": [
        ["cliente", "Me cobraron de más y el ruido sigue"],
        ["asistente", "Lamento mucho lo que pasó. Ya le avisé al equipo. Te escriben en cuanto puedan."],
        ["dueno", "Héctor, tráelo mañana y lo revisamos sin costo. Disculpa la molestia."]]}
    ]
  }
  $json$;
  v_slug text;
  v_conv jsonb;
  v_negocio uuid;
  v_id uuid;
  v_inicio timestamptz;
  i int;
begin
  delete from public.conversaciones c using public.negocios n
  where c.negocio_id = n.id and n.es_demo;

  for v_slug in select jsonb_object_keys(v_ejemplos) loop
    select id into v_negocio from public.negocios where slug = v_slug and es_demo;
    continue when v_negocio is null;

    for v_conv in select jsonb_array_elements(v_ejemplos -> v_slug) loop
      v_inicio := now() - make_interval(mins => (v_conv ->> 'min')::int);
      insert into public.conversaciones (negocio_id, cliente_nombre, cliente_telefono, estado, interes, creada_en, ultimo_mensaje_en)
      values (v_negocio, v_conv ->> 'nombre', v_conv ->> 'tel', v_conv ->> 'estado', v_conv ->> 'interes',
              v_inicio, v_inicio + make_interval(secs => jsonb_array_length(v_conv -> 'mensajes') * 20))
      returning id into v_id;

      for i in 0 .. jsonb_array_length(v_conv -> 'mensajes') - 1 loop
        insert into public.mensajes (conversacion_id, autor, texto, creado_en)
        values (v_id, v_conv -> 'mensajes' -> i ->> 0, v_conv -> 'mensajes' -> i ->> 1,
                v_inicio + make_interval(secs => (i + 1) * 20));
      end loop;

      if v_conv ? 'aviso' then
        insert into public.avisos (conversacion_id, motivo, mensaje_cliente, creado_en)
        values (v_id, v_conv ->> 'aviso', v_conv -> 'mensajes' -> 0 ->> 1, v_inicio + interval '20 seconds');
      end if;
    end loop;
  end loop;
end $$;

revoke execute on function public.reiniciar_demo() from public, anon, authenticated;

select public.reiniciar_demo();
