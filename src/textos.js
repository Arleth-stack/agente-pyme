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

  entrar: {
    titulo: 'Entra a tu panel',
    texto: 'Aquí ves a tus clientes y los que te necesitan.',
    correo: 'Correo',
    contrasena: 'Contraseña',
    boton: 'Entrar',
    entrando: 'Entrando…',
    faltanDatos: 'Escribe tu correo y tu contraseña.',
    incorrectos: 'Correo o contraseña incorrectos.',
    sinConexion: 'No hay conexión. Revisa tu internet.',
    crear: '¿Todavía no tienes tu negocio? Créalo aquí',
  },

  horario: {
    dias: { lun: 'Lunes', mar: 'Martes', mie: 'Miércoles', jue: 'Jueves', vie: 'Viernes', sab: 'Sábado', dom: 'Domingo' },
    abre: 'abre', cierra: 'cierra', a: 'a', cerrado: 'Cerrado',
    copiar: 'Usar el horario del lunes de martes a viernes',
    faltaHora: (dia) => `Escribe la hora de abrir y de cerrar del ${dia.toLowerCase()}.`,
    cierreAntes: (dia) => `El ${dia.toLowerCase()}, la hora de cierre debe ser después de la de apertura.`,
    ningunDia: 'Marca al menos un día en que abras.',
  },

  panel: {
    cargando: 'Cargando tu panel…',
    salir: 'Salir',
    verChat: 'Ver mi chat',
    sinNegocio: 'Tu cuenta todavía no tiene un negocio.',
    sinConexion: 'No pudimos cargar tu panel. Revisa tu internet e inténtalo de nuevo.',
    pestanas: { conversaciones: 'Conversaciones', preguntas: 'Preguntas frecuentes', negocio: 'Mi negocio' },
    negocio: {
      ayuda: 'Así te ven tus clientes. Si alguien escribe fuera de horario, le decimos cuándo le contestas.',
      nombre: 'Nombre del negocio',
      telefono: 'WhatsApp del negocio (10 dígitos)',
      direccion: 'Dirección (opcional)',
      horario: 'Horario',
      guardar: 'Guardar cambios',
      guardando: 'Guardando…',
      guardado: 'Listo, guardamos tus cambios.',
      faltaNombre: 'Escribe el nombre de tu negocio.',
      telefonoMal: 'El número debe tener 10 dígitos.',
      noSeGuardo: 'No pudimos guardar. Revisa tu internet e inténtalo de nuevo.',
    },
    temas: {
      horarios: 'Horarios', precios: 'Precios', servicios: 'Servicios', citas: 'Citas',
      pagos: 'Pagos', ubicacion: 'Ubicación', otros: 'Otros',
    },
    preguntas: {
      ayuda: 'Tu WhatsApp contesta con estas respuestas, tal cual las escribas. Si te preguntan algo que no está aquí, te avisa.',
      agregar: '+ Agregar pregunta',
      tituloNueva: 'Nueva pregunta',
      tituloEditar: 'Editar pregunta',
      tema: 'Tema',
      pregunta: '¿Cómo lo preguntan tus clientes?',
      otras: 'Otras formas de preguntarlo (opcional, separadas por coma)',
      respuesta: '¿Qué les respondes?',
      guardar: 'Guardar',
      guardando: 'Guardando…',
      cancelar: 'Cancelar',
      editar: 'Editar',
      pausar: 'Pausar',
      activar: 'Activar',
      quitar: 'Quitar',
      pausada: 'Pausada: tu WhatsApp no la usa',
      confirmarQuitar: (p) => `¿Quitar la pregunta «${p}»? Tu WhatsApp ya no la va a contestar.`,
      faltaPregunta: 'Escribe cómo lo preguntan tus clientes (al menos 3 letras).',
      faltaRespuesta: 'Escribe qué les respondes.',
      repetida: 'Ya tienes esa pregunta.',
      noSeGuardo: 'No pudimos guardar. Revisa tu internet e inténtalo de nuevo.',
      vacio: 'Todavía no tienes preguntas. Agrega las que más te hacen tus clientes.',
      otrasFormas: 'También: ',
    },
    filtros: {
      todas: 'Todas',
      te_necesita: 'Te necesitan',
      la_atiendes_tu: 'Las atiendes tú',
      al_dia: 'Al día',
    },
    estados: {
      te_necesita: 'Te necesita',
      la_atiendes_tu: 'La atiendes tú',
      al_dia: 'Al día',
    },
    motivos: {
      no_la_sabe: 'No la sabe',
      pidio_persona: 'Pidió una persona',
      pide_cita: 'Pide una cita',
      queja_o_urgencia: 'Queja o urgencia',
    },
    clienteSinNombre: 'Cliente',
    volver: '← Volver',
    autores: { cliente: 'Cliente', asistente: 'Respondió tu WhatsApp', dueno: 'Tú' },
    intereses: { precio: 'precios', cita: 'una cita', servicio: 'servicios', ubicacion: 'la ubicación', queja: 'una queja', otro: 'otra cosa' },
    datosCliente: (tel, interes) => [tel && `Tel. ${tel.replace(/(\d{2})(\d{4})(\d{4})/, '$1 $2 $3')}`, interes && `Preguntó por ${interes}`].filter(Boolean).join(' · '),
    avisoDetalle: (motivo) => `Te necesita: ${motivo.toLowerCase()}. Contéstale aquí y tu respuesta le llega en su chat.`,
    atiendesTu: 'La atiendes tú: tu WhatsApp no contesta en esta conversación hasta que la marques como resuelta.',
    escribeRespuesta: 'Escribe tu respuesta',
    enviar: 'Enviar',
    enviando: 'Enviando…',
    resolver: 'Marcar como resuelta',
    noSeEnvio: 'No se envió tu respuesta. Revisa tu internet e inténtalo de nuevo.',
    noSeResolvio: 'No pudimos marcarla como resuelta. Inténtalo de nuevo.',
    sinConversaciones: 'Todavía no hay conversaciones aquí.',
    hace: (fecha) => {
      const min = Math.round((Date.now() - new Date(fecha)) / 60000);
      if (min < 1) return 'ahorita';
      if (min < 60) return `hace ${min} min`;
      const h = Math.round(min / 60);
      if (h < 24) return `hace ${h} h`;
      if (h < 48) return 'ayer';
      return new Date(fecha).toLocaleDateString('es-MX', { day: 'numeric', month: 'short' });
    },
  },
};
