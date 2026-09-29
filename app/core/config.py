"""Configuración de la aplicación basada en variables de entorno."""

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_env: str
    database_url: str
    jwt_secret: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    cors_origins: tuple[str, ...]
    admin_email: str | None
    admin_password: str | None
    admin_full_name: str


@lru_cache
def get_settings() -> Settings:
    origins = tuple(
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"
        ).split(",")
        if origin.strip()
    )
    return Settings(
        app_name="RedSolidaria API",
        app_env=os.getenv("APP_ENV", "development"),
        database_url=os.getenv("DATABASE_URL", "sqlite:///./redsolidaria.db"),
        jwt_secret=os.getenv("JWT_SECRET", "solo-desarrollo-cambiar-clave-32-caracteres"),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        cors_origins=origins,
        admin_email=os.getenv("ADMIN_EMAIL"),
        admin_password=os.getenv("ADMIN_PASSWORD"),
        admin_full_name=os.getenv("ADMIN_FULL_NAME", "Administración RedSolidaria"),
    )


def validate_security_settings(settings: Settings) -> None:
    """Evita iniciar un entorno no local con una clave JWT débil."""
    if settings.app_env in {"staging", "production"} and len(settings.jwt_secret) < 32:
        raise RuntimeError("JWT_SECRET debe tener al menos 32 caracteres en staging/production")

