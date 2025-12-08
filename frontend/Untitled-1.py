
"""
Point d'entrée principal de l'API FastAPI SÉNTRA - Version CORRIGÉE

il se trouve dans src/api/main.py
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
# Import nécessaire pour le seeding et la configuration de la DB
from src.database.connection import get_db, engine, Base
from src.database.seeding import seed_db # <-- NOUVEL IMPORT

from src.core.config import settings
from src.core.logging import get_logger

# Import des middlewares de sécurité
from src.api.middlewares.rate_limit import RateLimitMiddleware
from src.api.middlewares.security import (
    SecurityHeadersMiddleware, 
    RequestIDMiddleware, 
    ErrorHandlingMiddleware,
    PerformanceMonitoringMiddleware
)

logger = get_logger(__name__)

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
)

# ============================================================================
# MIDDLEWARES OPTIMISÉS
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

# 6. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS.split(","),
    allow_headers=settings.CORS_ALLOW_HEADERS.split(","),
    expose_headers=[
        "X-Request-ID", 
        "X-Process-Time", 
        "X-RateLimit-Limit-Minute", 
        "X-RateLimit-Remaining-Minute", 
        "X-RateLimit-Limit-Hour", 
        "X-RateLimit-Remaining-Hour"
    ]
)

# 7. Trusted Host
allowed_hosts = (
    ["*"] if settings.ENVIRONMENT == "development" 
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
    """Optimise les performances de la documentation"""
    is_docs_path = (
        request.url.path.startswith(("/docs", "/redoc", "/openapi.json")) or
        "/static/" in request.url.path or
        request.url.path == "/favicon.ico"
    )
    
    response = await call_next(request)
    
    if is_docs_path:
        if "Content-Security-Policy" in response.headers:
            del response.headers["Content-Security-Policy"]
        
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
            "timestamp": datetime.now().isoformat()
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
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Erreur non gérée: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.ENVIRONMENT == "development" else "An error occurred",
            "path": str(request.url.path),
            "timestamp": datetime.now().isoformat()
        }
    )

# ============================================================================
# CHARGEMENT DES ROUTES - VERSION SIMPLIFIÉE ET FIABLE
# ============================================================================

try:
    from src.api.routes.health import router as health_router
    app.include_router(health_router, prefix=settings.API_PREFIX, tags=["santé"])
    logger.info("✅ Routes santé chargées")
except Exception as e:
    logger.error(f"❌ Erreur santé: {e}")

try:
    from src.api.routes.detection_pro import router as detection_router
    app.include_router(detection_router, prefix=settings.API_PREFIX, tags=["détection"])
    logger.info("✅ Routes détection PRO chargées")
except Exception as e:
    logger.error(f"❌ Erreur détection: {e}")

try:
    from src.api.routes.transactions import router as transactions_router
    app.include_router(transactions_router, prefix=settings.API_PREFIX, tags=["transactions"])
    logger.info("✅ Routes transactions chargées")
except Exception as e:
    logger.error(f"❌ Erreur transactions: {e}")

try:
    from src.api.routes.metrics import router as metrics_router
    app.include_router(metrics_router, prefix=settings.API_PREFIX, tags=["métriques"])
    logger.info("✅ Routes métriques chargées")
except Exception as e:
    logger.error(f"❌ Erreur métriques: {e}")

# ============================================================================
# ROUTES GLOBALES
# ============================================================================

@app.get("/", tags=["racine"])
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "documentation": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "status": "/status",
            "api": settings.API_PREFIX
        }
    }

@app.get("/health", tags=["santé"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status", tags=["santé"])
async def detailed_status():
    return {
        "status": "operational",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now().isoformat(),
        "features": [
            "Real-time fraud detection",
            "Machine Learning powered", 
            "Advanced analytics",
            "Security hardened"
        ]
    }

# ============================================================================
# ÉVÉNEMENTS LIFECYCLE
# ============================================================================

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 80)
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 80)

    # ----------------------------------------------------
    # NOUVELLE LOGIQUE : BASE DE DONNÉES
    # ----------------------------------------------------
    try:
        # 1. Création des tables si elles n'existent pas
        logger.info("⚙️  Vérification et création des tables de la base de données...")
        Base.metadata.create_all(bind=engine)
        
        # 2. Seeding des données réelles (via l'ETL)
        # On passe une session de DB au script de seeding
        db_session = next(get_db())
        seed_db(db_session)
        # NOTE: Le script seed_db ferme déjà la session.
        
    except Exception as e:
        logger.critical(f"❌ ERREUR FATALE au démarrage de la DB/Seeding : {e}", exc_info=True)
        # Selon le niveau de criticité, on pourrait choisir de laisser l'API démarrer
        # mais ici, l'absence de DB est considérée comme bloquante.
    # ----------------------------------------------------

    logger.info(f"📊 Environnement: {settings.ENVIRONMENT}")
    logger.info(f"🔗 Documentation: http://localhost:{settings.API_PORT}/docs")
    logger.info(f"🔗 ReDoc: http://localhost:{settings.API_PORT}/redoc")
   
    logger.info("")
    logger.info("🛡️  Middlewares activés:")
    logger.info("   ✓ Error Handling")
    logger.info("   ✓ Request ID Tracing") 
    logger.info("   ✓ Performance Monitoring")
    logger.info("   ✓ Rate Limiting (120/min, 2000/h)")
    logger.info("   ✓ Security Headers")
    logger.info("   ✓ CORS Protection")
    logger.info("   ✓ GZip Compression")
    logger.info("=" * 80)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("=" * 80)
    logger.info(f"🛑 {settings.APP_NAME} arrêtée proprement")
    logger.info("=" * 80)

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
        access_log=False
    )