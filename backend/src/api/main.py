# """
# Point d'entrée principal de l'API FastAPI SÉNTRA.
# Se trouve dans src/api/main.py
# """
# import time
# from contextlib import asynccontextmanager
# from datetime import datetime
# from typing import Generator

# from fastapi import FastAPI, Request, status
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.trustedhost import TrustedHostMiddleware
# from fastapi.middleware.gzip import GZipMiddleware
# from fastapi.responses import JSONResponse
# from fastapi.exceptions import RequestValidationError
# from starlette.exceptions import HTTPException as StarletteHTTPException
# from sqlalchemy.orm import Session
# from src.api.routes import customers  # AJOUTER CETTE LIGNE
# from src.api.routes.stats import router as stats_router
# # Import nécessaire pour la DB, les modèles et le seeding
# from src.database.connection import get_db, engine, Base, SessionLocal
# from src.database.seeding import seed_db 

# from src.core.config import settings
# from src.core.logging import get_logger

# # Import des middlewares de sécurité (Assurez-vous que ces fichiers existent)
# # Note: Ces classes doivent être des implémentations valides de BaseHTTPMiddleware ou de fonctions middleware
# try:
#     from src.api.middlewares.rate_limit import RateLimitMiddleware
#     from src.api.middlewares.security import (
#         SecurityHeadersMiddleware, 
#         RequestIDMiddleware, 
#         ErrorHandlingMiddleware,
#         PerformanceMonitoringMiddleware
#     )
# except ImportError as e:
#     # Ceci est une gestion d'erreur critique au cas où les middlewares n'existent pas encore
#     print(f"Erreur d'importation des middlewares : {e}")
#     # Pour que le code reste runnable sans les middlewares personnalisés:
#     class DummyMiddleware:
#         def __init__(self, app, **kwargs): self.app = app
#         async def __call__(self, scope, receive, send): return await self.app(scope, receive, send)
#     RateLimitMiddleware = DummyMiddleware
#     SecurityHeadersMiddleware = DummyMiddleware
#     RequestIDMiddleware = DummyMiddleware
#     ErrorHandlingMiddleware = DummyMiddleware
#     PerformanceMonitoringMiddleware = DummyMiddleware


# logger = get_logger(__name__)

# # ============================================================================
# # LOGIQUE D'INITIALISATION DE LA BASE DE DONNÉES
# # ============================================================================

# def create_tables():
#     """Crée toutes les tables dans la base de données (si elles n'existent pas)."""
#     try:
#         logger.info("⚙️  Vérification et création des tables de la base de données...")
#         # L'appel à Base.metadata.create_all(bind=engine) est une opération synchrone bloquante.
#         Base.metadata.create_all(bind=engine)
#         logger.info("✅ Tables créées ou déjà existantes.")
#     except Exception as e:
#         logger.critical(f"❌ ERREUR FATALE lors de la création des tables: {e}", exc_info=True)


# def seed_initial_data():
#     """Charge les données initiales (seeding) en utilisant une session dédiée."""
#     if not settings.RUN_DB_SEEDING:
#         logger.info("⏭️  Seeding des données ignoré (RUN_DB_SEEDING=False)")
#         return

#     db: Session = SessionLocal()
#     try:
#         logger.info("🌱 Tentative de seeding des données initiales...")
#         seed_db(db)
#         logger.info("✅ Seeding des données terminé.")
#     except Exception as e:
#         logger.error(f"❌ Erreur lors du seeding: {e}", exc_info=True)
#         db.rollback()
#     finally:
#         db.close()

# # ============================================================================
# # CYCLE DE VIE DE L'APPLICATION (LIFESPAN)
# # ============================================================================

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Gère le cycle de vie de l'application (démarrage/arrêt)."""
#     logger.info("=" * 80)
#     logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} - Démarrage")
#     logger.info("=" * 80)
    
#     # --- Code exécuté au démarrage (Startup) ---
    
#     # 1. Création des tables
#     create_tables()

#     # 2. Seeding des données (si configuré)
#     seed_initial_data()
    
#     logger.info(f"📊 Environnement: {settings.ENVIRONMENT}")
#     logger.info("🛡️  Middlewares activés: (Vérifiez la console pour la liste complète)")

#     yield # L'application commence à servir les requêtes
    
