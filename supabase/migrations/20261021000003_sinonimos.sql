-- Ajuste tras correr P1: "necesito" sí distingue ("¿Necesito cita?"), "dental" es
-- lo mismo que "dientes" y "hombre" lo mismo que "caballero".
create or replace function public.sinonimo(p text) returns text
language sql immutable as $$
  select case
    when p in ('ubicado','ubicados','ubicada','ubicacion','direccion','llego','llegar','mapa','localizo') then 'donde'
    when p in ('cita','citas','agendar','agendo','agende','agenda','reservar','reservo','reservacion','reserva',
               'apartar','aparto','turno') then 'cita'
    when p in ('pago','pagos','pagar','tarjeta','tarjetas','efectivo','transferencia','transferencias',
               'deposito','credito','debito') then 'pago'
    when p in ('horario','horarios','abren','abre','cierran','cierra','abierto','abiertos','abierta','hora','horas',
               'lunes','martes','miercoles','jueves','viernes','sabado','sabados','domingo','domingos','festivos') then 'horario'
    when p in ('telefono','numero','celular','whatsapp','contacto') then 'telefono'
    when p in ('domicilio','envio','envios','entrega','entregas','reparto','delivery','llevan','mandan') then 'domicilio'
    when p in ('carro','carros','auto','autos','coche','coches','camioneta','vehiculo','vehiculos') then 'auto'
    when p in ('nino','ninos','nina','ninas','hijo','hijos','hija','hijas','infantil','bebe','bebes','chamacos') then 'nino'
    when p in ('cabello','pelo') then 'cabello'
    when p in ('diente','dientes','muela','muelas','dental','dentales') then 'diente'
    when p in ('hombre','hombres','caballero','caballeros','senor','senores') then 'caballero'
    when p in ('mujer','mujeres','dama','damas','senora','senoras') then 'dama'
    else p
  end;
$$;

create or replace function public.palabras_relleno() returns text[]
language sql immutable as $$
  select array[
    'al','algo','alguien','algun','alguna','ante','aqui','asi','bien','bueno','buena','buenas','buenos','buen',
    'cada','como','con','cual','cuales','cuando','cuanto','cuanta','cuantos','cuantas','cuesta','cuestan',
    'costo','costos','cobran','cobra','precio','precios','sale','salen','del','dia','dias','tardes','noches',
    'esta','estan','este','esto','eso','esa','ese','estos','esas','esos','hay','hola','las','los','les',
    'mas','muy','mucho','mucha','muchas','muchos','para','por','pero','que','quisiera','quiero','queria',
    'saber','sea','ser','sin','sus','tus','una','unos','unas','uno','usted','ustedes','favor','gracias',
    'oiga','disculpe','pregunta','informacion','info','puedo','pueden','puede','podria','podrian',
    'tienen','tiene','tengo','hacen','hace','ofrecen','manejan','dan','trabajan','encuentran','encuentra',
    'queda','quedan','ahi','alli','nos','sobre','entre','hasta','desde','tambien','otra','otro','okey',
    'hoy','semana','ahorita','ahora','luego','todo','todos','toda','todas',
    -- 21 oct
    'hacer','hago','sacar','pedir','ocupo','gustaria','tendran','tendra','manejas',
    'tienes','haces','ofreces','cobras','vale','valen','cotizacion','tarifa','tarifas','aproximadamente',
    'servicio','servicios','mismo','misma','van','son','era','seria','fuera','alguno','algunos','mio','mia'
  ];
$$;
