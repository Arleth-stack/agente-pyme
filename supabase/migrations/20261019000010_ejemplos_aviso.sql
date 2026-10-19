-- Datos de ejemplo: el aviso guarda el mensaje del cliente que lo provocó
-- (el último del cliente), no su primera pregunta.
update public.avisos a set mensaje_cliente = (
  select m.texto from public.mensajes m
  where m.conversacion_id = a.conversacion_id and m.autor = 'cliente'
  order by m.id desc limit 1)
from public.negocios n
where n.id = a.negocio_id and n.es_demo;
