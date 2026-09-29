import os

os.environ["APP_ENV"] = "test"
os.environ["JWT_SECRET"] = "clave-segura-exclusiva-para-pruebas-123456"
os.environ.pop("ADMIN_EMAIL", None)
os.environ.pop("ADMIN_PASSWORD", None)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.database import Base, get_db
from app.main import app
from app.models import Role, User


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    with testing_session() as session:
        yield session
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def create_user(db_session: Session):
    def factory(
        email: str = "usuario@example.com",
        password: str = "Segura12345",
        role: Role = Role.USER,
        active: bool = True,
    ) -> User:
        user = User(
            email=email,
            full_name="Persona de prueba",
            password_hash=hash_password(password),
            role=role,
            is_active=active,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return factory


@pytest.fixture()
def login_headers(client: TestClient):
    def factory(email: str, password: str = "Segura12345") -> dict[str, str]:
        response = client.post(
            "/api/v1/auth/token",
            data={"username": email, "password": password},
        )
        assert response.status_code == 200
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    return factory