#     # --- Code exécuté à l'arrêt (Shutdown) ---
#     logger.info("=" * 80)
#     logger.info(f"🛑 {settings.APP_NAME} arrêtée proprement")
#     logger.info("=" * 80)

# # ============================================================================
# # APPLICATION FASTAPI
# # ============================================================================

# app = FastAPI(
#     title=settings.APP_NAME,
#     description=settings.APP_DESCRIPTION,
#     version=settings.APP_VERSION,
#     docs_url="/docs",
#     redoc_url="/redoc",
#     openapi_url="/openapi.json",
#     lifespan=lifespan,
#     # Ajouter ces paramètres pour Swagger UI sur Render
#     servers=[
#         {
#             "url": "https://sentra-backend.onrender.com",
#             "description": "Production server"
#         },
#         {
#             "url": "http://localhost:8000",
#             "description": "Local development"
#         }
#     ]
# )

# # ============================================================================
# # MIDDLEWARES OPTIMISÉS (Dans l'ordre d'exécution souhaité)
# # ============================================================================

# # 1. Error Handling (premier à capturer les erreurs)
# app.add_middleware(ErrorHandlingMiddleware)

# # 2. Request ID Tracking
# app.add_middleware(RequestIDMiddleware)

# # 3. Performance Monitoring
# app.add_middleware(PerformanceMonitoringMiddleware, slow_threshold_ms=1000)

# # 4. Rate Limiting
# app.add_middleware(
#     RateLimitMiddleware,
#     requests_per_minute=120,
#     requests_per_hour=2000,
#     burst_size=20
# )

# # 5. Security Headers
# app.add_middleware(SecurityHeadersMiddleware)

# # 6. CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.allowed_origins_list,
#     allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
#     allow_methods=settings.CORS_ALLOW_METHODS.split(","),
#     allow_headers=settings.CORS_ALLOW_HEADERS.split(","),
#     expose_headers=[
#         "X-Request-ID", 
#         "X-Process-Time", 
#         "X-RateLimit-Limit-Minute", 
#         "X-RateLimit-Remaining-Minute", 
#         "X-RateLimit-Limit-Hour", 
#         "X-RateLimit-Remaining-Hour"
#     ]
# )

# # 7. Trusted Host
# allowed_hosts = (
#     ["*"] if settings.ENVIRONMENT == "development" 
#     else settings.allowed_origins_list
# )
# app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

# # 8. GZip Compression
# app.add_middleware(GZipMiddleware, minimum_size=500)

# # ============================================================================
# # MIDDLEWARE POUR OPTIMISER LA DOCUMENTATION
# # ============================================================================

# @app.middleware("http")
# async def optimize_docs_performance(request: Request, call_next):
#     """Optimise les performances de la documentation et la gestion des CSP."""
#     is_docs_path = (
#         request.url.path.startswith(("/docs", "/redoc", "/openapi.json")) or
#         "/static/" in request.url.path or
#         request.url.path == "/favicon.ico"
#     )
    
#     response = await call_next(request)
    
#     if is_docs_path:
#         # Supprime la CSP pour ne pas bloquer les scripts de documentation
#         if "Content-Security-Policy" in response.headers:
#             del response.headers["Content-Security-Policy"]
        
#         # Ajoute le cache pour les fichiers statiques de la doc
#         if "/static/" in request.url.path:
#             response.headers["Cache-Control"] = "public, max-age=3600"
    
#     return response

# # ============================================================================
# # GESTIONNAIRES D'EXCEPTIONS
# # ============================================================================

# @app.exception_handler(StarletteHTTPException)
# async def http_exception_handler(request: Request, exc: StarletteHTTPException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={
#             "error": exc.detail,
#             "status_code": exc.status_code,
#             "path": str(request.url.path),
#             "timestamp": datetime.now().isoformat()
#         }
#     )

# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     return JSONResponse(
#         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#         content={
#             "error": "Validation error",
#             "details": exc.errors(),
#             "path": str(request.url.path),
#             "timestamp": datetime.now().isoformat()
#         }
#     )

# @app.exception_handler(Exception)
# async def general_exception_handler(request: Request, exc: Exception):
#     logger.error(f"❌ Erreur non gérée: {str(exc)}", exc_info=True)
#     return JSONResponse(
#         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         content={
#             "error": "Internal server error",
#             "message": str(exc) if settings.ENVIRONMENT == "development" else "An error occurred",
#             "path": str(request.url.path),
#             "timestamp": datetime.now().isoformat()
#         }
#     )

