from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.api.admin import auth as admin_auth
from backend.app.api.admin import bookings as admin_bookings
from backend.app.api.admin import calendar as admin_calendar
from backend.app.api.admin import pricing as admin_pricing
from backend.app.api.admin import properties as admin_properties
from backend.app.api.public import properties
from backend.app.core.config import get_settings
from backend.app.api.public import bookings, calendar

settings = get_settings()

app = FastAPI(title=settings.app_name, debug=not settings.is_production)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "base-uri 'self'; "
            "frame-ancestors 'none'; "
            "object-src 'none'"
        )
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(properties.router, prefix="/api", tags=["public-properties"])
app.include_router(bookings.router, prefix="/api", tags=["public-bookings"])
app.include_router(calendar.router, tags=["calendar"])
app.include_router(admin_auth.router, prefix="/api", tags=["admin-auth"])
app.include_router(admin_properties.router, prefix="/api", tags=["admin-properties"])
app.include_router(admin_bookings.router, prefix="/api", tags=["admin-bookings"])
app.include_router(admin_calendar.router, prefix="/api", tags=["admin-calendar"])
app.include_router(admin_pricing.router, prefix="/api", tags=["admin-pricing"])


@app.get("/health")
async def health():
    return {"status": "ok"}
