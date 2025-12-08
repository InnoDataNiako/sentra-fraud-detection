# ===========================================
# Script : create_frontend_structure.ps1
# Projet : SÉNTRA Fraud Detection (frontend)
# ===========================================

# Crée la structure principale
New-Item -ItemType Directory -Force -Path src\components
New-Item -ItemType Directory -Force -Path src\pages
New-Item -ItemType Directory -Force -Path src\layouts
New-Item -ItemType Directory -Force -Path src\hooks
New-Item -ItemType Directory -Force -Path src\context
New-Item -ItemType Directory -Force -Path src\services
New-Item -ItemType Directory -Force -Path src\api
New-Item -ItemType Directory -Force -Path src\types
New-Item -ItemType Directory -Force -Path src\utils
New-Item -ItemType Directory -Force -Path src\styles
New-Item -ItemType Directory -Force -Path src\assets\icons
New-Item -ItemType Directory -Force -Path src\assets\images

# Exemple de fichiers initiaux
New-Item -ItemType File -Force -Path src\api\index.ts
New-Item -ItemType File -Force -Path src\context\AppContext.tsx
New-Item -ItemType File -Force -Path src\hooks\useFetch.ts
New-Item -ItemType File -Force -Path src\services\fraudService.ts
New-Item -ItemType File -Force -Path src\utils\formatDate.ts
New-Item -ItemType File -Force -Path src\styles\global.css
New-Item -ItemType File -Force -Path src\types\fraud.ts
New-Item -ItemType File -Force -Path src\layouts\DashboardLayout.tsx
New-Item -ItemType File -Force -Path src\pages\Home.tsx
New-Item -ItemType File -Force -Path src\pages\Login.tsx
New-Item -ItemType File -Force -Path src\pages\Dashboard.tsx
New-Item -ItemType File -Force -Path src\components\Navbar.tsx
New-Item -ItemType File -Force -Path src\components\Sidebar.tsx
New-Item -ItemType File -Force -Path src\components\FraudChart.tsx
New-Item -ItemType File -Force -Path src\components\Loader.tsx

Write-Host "`n✅ Structure frontend SÉNTRA créée avec succès !" -ForegroundColor Green