# # ============================================================================
# # CHARGEMENT DES ROUTES
# # ============================================================================

# # NOTE: L'utilisation des blocs try/except est une bonne pratique pour 
# # le chargement des modules de routes afin d'éviter qu'une seule erreur
# # n'empêche le reste de l'application de démarrer.

# # ============================================================================
# # CHARGEMENT DES ROUTES - SECTION CORRIGÉE
# # ============================================================================


# # ============================================================================
# # CHARGEMENT DES ROUTES
# # ============================================================================

# def include_routers():
#     """Charge tous les routeurs d'API."""
    
#     # Importez MANUELLEMENT chaque routeur
#     try:
#         from src.api.routes.health import router as health_router
#         from src.api.routes.detection_pro import router as detection_router
#         from src.api.routes.metrics import router as metrics_router
#         from src.api.routes.customers import router as customers_router
#         from src.api.routes.transactions import router as transactions_router
        
#         # stats_router est déjà importé en haut du fichier
        
#         routers = [
#             (health_router, "", "santé"),
#             (detection_router, "", "détection"),
#             (metrics_router, "", "métriques"),
#             (customers_router, "/customers", "clients"),
#             (transactions_router, "/transactions", "transactions"),
#             (stats_router, "/stats", "statistiques"),
#         ]
        
#         for router_obj, prefix_suffix, tag in routers:
#             full_prefix = f"{settings.API_PREFIX}{prefix_suffix}"
#             app.include_router(router_obj, prefix=full_prefix, tags=[tag])
#             logger.info(f"✅ Routes '{tag}' chargées - Prefix: {full_prefix}")
            
#     except ImportError as e:
#         logger.error(f"❌ Erreur importation routeurs: {e}")

# include_routers()


# # ============================================================================
# # ROUTES GLOBALES
# # ============================================================================

# @app.get("/", tags=["racine"])
# async def root():
#     return {
#         "service": settings.APP_NAME,
#         "version": settings.APP_VERSION,
#         "environment": settings.ENVIRONMENT,
#         "status": "operational",
#         "timestamp": datetime.now().isoformat(),
#         "endpoints": {
#             "documentation": "/docs",
#             "redoc": "/redoc",
#             "api_prefix": settings.API_PREFIX
#         }
#     }

# @app.get("/health", tags=["santé"])
# async def health_check():
#     """Vérification de la santé simple de l'application."""
#     return {
#         "status": "healthy",
#         "service": settings.APP_NAME,
#         "version": settings.APP_VERSION,
#         "timestamp": datetime.now().isoformat()
#     }

# # ============================================================================
# # POINT D'ENTRÉE (Pour exécution directe avec Python)
# # ============================================================================

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "src.api.main:app",
#         host="0.0.0.0",
#         port=settings.API_PORT,
#         reload=settings.ENVIRONMENT == "development",
#         log_level=settings.LOG_LEVEL.lower(),
#         access_log=False
#     )


"""
Point d'entrée principal de l'API FastAPI SÉNTRA.
Se trouve dans src/api/main.py
"""
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Generator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session

# Import des routeurs
from src.api.routes.stats import router as stats_router

# Import nécessaire pour la DB, les modèles et le seeding
from src.database.connection import get_db, engine, Base, SessionLocal
from src.database.seeding import seed_db 

from src.core.config import settings
from src.core.logging import get_logger

# Import des middlewares de sécurité
try:
    from src.api.middlewares.rate_limit import RateLimitMiddleware
    from src.api.middlewares.security import (
        SecurityHeadersMiddleware, 
        RequestIDMiddleware, 
        ErrorHandlingMiddleware,
        PerformanceMonitoringMiddleware
    )
except ImportError as e:
    # Gestion d'erreur pour les middlewares
    print(f"⚠️  Middlewares non trouvés: {e}")
    # Middlewares factices pour le développement
    class DummyMiddleware:
        def __init__(self, app, **kwargs): self.app = app
        async def __call__(self, scope, receive, send): return await self.app(scope, receive, send)
    RateLimitMiddleware = DummyMiddleware
    SecurityHeadersMiddleware = DummyMiddleware
    RequestIDMiddleware = DummyMiddleware
    ErrorHandlingMiddleware = DummyMiddleware
    PerformanceMonitoringMiddleware = DummyMiddleware


