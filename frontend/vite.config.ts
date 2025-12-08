// import { defineConfig } from 'vite'
// import react from '@vitejs/plugin-react'
// import path from 'path'

// export default defineConfig({
//   plugins: [react()],
//   resolve: {
//     alias: {
//       '@': path.resolve(__dirname, './src'),
//     },
//   },
//   // ⚠️ SUPPRIMER TOUTE LA SECTION SERVER ⚠️
//   // server: {
//   //   host: true,
//   //   port: 3000,
//   // },
  
//   // Build optimisé pour Render
//   build: {
//     outDir: 'dist',
//     sourcemap: false,
//     // Optimisations supplémentaires
//     rollupOptions: {
//       output: {
//         manualChunks: {
//           vendor: ['react', 'react-dom', 'react-router-dom'],
//           ui: ['@radix-ui/react-icons', 'class-variance-authority'],
//         }
//       }
//     }
//   },
  
//   // IMPORTANT pour Render : base path
//   base: './',
  
//   // Variables d'environnement
//   define: {
//     'import.meta.env.VITE_RENDER': JSON.stringify(process.env.VITE_RENDER || 'false'),
//   }
// })

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  
  // Build optimisé pour Render
  build: {
    outDir: 'dist',
    sourcemap: false,
    chunkSizeWarningLimit: 1500, // AUGMENTÉ à 1500kB pour éviter le warning
    // Optimisations supplémentaires
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          ui: ['@radix-ui/react-icons', 'class-variance-authority'],
          charts: ['recharts', 'd3-scale', 'd3-shape'], // AJOUTÉ pour séparer les charts
        }
      }
    }
  },
  
  // IMPORTANT pour Render : base path
  base: './',
  
  // Prévisualisation pour tests locaux
  preview: {
    port: 4173,
    host: true,
  }
})