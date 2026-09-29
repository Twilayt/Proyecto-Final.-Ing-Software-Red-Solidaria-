from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.core.config import get_settings, validate_security_settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_is_hashed_and_verified():
    password = "Segura12345"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("Incorrecta123", hashed)


def test_token_round_trip_and_tampering_rejected():
    token = create_access_token("42", "admin")
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "admin"

    with pytest.raises(ValueError, match="Token inválido"):
        decode_access_token(token + "alterado")


def test_expired_token_is_rejected():
    settings = get_settings()
    expired = jwt.encode(
        {"sub": "1", "role": "user", "exp": datetime.now(UTC) - timedelta(minutes=1)},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    with pytest.raises(ValueError, match="Token inválido"):
        decode_access_token(expired)


def test_production_rejects_short_secret():
    settings = get_settings()
    insecure = type(settings)(
        **{**settings.__dict__, "app_env": "production", "jwt_secret": "corta"}
    )
    with pytest.raises(RuntimeError, match="al menos 32"):
        validate_security_settings(insecure)