logger = get_logger(__name__)

# ============================================================================
# LOGIQUE D'INITIALISATION DE LA BASE DE DONNÉES
# ============================================================================

def create_tables():
    """Crée toutes les tables dans la base de données (si elles n'existent pas)."""
    try:
        logger.info("⚙️  Vérification et création des tables de la base de données...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables créées ou déjà existantes.")
    except Exception as e:
        logger.critical(f"❌ ERREUR FATALE lors de la création des tables: {e}", exc_info=True)


def seed_initial_data():
    """Charge les données initiales (seeding) en utilisant une session dédiée."""
    if not settings.RUN_DB_SEEDING:
        logger.info("⏭️  Seeding des données ignoré (RUN_DB_SEEDING=False)")
        return

    db: Session = SessionLocal()
    try:
        logger.info("🌱 Tentative de seeding des données initiales...")
        seed_db(db)
        logger.info("✅ Seeding des données terminé.")
    except Exception as e:
        logger.error(f"❌ Erreur lors du seeding: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()

# ============================================================================
# CYCLE DE VIE DE L'APPLICATION (LIFESPAN)
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le cycle de vie de l'application (démarrage/arrêt)."""
    logger.info("=" * 80)
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} - Démarrage")
    logger.info("=" * 80)
    
    # --- Code exécuté au démarrage (Startup) ---
    
    # 1. Création des tables
    create_tables()

    # 2. Seeding des données (si configuré)
    seed_initial_data()
    
    logger.info(f"📊 Environnement: {settings.ENVIRONMENT}")
    logger.info(f"🌐 Déployé sur Render: {settings.is_render}")
    logger.info(f"🔗 Origines CORS autorisées: {settings.allowed_origins_list}")
    logger.info("🛡️  Middlewares activés")

    yield # L'application commence à servir les requêtes
    
    # --- Code exécuté à l'arrêt (Shutdown) ---
    logger.info("=" * 80)
    logger.info(f"🛑 {settings.APP_NAME} arrêtée proprement")
    logger.info("=" * 80)

# ============================================================================
# APPLICATION FASTAPI
# ============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    # Configuration des serveurs pour Swagger
    servers=[
        {
            "url": "https://sentra-backend.onrender.com",
            "description": "Production server (Render)"
        },
        {
            "url": "http://localhost:8000",
            "description": "Local development"
        }
    ] if settings.is_render else None
)

# ============================================================================
# MIDDLEWARES OPTIMISÉS (Dans l'ordre d'exécution souhaité)
# ============================================================================

# 1. Error Handling (premier à capturer les erreurs)
app.add_middleware(ErrorHandlingMiddleware)

# 2. Request ID Tracking
app.add_middleware(RequestIDMiddleware)

# 3. Performance Monitoring
app.add_middleware(PerformanceMonitoringMiddleware, slow_threshold_ms=1000)

# 4. Rate Limiting
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=120,
    requests_per_hour=2000,
    burst_size=20
)

# 5. Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# 6. CORS - CONFIGURATION AMÉLIORÉE POUR RENDER
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.cors_allow_methods_list,
    allow_headers=settings.cors_allow_headers_list,
    expose_headers=[
        "X-Request-ID", 
        "X-Process-Time", 
        "X-RateLimit-Limit", 
        "X-RateLimit-Remaining",
        "X-Response-Time"
    ]
)

