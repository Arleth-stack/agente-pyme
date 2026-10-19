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
