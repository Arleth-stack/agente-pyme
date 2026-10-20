-- T16: el botón "Reiniciar demo" de la página de demo. Solo toca las
-- conversaciones de los negocios marcados como demo; ningún otro negocio.
grant execute on function public.reiniciar_demo() to anon, authenticated;