# 7. Trusted Host
allowed_hosts = (
    ["*"] if settings.is_development 
    else settings.allowed_origins_list
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

# 8. GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=500)

# ============================================================================
# MIDDLEWARE POUR OPTIMISER LA DOCUMENTATION
# ============================================================================

@app.middleware("http")
async def optimize_docs_performance(request: Request, call_next):
    """Optimise les performances de la documentation et la gestion des CSP."""
    is_docs_path = (
        request.url.path.startswith(("/docs", "/redoc", "/openapi.json")) or
        "/static/" in request.url.path or
        request.url.path == "/favicon.ico"
    )
    
    response = await call_next(request)
    
    if is_docs_path:
        # Supprime la CSP pour ne pas bloquer les scripts de documentation
        if "Content-Security-Policy" in response.headers:
            del response.headers["Content-Security-Policy"]
        
        # Ajoute le cache pour les fichiers statiques de la doc
        if "/static/" in request.url.path:
            response.headers["Cache-Control"] = "public, max-age=3600"
    
    return response

# ============================================================================
# GESTIONNAIRES D'EXCEPTIONS
# ============================================================================

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path),
            "timestamp": datetime.now().isoformat(),
            "request_id": request.headers.get("X-Request-ID", "unknown")
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "details": exc.errors(),
            "path": str(request.url.path),
            "timestamp": datetime.now().isoformat(),
            "request_id": request.headers.get("X-Request-ID", "unknown")
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Erreur non gérée: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.is_development else "An error occurred",
            "path": str(request.url.path),
            "timestamp": datetime.now().isoformat(),
            "request_id": request.headers.get("X-Request-ID", "unknown")
        }
    )

# ============================================================================
# CHARGEMENT DES ROUTES
# ============================================================================

def include_routers():
    """Charge tous les routeurs d'API."""
    
    try:
        from src.api.routes.health import router as health_router
        from src.api.routes.detection_pro import router as detection_router
        from src.api.routes.metrics import router as metrics_router
        from src.api.routes.customers import router as customers_router
        from src.api.routes.transactions import router as transactions_router
        
        routers = [
            (health_router, "", "santé"),
            (detection_router, "", "détection"),
            (metrics_router, "", "métriques"),
            (customers_router, "/customers", "clients"),
            (transactions_router, "/transactions", "transactions"),
            (stats_router, "/stats", "statistiques"),
        ]
        
        for router_obj, prefix_suffix, tag in routers:
            full_prefix = f"{settings.API_PREFIX}{prefix_suffix}"
            app.include_router(router_obj, prefix=full_prefix, tags=[tag])
            logger.info(f"✅ Routes '{tag}' chargées - Prefix: {full_prefix}")
            
    except ImportError as e:
        logger.error(f"❌ Erreur importation routeurs: {e}")
        raise

include_routers()

# ============================================================================
# ROUTES GLOBALES
# ============================================================================

@app.get("/", tags=["racine"])
async def root():
    """Endpoint racine avec informations sur le déploiement."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "deployment": {
            "platform": "Render" if settings.is_render else "Local",
            "frontend_url": "https://sentra-frontend.onrender.com" if settings.is_render else "http://localhost:3000",
            "api_url": "https://sentra-backend.onrender.com" if settings.is_render else "http://localhost:8000",
        },
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "documentation": "/docs",
            "redoc": "/redoc",
            "api": settings.API_PREFIX,
            "health": f"{settings.API_PREFIX}/health"
        }
    }

@app.get("/health", tags=["santé"])
@app.get("/api/v1/health", tags=["santé"])
async def health_check():
    """Vérification complète de la santé de l'application."""
    import psutil
    
    health_status = "healthy"
    checks = {}
    
    # Check 1: Database
    try:
        db: Session = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
        health_status = "degraded"
    
    # Check 2: Redis
    try:
        import redis
        if settings.REDIS_URL:
            redis_client = redis.from_url(settings.REDIS_URL)
            redis_client.ping()
            checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)}"
        health_status = "degraded"
    
    # Check 3: System resources
    checks["system"] = {
        "memory_usage": f"{psutil.virtual_memory().percent}%",
        "cpu_usage": f"{psutil.cpu_percent()}%"
    }
    
    return {
        "status": health_status,
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now().isoformat(),
        "checks": checks,
        "deployment": {
            "platform": "Render" if settings.is_render else "Local",
            "cors_configured": True,
            "cors_origins": settings.allowed_origins_list
        }
    }

@app.get("/api/v1/deployment-info", tags=["debug"])
async def deployment_info(request: Request):
    """Information sur le déploiement pour le débogage."""
    return {
        "is_render": settings.is_render,
        "environment": settings.ENVIRONMENT,
        "cors_origins": settings.allowed_origins_list,
        "request_origin": request.headers.get("origin"),
        "allowed_methods": settings.cors_allow_methods_list,
        "headers_received": dict(request.headers),
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# POINT D'ENTRÉE (Pour exécution directe avec Python)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=False
    )