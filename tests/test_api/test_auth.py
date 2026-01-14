# ruff: noqa: S106
import datetime

import pytest
from app.db.tenant import TenantDB
from app.db.user import UserDB
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture(autouse=True)
def init_authenticated_users(session: Session):
    tenant = TenantDB(
        name="Active",
        code="active",
        valid_until=datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=1),
    )

    users = [
        UserDB(
            username="admin",
            firstname="Superuser",
            lastname="Active",
            hashed_password="hashed_admin",
            role="superuser",
        ),
        UserDB(
            username="admin",
            firstname="Tenant Superuser",
            lastname="Active",
            hashed_password="hashed_admin",
            role="tenant-superuser",
            tenant=tenant,
        ),
    ]

    session.add(tenant)
    session.add_all(users)

    session.commit()

    yield

    session.query(TenantDB).delete()
    session.query(UserDB).delete()


def get_access_token(client: TestClient, username: str, password: str) -> str:
    response = client.post("/api/auth/token", data={"username": username, "password": password})

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["token_type"] == "bearer"  # noqa: S105

    return response.json()["access_token"]


def test_authenticate_superuser(client: TestClient) -> None:
    access_token = get_access_token(client, "admin", "admin")

    response = client.post("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "admin"
    assert response.json()["fullname"] == "Superuser Active"
    assert response.json()["role"] == "superuser"


def test_authenticate_tenant_superuser(client: TestClient) -> None:
    access_token = get_access_token(client, "admin@active", "admin")
    response = client.post("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "admin"
    assert response.json()["fullname"] == "Tenant Superuser Active"
    assert response.json()["role"] == "tenant-superuser"


def test_deactivate_user_after_getting_access_token(client: TestClient, session: Session) -> None:
    access_token = get_access_token(client, "admin@active", "admin")

    tenant = session.query(TenantDB).filter(TenantDB.code == "active").first()
    user = session.query(UserDB).filter(UserDB.username == "admin", UserDB.tenant == tenant).first()

    assert bool(user)

    user.is_active = False
    session.commit()

    response = client.post("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "User is not active"


def test_deactivate_tenant_after_getting_access_token(client: TestClient, session: Session) -> None:
    access_token = get_access_token(client, "admin@active", "admin")

    tenant = session.query(TenantDB).filter(TenantDB.code == "active").first()
    user = session.query(UserDB).filter(UserDB.username == "admin", UserDB.tenant == tenant).first()

    assert bool(user)
    assert bool(tenant)

    tenant.disabled = True
    session.commit()

    response = client.post("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Tenant is not active"
