-- T04 (ajuste): "quiero llevarlo mañana a las 10" no se reconocía como cita
-- porque la regla esperaba palabras exactas. Ahora acepta sus variantes.

create or replace function public.detectar_motivo(p_texto text) returns text
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
    when n ~ '\m(cita\w*|agend\w*|apart\w*|reserv\w*|turno|espacio|lugar|llev\w*|ir|voy|pas\w*|ver|verme|atend\w*|atiend\w*)\M'
     and n ~ '(\m(lunes|martes|miercoles|jueves|viernes|sabado|domingo|hoy|manana|pasado manana)\M|\ma las \d|\m\d{1,2}( ?(am|pm|hrs|horas))\M|\men la (manana|tarde|noche)\M)'
      then 'pide_cita'
  end
  from t;
$$;
