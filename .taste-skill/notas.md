# Notas de diseño — inicio (puerta de entrada a Merkatics)

## Lectura del encargo
Página de inicio del módulo "Tu WhatsApp contesta solo" (Merkatics 2026-544-16). Público: dueños de PyME mexicanas no técnicos (consultorios, salones, talleres). Una acción: Crear mi negocio. Segunda: Entrar a mi panel. Marca: Merkatics (puerta de entrada). Imágenes propias: ninguna foto; sí hay interfaz real (chat, formulario, panel) que se puede mostrar en HTML.

## Inventario (lo que es de este producto y de nadie más)
1. El mensaje que llega a las 11:42 p. m. mientras el dueño duerme o atiende.
2. Las palomitas, la hora y el "escribiendo…" del chat.
3. Precios reales de negocio mexicano: corte de dama $250, limpieza $600, cambio de aceite $750.
4. Las direcciones de la demo: Calle Morelos 230 (Salón Bella), Av. Tecnológico 1500 (Sonrisa Clara), Blvd. Independencia 820 (Taller Rápido).
5. Las manos ocupadas del dueño: tijeras, llave de cruz, la silla del dentista.
6. El aviso: "Un cliente te necesita · Pide una cita".
7. El formulario: "¿Cómo lo preguntan tus clientes?" / "¿Qué les respondes?".
8. "Nunca inventa": la respuesta es exactamente la que escribió el dueño.
9. "Cerrado · abre mañana a las 10:00 a. m."
10. Merkatics: el siguiente paso (seguimiento, CRM, campañas).

## Argumento (una línea por sección)
- Portada: Tu WhatsApp contesta aunque tengas las manos ocupadas → prueba: chat real que contesta ahorita (la cosa viva).
- Con tus palabras: contesta exactamente lo que tú escribiste, no inventa → prueba: lo que escribe el dueño junto a lo que recibe el cliente.
- Te avisa: cuando piden cita, se quejan o no sabe, te avisa → prueba: el panel con el aviso.
- Cómo empiezas: 4 pasos en un formulario → prueba: los pasos reales y el botón.
- Para quién: negocios que viven en WhatsApp → prueba: fotos de negocios así y las preguntas que reciben.
- Lo que sigue: cuando quieras crecer, Merkatics → prueba: lo que agrega Merkatics.
- Preguntas: dudas honestas (¿es mi número de WhatsApp?).
- Cierre: crear mi negocio, firma Merkatics.

## Dirección elegida
product-performs: el chat real de un negocio de la demo, contestando en la portada, es la mejor prueba y lleva el inventario (precios reales, horario real, aviso real).

## Marca Merkatics (manual de identidad + iconografía, entregados por Arleth el 21 oct)
Sustituye la paleta sorteada (equivale a --keep palette): fondo grafito #111111, superficie #1E1E1E, tinta #F1F1F1, gris secundario #9A9A9A (el #757575 de la marca no alcanza contraste 4.5:1 sobre grafito), acento coral #E95349 (10–20 % de la página: botón, marcadores, el escenario de la portada y el cierre).
Tipografía: Jost, que es la libre inspirada en Futura (la del logotipo); se conserva la sorteada.
Logo: imagotipo recortado del manual (variante de fondo oscuro: ícono coral, MERKATICS en blanco, "Operating System" en coral). Escritura "Merkatics".
Iconos: lineales de 2 px, puntas redondeadas, acento coral, rejilla de 24 px (solo en la sección Merkatics, como marcadores de lista; activo de marca).

## La idea
En esta página, el mensaje que llega a las 11:42 p. m. cuando el negocio ya cerró se convierte en el fragmento de chat sobre el escenario coral; y la cosa viva es la demo: eliges uno de los 3 negocios y una hora, y le preguntas tú como cliente (contesta la base real).

## Avance 21 oct (pausa por límite de uso)
- Fotos revisadas y aprobadas; versiones ligeras listas: public/fotos/salon.jpg, consultorio.jpg, barberia.jpg (créditos en credits.json; los originales se pueden borrar al terminar).
- Respuestas reales de Salón Bella a las 11:42 p. m. (para el fragmento de portada):
  - "cuanto cuesta un corte de dama" → "Corte de dama $250, corte de caballero $150 y corte de niño $120."
  - "quiero cita el sabado a las 11" → "¡Con gusto! Ya le pasé tu solicitud al equipo para que te confirme el lugar. Ahorita estamos cerrados; te escriben mañana a partir de las 10:00 a. m." (aviso pide_cita)
- Siguiente: escribir index.html (copia fija en el HTML; P5 también revisa el HTML) + src/inicio.js (demo en vivo con chat_iniciar/chat_enviar/chat_negocio y p_hora) + hoja de estilos de marca; crear.js debe leer ?nombre=&giro=; luego lint/inspect, módulos, guion D4.
