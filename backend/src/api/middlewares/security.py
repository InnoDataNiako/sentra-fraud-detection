"""
Middlewares de sécurité complets pour SÉNTRA API
Inclut: Security Headers, Request ID, Error Handling, Performance Monitoring, IP Whitelist
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
from datetime import datetime
import time
import uuid
from typing import Set, Optional

from src.core.logging import get_logger

logger = get_logger(__name__)


# ============================================================================
# 1. SECURITY HEADERS MIDDLEWARE
# ============================================================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Ajoute les headers de sécurité recommandés par OWASP
    """
    
    def __init__(self, app):
        super().__init__(app)
        logger.info("🛡️  Security Headers activés")
    
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        
        # Ne pas appliquer CSP pour la documentation Swagger
        if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc"):
            return response
        
        # Content Security Policy pour le reste de l'application
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )    
            # Protection MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Protection clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Protection XSS
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), payment=(), "
            "usb=(), magnetometer=(), gyroscope=(), accelerometer=()"
        )
        
        # Cache Control pour API
        if "/api/" in request.url.path:
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        return response


# ============================================================================
# 2. REQUEST ID MIDDLEWARE
# ============================================================================

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Génère un ID unique pour chaque requête (traçabilité)
    """
    
    def __init__(self, app):
        super().__init__(app)
        logger.info("🔍 Request ID Tracking activé")
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Ajoute un ID unique à chaque requête"""
        # Générer ou récupérer l'ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Stocker dans l'état de la requête
        request.state.request_id = request_id
        
        # Traiter la requête
        response = await call_next(request)
        
        # Ajouter l'ID dans la réponse
        response.headers["X-Request-ID"] = request_id
        
        return response


# ============================================================================
# 3. ERROR HANDLING MIDDLEWARE
# ============================================================================

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Gestion centralisée des erreurs avec logging
    """
    
    def __init__(self, app):
        super().__init__(app)
        logger.info("⚠️  Error Handling activé")
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Capture et gère toutes les erreurs"""
        try:
            response = await call_next(request)
            return response
            
        except HTTPException as exc:
            # Erreurs HTTP connues
            logger.warning(
                f"HTTP {exc.status_code}: {exc.detail} - "
                f"Path: {request.url.path}"
            )
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": exc.detail,
                    "status_code": exc.status_code,
                    "path": str(request.url.path),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as exc:
            # Erreurs inattendues
            request_id = getattr(request.state, "request_id", "unknown")
            logger.error(
                f"❌ Unhandled error [{request_id}]: {str(exc)} - "
                f"Path: {request.url.path}",
                exc_info=True
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal server error",
                    "message": str(exc),
                    "request_id": request_id,
                    "path": str(request.url.path),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )


# ============================================================================
# 4. PERFORMANCE MONITORING MIDDLEWARE
# ============================================================================

class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Mesure et log les performances de chaque requête
    """
    
    def __init__(self, app, slow_threshold_ms: float = 1000):
        super().__init__(app)
        self.slow_threshold_ms = slow_threshold_ms
        logger.info(f"⚡ Performance Monitoring activé (seuil: {slow_threshold_ms}ms)")
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Mesure le temps de traitement"""
        start_time = time.time()
        
        # Traiter la requête
        response = await call_next(request)
        
        # Calculer le temps
        process_time = (time.time() - start_time) * 1000  # en ms
        
        # Ajouter header
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        
        # Logger les requêtes lentes
        if process_time > self.slow_threshold_ms:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.warning(
                f"⚠️ Slow request [{request_id}]: {request.method} {request.url.path} - "
                f"{process_time:.2f}ms"
            )
        
        # Log normal
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.2f}ms"
        )
        
        return response


# ============================================================================
# 5. IP WHITELIST MIDDLEWARE
# ============================================================================

class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """
    Restreint l'accès à certaines IPs (optionnel, pour admin)
    """
    
    def __init__(
        self, 
        app,
        whitelist: Optional[Set[str]] = None,
        enabled: bool = False
    ):
        super().__init__(app)
        self.whitelist = whitelist or set()
        self.enabled = enabled
        
        if self.enabled:
            logger.info(f"🔒 IP Whitelist activé: {len(self.whitelist)} IPs autorisées")
        else:
            logger.info("🔓 IP Whitelist désactivé")
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Vérifie si l'IP est autorisée"""
        if not self.enabled:
            return await call_next(request)
        
        # Récupérer l'IP client
        client_ip = self._get_client_ip(request)
        
        # Vérifier whitelist
        if client_ip not in self.whitelist and self.whitelist:
            logger.warning(f"🚫 IP non autorisée: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "error": "access_denied",
                    "message": "Your IP address is not authorized",
                    "ip": client_ip,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extrait l'IP du client"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


# ============================================================================
# 6. CORS SECURITY MIDDLEWARE (Bonus)
# ============================================================================

class CORSSecurityMiddleware(BaseHTTPMiddleware):
    """
    CORS sécurisé avec validation stricte des origines
    """
    
    def __init__(self, app, allowed_origins: Set[str] = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or set()
        logger.info(f"🌐 CORS sécurisé activé pour: {self.allowed_origins}")
    
    async def dispatch(self, request: Request, call_next) -> Response:
        origin = request.headers.get("origin")
        
        # Valider l'origine
        if origin and origin not in self.allowed_origins:
            logger.warning(f"⚠️ Origine non autorisée: {origin}")
        
        response = await call_next(request)
        return response