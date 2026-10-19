import { createClient } from '@supabase/supabase-js';

// La llave pública está hecha para viajar en la página: lo que protege los
// datos son las reglas por fila y las funciones de la base, no esconderla.
export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY,
);
