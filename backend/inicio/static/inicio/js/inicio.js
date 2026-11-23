// Página de inicio: portada animada, chat de ejemplo, QR, notas del panel, fotos y preguntas.
(() => {
  const sinMovimiento = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const csrf = document.querySelector('meta[name="csrf-token"]')?.content ?? '';
  const espera = (ms) => new Promise((r) => setTimeout(r, ms));

  // Cada parte de una sección aparece un poco después de la anterior.
  const observador = new IntersectionObserver((entradas) => {
    for (const e of entradas) {
      if (!e.isIntersecting) continue;
      e.target.classList.add('visible');
      observador.unobserve(e.target);
    }
  }, { rootMargin: '0px 0px -8% 0px' });
  document.querySelectorAll('main > section').forEach(($s) => {
    $s.querySelectorAll('.revelar').forEach(($r, i) => {
      $r.style.setProperty('--retraso', `${Math.min(i, 6) * 80}ms`);
      observador.observe($r);
    });
  });

  // Portada: el escenario se abre y los mensajes de las 11:42 p. m. llegan uno por uno.
  const $escenario = document.getElementById('escenario');
  const $pasos = [...document.querySelectorAll('.portada [data-paso]')].sort((a, b) => a.dataset.paso - b.dataset.paso);
  const $escribiendo = document.querySelector('.portada .wa-escribiendo');
  (async () => {
    requestAnimationFrame(() => $escenario.classList.add('abierto'));
    if (sinMovimiento) return $pasos.forEach(($p) => $p.classList.add('visto'));
    await espera(1100);
    for (const $p of $pasos) {
      const esNegocio = $p.classList.contains('wa-negocio');
      if (esNegocio) {
        $p.before($escribiendo);
        $escribiendo.classList.add('activo');
        await espera(900);
        $escribiendo.classList.remove('activo');
      }
      $p.classList.add('visto');
      await espera(esNegocio ? 700 : 500);
    }
  })();

  // Chat de ejemplo con los negocios de la demo -------------------------------
  const $prueba = document.getElementById('prueba');
  const textos = $prueba.dataset;
  const $mensajes = document.getElementById('demo-mensajes');
  const $entrada = document.getElementById('demo-entrada');
  const $estado = document.getElementById('demo-estado');
  const $abrir = document.getElementById('demo-abrir');
  const elegido = document.querySelector('input[name="negocio"]:checked');
  const demo = { slug: elegido?.value, hora: '', token: null, version: 0 };

  async function pedir(url, datos) {
    const r = await fetch(url, datos === undefined ? {} : {
      method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf }, body: JSON.stringify(datos),
    });
    if (!r.ok) throw new Error(r.status);
    return r.json();
  }
  const estadoDe = (slug) => pedir(`/chat/${slug}/estado/${demo.hora ? `?hora=${demo.hora}` : ''}`);

  function horaVisible(fecha) {
    if (demo.hora) {
      const [h, m] = demo.hora.split(':').map(Number);
      return `${h % 12 || 12}:${String(m).padStart(2, '0')} ${h < 12 ? 'a. m.' : 'p. m.'}`;
    }
    return new Date(fecha ?? Date.now()).toLocaleTimeString('es-MX', { hour: 'numeric', minute: '2-digit' });
  }

  function quitarOpciones() {
    $mensajes.querySelectorAll('.wa-opciones').forEach(($o) => $o.remove());
    // La lista que mostraban los botones vuelve a escribirse en su burbuja.
    $mensajes.querySelectorAll('[data-completo]').forEach(($v) => {
      $v.firstChild.nodeValue = $v.dataset.completo;
      delete $v.dataset.completo;
    });
  }

  function burbuja({ autor, texto, creado_en, opciones }) {
    quitarOpciones();
    const $b = document.createElement('p');
    $b.className = `wa-burbuja ${autor === 'cliente' ? 'wa-cliente' : 'wa-negocio'}`;
    // Con botones a la vista, la lista numerada sobra.
    $b.textContent = opciones?.length
      ? texto.split('\n').filter((l) => !/^\d{1,2}\. /.test(l) && l !== 'Escríbeme el número o tu pregunta.').join('\n').trim()
      : texto;
    if ($b.textContent !== texto) $b.dataset.completo = texto;
    const $h = document.createElement('span');
    $h.textContent = horaVisible(creado_en);
    $b.append($h);
    $mensajes.append($b);
    if (opciones?.length) {
      const $fila = document.createElement('div');
      $fila.className = 'wa-opciones';
      for (const { pregunta, enviar = pregunta } of opciones) {
        const $o = document.createElement('button');
        $o.type = 'button';
        $o.className = 'wa-opcion';
        $o.textContent = pregunta;
        $o.addEventListener('click', () => enviarDemo(enviar));
        $fila.append($o);
      }
      $mensajes.append($fila);
    }
    $mensajes.scrollTop = $mensajes.scrollHeight;
    return $b;
  }

  const iniciales = (nombre) => nombre.split(/\s+/).filter((p) => p.length > 2).slice(0, 2).map((p) => p[0].toUpperCase()).join('');

  // El QR lo arma el servidor; aquí solo se muestra el del negocio elegido.
  function mostrarQr() {
    document.querySelectorAll('[data-qr]').forEach(($q) => { $q.hidden = $q.dataset.qr !== demo.slug; });
    const nombre = document.querySelector(`input[name="negocio"][value="${demo.slug}"]`)?.closest('label')?.textContent.trim() ?? '';
    document.getElementById('demo-qr-nombre').textContent = nombre;
  }

  async function cargarDemo() {
    if (!demo.slug) return;
    const version = ++demo.version;
    demo.token = null;
    $mensajes.replaceChildren();
    $abrir.href = `/chat/${demo.slug}/${demo.hora ? `?hora=${demo.hora}` : ''}`;
    mostrarQr();
    let datos;
    try {
      datos = await estadoDe(demo.slug);
    } catch {
      if (version === demo.version) $estado.textContent = textos.sinConexion;
      return;
    }
    if (version !== demo.version) return;
    document.getElementById('demo-nombre').textContent = datos.nombre;
    document.getElementById('demo-avatar').textContent = iniciales(datos.nombre);
    $estado.textContent = datos.estado;
    burbuja({
      autor: 'asistente',
      texto: datos.bienvenida,
      opciones: [...(datos.sugerencias ?? []).map((pregunta) => ({ pregunta })), { pregunta: textos.hablarPersona, enviar: 'persona' }],
    });
  }

  async function enviarDemo(texto) {
    texto = texto.trim();
    if (!texto) return;
    const version = demo.version;
    const $mio = burbuja({ autor: 'cliente', texto });
    $mio.style.opacity = '0.6';
    $estado.textContent = textos.escribiendo;
    try {
      if (!demo.token) demo.token = (await pedir(`/chat/${demo.slug}/iniciar/`, {})).token;
      const respuesta = await pedir('/chat/enviar/', { token: demo.token, texto, hora: demo.hora || null });
      if (version !== demo.version) return;
      $mio.style.opacity = '';
      const r = respuesta.find((m) => m.autor === 'asistente');
      if (r) burbuja(r);
    } catch {
      if (version !== demo.version) return;
      $mio.style.opacity = '';
      burbuja({ autor: 'asistente', texto: textos.noSeEnvio });
    }
    try {
      const datos = await estadoDe(demo.slug);
      if (version === demo.version) $estado.textContent = datos.estado;
    } catch { /* se queda el estado anterior */ }
  }

  document.getElementById('demo-formulario').addEventListener('submit', (e) => {
    e.preventDefault();
    const texto = $entrada.value;
    $entrada.value = '';
    enviarDemo(texto);
  });
  document.querySelectorAll('input[name="negocio"]').forEach(($r) => $r.addEventListener('change', () => {
    demo.slug = $r.value;
    cargarDemo();
  }));
  document.querySelectorAll('input[name="hora"]').forEach(($r) => $r.addEventListener('change', () => {
    demo.hora = $r.value;
    cargarDemo();
  }));
  document.querySelectorAll('.pista').forEach(($p) => $p.addEventListener('click', () => enviarDemo($p.dataset.texto)));

  // El chat de ejemplo se carga cuando el visitante se acerca, no al abrir la página.
  new IntersectionObserver((entradas, obs) => {
    if (!entradas.some((e) => e.isIntersecting)) return;
    obs.disconnect();
    cargarDemo();
  }, { rootMargin: '400px 0px' }).observe($prueba);

  // Panel con notas: al pasar por una nota, se resalta su parte del panel.
  const $panel = document.querySelector('.panel');
  document.querySelectorAll('.nota').forEach(($n) => {
    const encender = () => {
      $panel.classList.add('enfocado');
      $panel.querySelectorAll('[data-parte]').forEach(($p) => $p.classList.toggle('foco', $p.dataset.parte === $n.dataset.apunta));
    };
    const apagar = () => $panel.classList.remove('enfocado');
    $n.addEventListener('mouseenter', encender);
    $n.addEventListener('focus', encender);
    $n.addEventListener('mouseleave', apagar);
    $n.addEventListener('blur', apagar);
  });

  // Copiar el enlace de ejemplo.
  const $copiar = document.getElementById('copiar-enlace');
  $copiar.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText($copiar.dataset.enlace);
      const antes = $copiar.textContent;
      $copiar.textContent = $copiar.dataset.copiado;
      setTimeout(() => { $copiar.textContent = antes; }, 1800);
    } catch { /* sin permiso para copiar: el enlace sigue a la vista */ }
  });

  // Para quién: la foto cambia con el giro que se está leyendo.
  const $fotos = document.querySelectorAll('.para-foto img');
  const mostrarFoto = (nombre) => $fotos.forEach(($f) => $f.classList.toggle('activa', $f.dataset.foto === nombre));
  const observaGrupos = new IntersectionObserver((entradas) => {
    for (const e of entradas) if (e.isIntersecting && e.target.dataset.foto) mostrarFoto(e.target.dataset.foto);
  }, { rootMargin: '-45% 0px -45% 0px' });
  document.querySelectorAll('.grupo').forEach(($g) => {
    $g.addEventListener('mouseenter', () => { if ($g.dataset.foto) mostrarFoto($g.dataset.foto); });
    observaGrupos.observe($g);
  });

  // Preguntas: una respuesta grande a la derecha (en celular, abajo de la pregunta).
  const $grande = document.getElementById('respuesta-grande');
  const $botones = [...document.querySelectorAll('#lista-preguntas button')];
  function elegir($b) {
    if ($b.getAttribute('aria-expanded') === 'true') return;
    for (const $o of $botones) {
      const si = $o === $b;
      $o.setAttribute('aria-expanded', String(si));
      document.getElementById($o.getAttribute('aria-controls')).hidden = !si;
    }
    const texto = document.getElementById($b.getAttribute('aria-controls')).textContent;
    $grande.classList.add('cambiando');
    setTimeout(() => { $grande.textContent = texto; $grande.classList.remove('cambiando'); }, sinMovimiento ? 0 : 150);
  }
  $botones.forEach(($b) => {
    $b.addEventListener('click', () => elegir($b));
    $b.addEventListener('focus', () => elegir($b));
    $b.addEventListener('mouseenter', () => { if (matchMedia('(hover: hover)').matches) elegir($b); });
  });

  // Menú lateral en celular: al elegir una sección se cierra y, ya cerrado, baja hasta ella
  // (mientras está abierto, Bootstrap bloquea el desplazamiento de la página).
  const $lateral = document.getElementById('lateral');
  $lateral.querySelectorAll('.lateral-enlaces a').forEach(($a) => $a.addEventListener('click', (e) => {
    const menu = bootstrap.Offcanvas.getInstance($lateral);
    if (!$lateral.classList.contains('show') || !menu) return;
    e.preventDefault();
    $lateral.addEventListener('hidden.bs.offcanvas', () => {
      document.querySelector($a.hash)?.scrollIntoView({ behavior: sinMovimiento ? 'auto' : 'smooth' });
      history.replaceState(null, '', $a.hash);
    }, { once: true });
    menu.hide();
  }));
})();
