-- T15: nombres y enlaces de los negocios demo (información pública: es lo
-- mismo que muestra su chat). La pantalla de aislamiento y la página de demo
-- los usan para intentar leerlos con la sesión del dueño.
create function public.negocios_demo() returns json
language sql stable security definer set search_path = '' as $$
  select coalesce(json_agg(json_build_object('slug', slug, 'nombre', nombre) order by nombre), '[]'::json)
  from public.negocios where es_demo;
$$;

revoke execute on function public.negocios_demo() from public;
grant execute on function public.negocios_demo() to anon, authenticated;
