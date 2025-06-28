from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
import structlog
from collections import defaultdict
import asyncio

from app.core.config import settings

logger = structlog.get_logger()

class RateLimiterMiddleware:
    """Rate limiting middleware using sliding window"""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.cleanup_task = None
    
    async def __call__(self, request: Request, call_next):
        # Get client identifier (IP address or user ID)
        client_id = self._get_client_id(request)
        
        # Check rate limit
        if not await self._is_allowed(client_id):
            logger.warning("Rate limit exceeded", client_id=client_id, path=request.url.path)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "code": 429,
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Add request to tracking
        await self._add_request(client_id)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_PER_MINUTE)
        response.headers["X-RateLimit-Remaining"] = str(
            settings.RATE_LIMIT_PER_MINUTE - len(self.requests[client_id])
        )
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Try to get user ID from token if authenticated
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from app.core.security import verify_token
                token = auth_header.split(" ")[1]
                token_data = verify_token(token)
                if token_data:
                    return f"user:{token_data.user_id}"
            except Exception:
                pass
        
        # Fallback to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"
        
        return f"ip:{request.client.host}"
    
    async def _is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed based on rate limit"""
        current_time = time.time()
        window_start = current_time - 60  # 1 minute window
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]
        
        # Check if under limit
        return len(self.requests[client_id]) < settings.RATE_LIMIT_PER_MINUTE
    
    async def _add_request(self, client_id: str):
        """Add request to tracking"""
        current_time = time.time()
        self.requests[client_id].append(current_time)
    
    async def cleanup_old_requests(self):
        """Clean up old request records"""
        current_time = time.time()
        window_start = current_time - 60
        
        for client_id in list(self.requests.keys()):
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if req_time > window_start
            ]
            
            # Remove empty entries
            if not self.requests[client_id]:
                del self.requests[client_id]
    
    async def start_cleanup_task(self):
        """Start background cleanup task"""
        async def cleanup_loop():
            while True:
                await asyncio.sleep(60)  # Clean up every minute
                await self.cleanup_old_requests()
        
        self.cleanup_task = asyncio.create_task(cleanup_loop())
    
    async def stop_cleanup_task(self):
        """Stop background cleanup task"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass 