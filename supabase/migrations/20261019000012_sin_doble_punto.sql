-- Corrige el doble punto: "las 10:00 a. m." ya termina en punto, así que
-- no se le agrega otro al final de la frase.

create or replace function public.texto_cuando(abierto boolean, dia text, abre time) returns text
language sql immutable as $$
  select case
    when abierto or dia is null then 'Te escriben en cuanto puedan.'
    else 'Ahorita estamos cerrados; te escriben ' || dia || ' a partir de ' || public.las(abre)
  end;
$$;

create or replace function public.chat_decidir(p_negocio uuid, p_texto text, p_momento timestamptz,
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
      when h.abierto then 'Sí, ahorita estamos abiertos. Hoy cerramos a ' || public.las(h.cierra)
      when h.dia is null then 'Ahorita estamos cerrados.'
      else 'Ahorita estamos cerrados. Abrimos ' || h.dia || ' a ' || public.las(h.abre)
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
