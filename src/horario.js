import { textos } from './textos.js';

// Editor de horario por día. Lo usan "Mi negocio" (T10) y "Crear mi negocio" (T11).
// El horario se guarda como { lun: { abre: '09:00', cierra: '19:00' }, dom: null, ... }.

const th = textos.horario;
const DIAS = ['lun', 'mar', 'mie', 'jue', 'vie', 'sab', 'dom'];

export function crearEditorHorario($contenedor, horario = {}) {
  $contenedor.classList.add('editor-horario');
  const filas = {};

  for (const dia of DIAS) {
    const valor = horario[dia];
    const $fila = document.createElement('div');
    $fila.className = 'horario-fila';

    const $abierto = document.createElement('input');
    $abierto.type = 'checkbox';
    $abierto.id = `horario-${dia}`;
    $abierto.checked = Boolean(valor);

    const $etiqueta = document.createElement('label');
    $etiqueta.htmlFor = $abierto.id;
    $etiqueta.textContent = th.dias[dia];

    const $abre = document.createElement('input');
    $abre.type = 'time';
    $abre.className = 'hora-abre';
    $abre.value = valor?.abre ?? '09:00';
    $abre.setAttribute('aria-label', `${th.dias[dia]}: ${th.abre}`);

    const $cierra = document.createElement('input');
    $cierra.type = 'time';
    $cierra.className = 'hora-cierra';
    $cierra.value = valor?.cierra ?? '18:00';
    $cierra.setAttribute('aria-label', `${th.dias[dia]}: ${th.cierra}`);

    const $a = document.createElement('span');
    $a.className = 'suave horario-a';
    $a.textContent = th.a;

    const $cerrado = document.createElement('span');
    $cerrado.className = 'suave horario-cerrado';
    $cerrado.textContent = th.cerrado;

    const actualizar = () => {
      $fila.classList.toggle('dia-cerrado', !$abierto.checked);
    };
    $abierto.addEventListener('change', actualizar);
    actualizar();

    $fila.append($abierto, $etiqueta, $abre, $a, $cierra, $cerrado);
    $contenedor.append($fila);
    filas[dia] = { $abierto, $abre, $cierra };
  }

  const $copiar = document.createElement('button');
  $copiar.type = 'button';
  $copiar.className = 'boton-chico';
  $copiar.textContent = th.copiar;
  $copiar.addEventListener('click', () => {
    const lun = filas.lun;
    for (const dia of ['mar', 'mie', 'jue', 'vie']) {
      filas[dia].$abierto.checked = lun.$abierto.checked;
      filas[dia].$abre.value = lun.$abre.value;
      filas[dia].$cierra.value = lun.$cierra.value;
      filas[dia].$abierto.dispatchEvent(new Event('change'));
    }
  });
  $contenedor.append($copiar);

  return {
    // Regresa { horario } o { error } con un mensaje en español.
    leer() {
      const resultado = {};
      for (const dia of DIAS) {
        const { $abierto, $abre, $cierra } = filas[dia];
        if (!$abierto.checked) {
          resultado[dia] = null;
          continue;
        }
        if (!$abre.value || !$cierra.value) return { error: th.faltaHora(th.dias[dia]) };
        if ($cierra.value <= $abre.value) return { error: th.cierreAntes(th.dias[dia]) };
        resultado[dia] = { abre: $abre.value, cierra: $cierra.value };
      }
      if (!Object.values(resultado).some(Boolean)) return { error: th.ningunDia };
      return { horario: resultado };
    },
  };
}

function hora(hhmm) {
  const [h, m] = hhmm.split(':').map(Number);
  const h12 = h % 12 || 12;
  return `${h12}:${String(m).padStart(2, '0')} ${h < 12 ? 'a. m.' : 'p. m.'}`;
}

// { lun..vie 9–18, sab 9–14, dom null } →
// "Abrimos de lunes a viernes de 9:00 a. m. a 6:00 p. m. y los sábados de 9:00 a. m. a 2:00 p. m. Los domingos descansamos."
export function describirHorario(horario) {
  const tramos = [];
  for (const dia of DIAS) {
    const v = horario[dia];
    const ultimo = tramos.at(-1);
    if (v && ultimo && ultimo.abre === v.abre && ultimo.cierra === v.cierra && ultimo.hasta === DIAS[DIAS.indexOf(dia) - 1]) {
      ultimo.hasta = dia;
    } else if (v) {
      tramos.push({ desde: dia, hasta: dia, abre: v.abre, cierra: v.cierra });
    }
  }
  const partes = tramos.map((r) => {
    const dias = r.desde === r.hasta ? `los ${th.plural[r.desde]}` : `de ${th.singular[r.desde]} a ${th.singular[r.hasta]}`;
    return `${dias} de ${hora(r.abre)} a ${hora(r.cierra)}`;
  });
  const cerrados = DIAS.filter((d) => !horario[d]).map((d) => th.plural[d]);
  // Las horas ya terminan en "m.", así que no se agrega otro punto.
  let texto = partes.length ? `Abrimos ${partes.slice(0, -1).join(', ')}${partes.length > 1 ? ' y ' : ''}${partes.at(-1)}` : '';
  if (cerrados.length) {
    const lista = cerrados.length > 1 ? `${cerrados.slice(0, -1).join(', ')} y ${cerrados.at(-1)}` : cerrados[0];
    texto += ` Los ${lista} descansamos.`;
  }
  return texto.trim();
}
