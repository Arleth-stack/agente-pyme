-- Los 3 negocios de la demo (fichas v2 de 04_Multiempresa). Datos ficticios.
-- Se cargan directo para construir T01 a T10; en T14 se vuelven a crear con
-- el formulario para medir los 5 minutos.

insert into public.negocios (slug, nombre, giro, telefono, direccion, horario, es_demo) values
('consultorio-dental-sonrisa-clara', 'Consultorio Dental Sonrisa Clara', 'consultorio', '5500000101',
 'Av. Tecnológico 1500, local 4, Col. Centro',
 '{"lun":{"abre":"09:00","cierra":"19:00"},"mar":{"abre":"09:00","cierra":"19:00"},"mie":{"abre":"09:00","cierra":"19:00"},"jue":{"abre":"09:00","cierra":"19:00"},"vie":{"abre":"09:00","cierra":"19:00"},"sab":{"abre":"09:00","cierra":"14:00"},"dom":null}',
 true),
('salon-bella', 'Salón Bella', 'salon', '5500000202',
 'Calle Morelos 230, Col. Centro',
 '{"lun":null,"mar":{"abre":"10:00","cierra":"20:00"},"mie":{"abre":"10:00","cierra":"20:00"},"jue":{"abre":"10:00","cierra":"20:00"},"vie":{"abre":"10:00","cierra":"20:00"},"sab":{"abre":"10:00","cierra":"20:00"},"dom":{"abre":"10:00","cierra":"15:00"}}',
 true),
('taller-rapido', 'Taller Rápido', 'taller', '5500000303',
 'Blvd. Independencia 820, Col. Industrial',
 '{"lun":{"abre":"08:00","cierra":"18:00"},"mar":{"abre":"08:00","cierra":"18:00"},"mie":{"abre":"08:00","cierra":"18:00"},"jue":{"abre":"08:00","cierra":"18:00"},"vie":{"abre":"08:00","cierra":"18:00"},"sab":{"abre":"08:00","cierra":"14:00"},"dom":null}',
 true);

