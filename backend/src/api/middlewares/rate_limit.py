"""
Middleware de Rate Limiting - Protection contre les abus
Limite le nombre de requêtes par IP et par endpoint
"""

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple
from datetime import datetime, timedelta
import time
from collections import defaultdict
from threading import Lock

from src.core.logging import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware de limitation de débit avec bucket algorithm
    """
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_size: int = 10,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_size = burst_size
        
        # Stockage des requêtes par IP
        self.minute_buckets: Dict[str, list] = defaultdict(list)
        self.hour_buckets: Dict[str, list] = defaultdict(list)
        self.burst_buckets: Dict[str, int] = defaultdict(int)
        
        # Lock pour thread safety
        self.lock = Lock()
        
        # Endpoints exemptés (health checks)
        self.exempted_paths = {"/health", "/", "/docs", "/redoc", "/openapi.json"}
    
    async def dispatch(self, request: Request, call_next):
        """
        Vérifie les limites de taux avant de traiter la requête
        """
        # Exempter certains endpoints
        if request.url.path in self.exempted_paths:
            return await call_next(request)
        
        # Identifier le client
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Vérifier les limites
        with self.lock:
            # Nettoyer les anciennes entrées
            self._cleanup_old_requests(client_ip, current_time)
            
            # Vérifier burst (rafale)
            if self.burst_buckets[client_ip] >= self.burst_size:
                logger.warning(f"🚫 Rate limit BURST dépassé - IP: {client_ip}")
                return self._rate_limit_response("Trop de requêtes simultanées")
            
            # Vérifier limite par minute
            minute_count = len(self.minute_buckets[client_ip])
            if minute_count >= self.requests_per_minute:
                logger.warning(f"🚫 Rate limit MINUTE dépassé - IP: {client_ip} ({minute_count} req/min)")
                return self._rate_limit_response("Limite de 60 requêtes par minute atteinte")
            
            # Vérifier limite par heure
            hour_count = len(self.hour_buckets[client_ip])
            if hour_count >= self.requests_per_hour:
                logger.warning(f"🚫 Rate limit HEURE dépassé - IP: {client_ip} ({hour_count} req/h)")
                return self._rate_limit_response("Limite de 1000 requêtes par heure atteinte")
            
            # Enregistrer la requête
            self.minute_buckets[client_ip].append(current_time)
            self.hour_buckets[client_ip].append(current_time)
            self.burst_buckets[client_ip] += 1
        
        # Traiter la requête
        try:
            response = await call_next(request)
            
            # Ajouter headers de rate limiting
            response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Remaining-Minute"] = str(
                max(0, self.requests_per_minute - minute_count - 1)
            )
            response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
            response.headers["X-RateLimit-Remaining-Hour"] = str(
                max(0, self.requests_per_hour - hour_count - 1)
            )
            
            return response
            
        finally:
            # Décrémenter le burst counter
            with self.lock:
                self.burst_buckets[client_ip] = max(0, self.burst_buckets[client_ip] - 1)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extrait l'IP du client (supporte les proxies)"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _cleanup_old_requests(self, client_ip: str, current_time: float):
        """Nettoie les anciennes requêtes pour une IP donnée"""
        try:
            # Minute buckets
            if client_ip in self.minute_buckets:
                minute_cutoff = current_time - 60
                self.minute_buckets[client_ip] = [
                    t for t in self.minute_buckets[client_ip] if t > minute_cutoff
                ]
                if not self.minute_buckets[client_ip]:
                    del self.minute_buckets[client_ip]
            
            # Hour buckets  
            if client_ip in self.hour_buckets:
                hour_cutoff = current_time - 3600
                self.hour_buckets[client_ip] = [
                    t for t in self.hour_buckets[client_ip] if t > hour_cutoff
                ]
                if not self.hour_buckets[client_ip]:
                    del self.hour_buckets[client_ip]
            
            # Burst buckets - gestion sécurisée
            if client_ip in self.burst_buckets and self.burst_buckets[client_ip] <= 0:
                del self.burst_buckets[client_ip]
                
        except KeyError:
            # Ignorer silencieusement si la clé n'existe plus
            pass

    def _rate_limit_response(self, message: str) -> JSONResponse:
        """Retourne une réponse 429 Too Many Requests"""
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "rate_limit_exceeded",
                "message": message,
                "retry_after_seconds": 60,
                "timestamp": datetime.utcnow().isoformat()
            },
            headers={
                "Retry-After": "60"
            }
        )


class EndpointRateLimiter:
    """
    Décorateur pour limiter des endpoints spécifiques
    Usage: @endpoint_limiter.limit("5/minute")
    """
    
    def __init__(self):
        self.buckets: Dict[Tuple[str, str], list] = defaultdict(list)
        self.lock = Lock()
    
    def limit(self, rate: str):
        """
        Décorateur pour limiter un endpoint
        rate format: "N/unit" ex: "5/minute", "100/hour"
        """
        count, unit = rate.split("/")
        max_requests = int(count)
        
        # Conversion en secondes
        if unit == "second":
            window = 1
        elif unit == "minute":
            window = 60
        elif unit == "hour":
            window = 3600
        else:
            raise ValueError(f"Unité invalide: {unit}")
        
        def decorator(func):
            async def wrapper(request: Request, *args, **kwargs):
                client_ip = request.client.host if request.client else "unknown"
                endpoint = request.url.path
                key = (client_ip, endpoint)
                
                current_time = time.time()
                
                with self.lock:
                    # Nettoyer anciennes requêtes
                    cutoff = current_time - window
                    self.buckets[key] = [t for t in self.buckets[key] if t > cutoff]
                    
                    # Vérifier limite
                    if len(self.buckets[key]) >= max_requests:
                        raise HTTPException(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail=f"Limite de {rate} dépassée pour cet endpoint"
                        )
                    
                    # Enregistrer requête
                    self.buckets[key].append(current_time)
                
                return await func(request, *args, **kwargs)
            
            return wrapper
        return decorator


# Instance globale
endpoint_limiter = EndpointRateLimiter()