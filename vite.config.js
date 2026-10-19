import { defineConfig } from 'vite';

// Dos páginas por ahora; cada ticket agrega la suya.
const paginas = {
  main: 'index.html',
  chat: 'chat.html',
};

// En desarrollo, /chat/salon-bella sirve chat.html (en Vercel lo hace vercel.json).
const rutasLimpias = {
  name: 'rutas-limpias',
  configureServer(server) {
    server.middlewares.use((req, _res, next) => {
      if (/^\/chat\/[a-z0-9-]+\/?(\?.*)?$/.test(req.url)) req.url = '/chat.html';
      next();
    });
  },
};

export default defineConfig({
  plugins: [rutasLimpias],
  build: { rollupOptions: { input: paginas } },
});
