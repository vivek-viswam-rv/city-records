import { fileURLToPath } from 'node:url'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const src = (dir) => fileURLToPath(new URL(`./src/${dir}`, import.meta.url))

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      apis: src('apis'),
      hooks: src('hooks'),
      components: src('components'),
      utils: src('utils'),
      constants: src('constants'),
      lib: src('lib'),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
