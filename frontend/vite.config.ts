import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// 获取仓库名称用于GitHub Pages的base路径
const repoName = process.env.GITHUB_REPOSITORY?.split('/')[1] || 'EventPredictor'
const isGitHubPages = process.env.GITHUB_PAGES === 'true'

export default defineConfig({
  plugins: [react()],
  base: isGitHubPages ? `/${repoName}/` : '/',
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          charts: ['recharts'],
          globe: ['react-globe.gl']
        }
      }
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8005',
        changeOrigin: true
      }
    }
  }
})
