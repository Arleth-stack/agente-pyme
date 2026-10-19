// Todos los textos que ven el dueño y el cliente viven aquí, para revisar
// la regla de lenguaje en un solo lugar (Propuesta de valor y guía de lenguaje v2).

export const textos = {
  marca: 'Tu WhatsApp contesta solo',

  inicio: {
    titulo: 'Tu WhatsApp responde solo, a cualquier hora.',
    texto: 'Escribe las preguntas que te hacen tus clientes y te avisamos cuando alguien te necesite.',
    ejemplos: 'Prueba cómo contesta el WhatsApp de estos negocios:',
  },

  chat: {
    bienvenida: (negocio) =>
      `¡Hola! Soy el asistente de ${negocio}. Te ayudo con precios, horarios y citas. Si prefieres hablar con alguien del equipo, escribe «persona».`,
    placeholder: 'Escribe un mensaje',
    enviar: 'Enviar',
    noEncontrado: 'No encontramos este negocio. Revisa el enlace.',
    sinConexion: 'No pudimos cargar el chat. Revisa tu internet e inténtalo de nuevo.',
    noSeEnvio: 'No se envió · Toca para reintentar',
    hoy: 'Hoy',
    escribiendo: 'escribiendo…',
  },
};
