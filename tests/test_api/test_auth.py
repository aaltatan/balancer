import datetime
from collections.abc import Callable

import pytest
from app.db.tenant import TenantDB
from app.db.user import UserDB
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture(autouse=True, scope="module")
def init_authenticated_users(session: Session, hasher_fn: Callable[[str], str]):
    tenant = TenantDB(
        name="Active",
        code="actv",
        valid_until=datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=1),
    )

    users = [
        UserDB(
            username="admin",
            firstname="Superuser",
            lastname="Active",
            hashed_password=hasher_fn("admin"),
            role="superuser",
        ),
        UserDB(
            username="admin",
            firstname="Tenant Superuser",
            lastname="Active",
            hashed_password=hasher_fn("admin"),
            role="tenant-superuser",
            tenant=tenant,
        ),
        UserDB(
            username="user",
            firstname="Tenant User",
            lastname="Active",
            hashed_password=hasher_fn("admin"),
            role="tenant-user",
            tenant=tenant,
        ),
    ]

    session.add(tenant)
    session.add_all(users)

    session.commit()

    yield

    session.query(TenantDB).delete()
    session.query(UserDB).delete()

    session.commit()


def get_access_token(client: TestClient, username: str, password: str) -> str:
    response = client.post("/api/auth/token", data={"username": username, "password": password})

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["token_type"] == "bearer"  # noqa: S105

    return response.json()["access_token"]


@pytest.mark.parametrize(
    "username, password, expected_username, expected_fullname, expected_role",
    [
        ("admin", "admin", "admin", "Superuser Active", "superuser"),
        ("admin@actv", "admin", "admin", "Tenant Superuser Active", "tenant-superuser"),
        ("user@actv", "admin", "user", "Tenant User Active", "tenant-user"),
    ],
)
def test_authenticate_superuser(  # noqa: PLR0913
    client: TestClient,
    username: str,
    password: str,
    expected_username: str,
    expected_fullname: str,
    expected_role: str,
) -> None:
    access_token = get_access_token(client, username, password)
    response = client.post("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == expected_username
    assert response.json()["fullname"] == expected_fullname
    assert response.json()["role"] == expected_role


@pytest.mark.parametrize(
    "username, password",
    [("admin@", "admin"), ("admin@xctv", "admin"), ("xxx@active", "admin")],
)
def test_authenticate_invalid_credentials(client: TestClient, username: str, password: str) -> None:
    response = client.post("/api/auth/token", data={"username": username, "password": password})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid credentials"


def test_deactivate_user_after_getting_access_token(client: TestClient, session: Session) -> None:
    access_token = get_access_token(client, "admin@actv", "admin")

    tenant = session.query(TenantDB).filter(TenantDB.code == "actv").first()
    user = session.query(UserDB).filter(UserDB.username == "admin", UserDB.tenant == tenant).first()

    assert bool(user)

    user.is_active = False
    session.commit()

    response = client.post("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "User is not active"

    user.is_active = True
    session.commit()


def test_deactivate_tenant_after_getting_access_token(client: TestClient, session: Session) -> None:
    access_token = get_access_token(client, "admin@actv", "admin")

    tenant = session.query(TenantDB).filter(TenantDB.code == "actv").first()
    user = session.query(UserDB).filter(UserDB.username == "admin", UserDB.tenant == tenant).first()

    assert bool(user)
    assert bool(tenant)

    tenant.disabled = True
    session.commit()

    response = client.post("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Tenant is not active"

    tenant.disabled = False
    session.commit()


def test_outdated_tenant_after_getting_access_token(client: TestClient, session: Session) -> None:
    access_token = get_access_token(client, "admin@actv", "admin")

    tenant = session.query(TenantDB).filter(TenantDB.code == "actv").first()
    user = session.query(UserDB).filter(UserDB.username == "admin", UserDB.tenant == tenant).first()

    assert bool(user)
    assert bool(tenant)

    tenant.valid_until = datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(days=1)
    session.commit()

    response = client.post("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Tenant is not active"

    tenant.valid_until = datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=1)
    session.commit()
