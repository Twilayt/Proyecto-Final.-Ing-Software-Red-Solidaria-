"""Punto de entrada ASGI de RedSolidaria."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.core.config import get_settings, validate_security_settings
from app.core.security import hash_password
from app.database import SessionLocal, init_db
from app.models import Role, User
from app.routers import auth, donors


def seed_admin() -> None:
    settings = get_settings()
    if not settings.admin_email or not settings.admin_password:
        return
    with SessionLocal() as db:
        existing = db.scalar(select(User).where(User.email == settings.admin_email.lower()))
        if existing:
            return
        admin = User(
            email=settings.admin_email.lower(),
            full_name=settings.admin_full_name,
            password_hash=hash_password(settings.admin_password),
            role=Role.ADMIN,
        )
        db.add(admin)
        db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    validate_security_settings(settings)
    init_db()
    seed_admin()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    api = FastAPI(
        title=settings.app_name,
        version="2.0.0",
        description="Módulo académico de autenticación y gestión de donantes.",
        lifespan=lifespan,
    )
    api.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @api.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )

        # Swagger necesita cargar JavaScript y CSS externos.
        # La política CSP restrictiva se conserva para las rutas normales de la API.
        documentation_route = (
            request.url.path.startswith("/docs")
            or request.url.path == "/redoc"
            or request.url.path == "/openapi.json"
        )

        if not documentation_route:
            response.headers["Content-Security-Policy"] = (
                "default-src 'none'; frame-ancestors 'none'"
            )

        return response

    @api.get("/health", tags=["Operación"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "redsolidaria-api"}

    api.include_router(auth.router, prefix="/api/v1")
    api.include_router(donors.router, prefix="/api/v1")
    return api


app = create_app()


#this is a note