-- Al reiniciar la demo, cada aviso de ejemplo guarda el último mensaje del
-- cliente (el que lo provocó), igual que hace el chat.
alter function public.reiniciar_demo() rename to cargar_ejemplos;

create function public.reiniciar_demo() returns void
language plpgsql security definer set search_path = '' as $$
begin
  perform public.cargar_ejemplos();
  update public.avisos a set mensaje_cliente = (
    select m.texto from public.mensajes m
    where m.conversacion_id = a.conversacion_id and m.autor = 'cliente'
    order by m.id desc limit 1)
  from public.negocios n
  where n.id = a.negocio_id and n.es_demo;
end $$;

revoke execute on function public.cargar_ejemplos(), public.reiniciar_demo() from public, anon, authenticated;
