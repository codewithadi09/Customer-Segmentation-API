from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request


class SecurityHeadersMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        response = await call_next(request)

        # Don't let browsers guess the content type — prevents MIME sniffing attacks
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent your API responses from being embedded in iframes
        response.headers["X-Frame-Options"] = "DENY"

        # Force HTTPS in browsers that support it
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Control what information is sent in the Referer header
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Hide the fact that your server is running uvicorn
        response.headers["Server"] = "unknown"

        # Disable caching for API responses — prevents sensitive data sitting in browser cache
        response.headers["Cache-Control"] = "no-store"

        return response