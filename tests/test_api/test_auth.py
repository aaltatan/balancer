# ruff: noqa: S106
import datetime

import pytest
from app.db.tenant import TenantDB
from app.db.user import UserDB
from devtools import debug
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture(autouse=True)
def init_authenticated_users(session: Session):
    tenants = [
        TenantDB(
            name="Active",
            valid_from=datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC),
            valid_to=datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=1),
        ),
        TenantDB(
            name="Outdated",
            valid_from=datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC),
            valid_to=datetime.datetime(2026, 1, 5, tzinfo=datetime.UTC),
        ),
        TenantDB(
            name="Disabled",
            valid_from=datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC),
            valid_to=datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=1),
            disabled=True,
        ),
    ]

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
            tenant=tenants[0],
        ),
        UserDB(
            username="admin2",
            firstname="Tenant Superuser",
            lastname="Deactivated",
            hashed_password="hashed_admin",
            role="tenant-superuser",
            tenant=tenants[0],
            is_active=False,
        ),
        UserDB(
            username="admin",
            firstname="Tenant Superuser",
            lastname="Tenant Outdated",
            hashed_password="hashed_admin",
            role="tenant-superuser",
            tenant=tenants[1],
        ),
        UserDB(
            username="admin",
            firstname="Tenant Superuser",
            lastname="Tenant Disabled",
            hashed_password="hashed_admin",
            role="tenant-superuser",
            tenant=tenants[2],
        ),
    ]

    session.add_all(tenants)
    session.add_all(users)

    session.commit()

    yield

    session.query(TenantDB).delete()
    session.query(UserDB).delete()


def test_authenticate_superuser(client: TestClient):
    response = client.post(
        "/api/auth/superuser/token", data={"username": "admin", "password": "admin"}
    )
    debug(response.status_code)
    debug(response.json())
    assert response.status_code == status.HTTP_200_OK
