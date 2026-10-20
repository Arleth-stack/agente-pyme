# Tu WhatsApp contesta solo

Qué es: módulo multiempresa para que el WhatsApp de una PyME conteste solo sus preguntas frecuentes y avise al dueño cuando un cliente lo necesita (Merkatics 2026-544-16, Fase 1 con canal simulado).
Cómo se usa: el dueño crea su negocio en https://agente-pyme-merkatics.vercel.app/crear, comparte el enlace de su chat y atiende los avisos en /panel; la demo para presentar está en /demo.
Cómo se corre: `npm install`, copiar `.env.example` como `.env.local` con los datos de Supabase y `npm run dev`; pruebas con `node pruebas/correr.mjs`, `node pruebas/aislamiento.mjs` y `node pruebas/lenguaje.mjs`.
Quién lo mantiene: Arleth Caballero (practicante GrowthLab, Merkatics); documentación en `docs/` y en el Drive del proyecto.
Ojo: la base gratuita de Supabase se pausa sola tras una semana sin uso (abre la demo antes de presentarla) y las cuentas de la demo viven solo en `cuentas-demo.local.txt`, fuera de GitHub.