insert into public.preguntas (negocio_id, orden, tema, pregunta, otras_formas, respuesta)
select n.id, p.orden, p.tema, p.pregunta, p.otras_formas, p.respuesta
from (values
  ('consultorio-dental-sonrisa-clara', 1, 'horarios', '¿Cuál es su horario?', 'a qué hora abren, a qué hora cierran, días que atienden', 'Atendemos de lunes a viernes de 9:00 a. m. a 7:00 p. m. y los sábados de 9:00 a. m. a 2:00 p. m. Los domingos descansamos.'),
  ('consultorio-dental-sonrisa-clara', 2, 'citas', '¿Cómo agendo una cita?', 'cómo hago cita, necesito cita, se puede sin cita', 'Escríbenos el día y la hora que te acomodan y alguien del equipo te confirma el lugar.'),
  ('consultorio-dental-sonrisa-clara', 3, 'precios', '¿Cuánto cuesta la consulta?', 'precio de la valoración, cuánto cobran por revisar', 'La valoración cuesta $300 y se descuenta si haces tu tratamiento con nosotros.'),
  ('consultorio-dental-sonrisa-clara', 4, 'precios', '¿Cuánto cuesta una limpieza dental?', 'precio limpieza, profilaxis', 'La limpieza dental cuesta $600 e incluye revisión.'),
  ('consultorio-dental-sonrisa-clara', 5, 'precios', '¿Cuánto cuesta un blanqueamiento?', 'blanquear los dientes, precio blanqueamiento', 'El blanqueamiento en consultorio cuesta $3,500 por sesión.'),
  ('consultorio-dental-sonrisa-clara', 6, 'servicios', '¿Hacen ortodoncia o brackets?', 'frenos dentales, precio de brackets', 'Sí. Primero hacemos una valoración de $300; los brackets metálicos van desde $18,000 el tratamiento completo, con pagos mensuales.'),
  ('consultorio-dental-sonrisa-clara', 7, 'servicios', '¿Atienden niños?', 'dentista para niños, odontopediatra', 'Sí, atendemos niños de todas las edades; los sábados tenemos dentista especialista en niños.'),
  ('consultorio-dental-sonrisa-clara', 8, 'servicios', '¿Hacen resinas o curaciones?', 'tapar una muela, empaste, caries', 'Sí, las resinas van desde $700 por pieza, según el tamaño.'),
  ('consultorio-dental-sonrisa-clara', 9, 'servicios', '¿Atienden urgencias?', 'emergencia dental', 'Sí, en horario de atención damos prioridad a las urgencias. Cuéntanos qué te pasa y alguien del equipo te contesta.'),
  ('consultorio-dental-sonrisa-clara', 10, 'pagos', '¿Aceptan tarjeta?', 'formas de pago, transferencia, efectivo', 'Aceptamos efectivo, tarjeta de débito y crédito y transferencia.'),
  ('consultorio-dental-sonrisa-clara', 11, 'pagos', '¿Aceptan seguro dental?', 'aseguradora, reembolso, factura', 'No trabajamos directamente con aseguradoras, pero te damos factura para que pidas tu reembolso.'),
  ('consultorio-dental-sonrisa-clara', 12, 'ubicacion', '¿Dónde están?', 'dirección, cómo llego, estacionamiento', 'Estamos en Av. Tecnológico 1500, local 4, Col. Centro. Tenemos 4 cajones de estacionamiento al frente.'),

  ('salon-bella', 1, 'horarios', '¿A qué hora abren?', 'horario, a qué hora cierran, abren los lunes', 'Abrimos de martes a sábado de 10:00 a. m. a 8:00 p. m. y los domingos de 10:00 a. m. a 3:00 p. m. Los lunes descansamos.'),
  ('salon-bella', 2, 'citas', '¿Necesito cita?', 'cómo agendo, atienden sin cita', 'Te recomendamos agendar. Escríbenos el día y la hora que quieres y alguien del equipo te confirma. Sin cita te atendemos si hay lugar.'),
  ('salon-bella', 3, 'precios', '¿Cuánto cuesta un corte?', 'precio corte de dama, corte de caballero, corte de niño', 'Corte de dama $250, corte de caballero $150 y corte de niño $120.'),
  ('salon-bella', 4, 'precios', '¿Cuánto cuesta un tinte?', 'precio de tinte, pintarme el cabello, color', 'El tinte va desde $650 en cabello corto; en cabello largo desde $900.'),
  ('salon-bella', 5, 'precios', '¿Cuánto cuestan las mechas o el balayage?', 'luces, rayitos', 'Las mechas y el balayage van desde $1,200, según el largo del cabello.'),
  ('salon-bella', 6, 'precios', '¿Cuánto cuesta el manicure?', 'uñas, pedicure, acrílicas', 'Manicure $200, pedicure $280 y uñas acrílicas desde $450.'),
  ('salon-bella', 7, 'precios', '¿Hacen peinado y maquillaje para eventos?', 'maquillaje para boda, peinado para fiesta, XV años', 'Sí: peinado $500, maquillaje $600, o los dos por $1,000.'),
  ('salon-bella', 8, 'servicios', '¿Hacen keratina o alaciado?', 'alaciado permanente, tratamiento de keratina', 'Sí, la keratina va desde $1,500 según el largo del cabello.'),
  ('salon-bella', 9, 'servicios', '¿Atienden caballeros?', 'barba, barbería, hombres', 'Sí, hacemos corte de caballero y arreglo de barba.'),
  ('salon-bella', 10, 'otros', '¿Qué pasa si llego tarde?', 'tolerancia, retraso', 'Tenemos 15 minutos de tolerancia; después puede que tengamos que cambiar tu cita.'),
  ('salon-bella', 11, 'otros', '¿Tienen promociones?', 'descuentos, ofertas', 'Los martes tenemos 20 % de descuento en manicure.'),
  ('salon-bella', 12, 'ubicacion', '¿Dónde están?', 'dirección, cómo llego', 'Estamos en Calle Morelos 230, Col. Centro.'),

  ('taller-rapido', 1, 'horarios', '¿A qué hora abren?', 'horario, a qué hora cierran, abren sábado', 'Abrimos de lunes a viernes de 8:00 a. m. a 6:00 p. m. y los sábados de 8:00 a. m. a 2:00 p. m.'),
  ('taller-rapido', 2, 'precios', '¿Cuánto cuesta el cambio de aceite?', 'precio aceite, servicio de aceite, aceite sintético', 'El cambio de aceite con filtro va desde $750 con aceite convencional y desde $1,100 con sintético, según el motor.'),
  ('taller-rapido', 3, 'precios', '¿Cuánto cuesta una afinación?', 'afinación menor, servicio de afinación', 'La afinación menor va desde $1,400 para motores de 4 cilindros.'),
  ('taller-rapido', 4, 'precios', '¿Cuánto cuesta el diagnóstico?', 'escáner, revisar el carro, revisión', 'El diagnóstico con escáner cuesta $350 y se descuenta si haces la reparación con nosotros.'),
  ('taller-rapido', 5, 'precios', '¿Cuánto cuestan los frenos?', 'balatas, cambio de frenos', 'El cambio de balatas delanteras va desde $900 de mano de obra, más las refacciones.'),
  ('taller-rapido', 6, 'precios', '¿Cargan el aire acondicionado?', 'gas del clima, aire del carro, clima', 'Sí, la carga de gas del aire acondicionado cuesta $850.'),
  ('taller-rapido', 7, 'servicios', '¿Cuánto tarda un cambio de aceite?', 'cuánto tiempo, me espero', 'Unos 40 minutos; puedes esperar en el taller.'),
  ('taller-rapido', 8, 'citas', '¿Necesito cita?', 'cómo agendo, atienden sin cita', 'Para cambio de aceite no; para reparaciones te recomendamos agendar. Escríbenos el día y alguien del equipo te confirma.'),
  ('taller-rapido', 9, 'servicios', '¿Reparan transmisiones?', 'caja de velocidades, transmisión automática', 'No reparamos transmisiones; solo hacemos cambio de aceite de transmisión desde $1,200.'),
  ('taller-rapido', 10, 'servicios', '¿Dan garantía?', 'garantía de la reparación', 'Sí, 30 días o 1,000 km en mano de obra.'),
  ('taller-rapido', 11, 'pagos', '¿Aceptan tarjeta?', 'formas de pago, transferencia, efectivo', 'Aceptamos efectivo, tarjeta de débito y crédito y transferencia.'),
  ('taller-rapido', 12, 'ubicacion', '¿Dónde están?', 'dirección, cómo llego', 'Estamos en Blvd. Independencia 820, Col. Industrial.')
) as p(slug, orden, tema, pregunta, otras_formas, respuesta)
join public.negocios n on n.slug = p.slug;
