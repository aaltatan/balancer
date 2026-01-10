<<<<<<< HEAD
# ruff: noqa: DTZ001, FBT001
=======
# ruff: noqa: DTZ001
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
from datetime import datetime

import pytest
from app.db.tenant import TenantDB
from app.db.user import UserDB
from app.services.auth import authenticate
<<<<<<< HEAD
from sqlalchemy.orm import Session


def mock_hash_password(password: str) -> str:
    return f"hashed_{password}"


def mock_verify_password(password: str, hashed_password: str) -> bool:
    return f"hashed_{password}" == hashed_password


=======
from app.utils.hash import hash_password
from sqlalchemy.orm import Session


>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
@pytest.fixture(autouse=True, scope="module")
def init_users_tenants(session: Session):
    active_tenant = TenantDB(
        name="Active", valid_from=datetime(2026, 1, 1), valid_to=datetime(2027, 1, 1)
    )
    outdate_tenant = TenantDB(
        name="Inactive", valid_from=datetime(2027, 1, 1), valid_to=datetime(2028, 1, 1)
    )
    disabled_tenant = TenantDB(
        name="Disabled",
        valid_from=datetime(2022, 1, 1),
        valid_to=datetime(2029, 1, 1),
        disabled=True,
    )

    users = [
        UserDB(
            username="admin",
            firstname="Admin",
            lastname="Admin",
<<<<<<< HEAD
            hashed_password=mock_hash_password("Abdullah@123"),
=======
            hashed_password=hash_password("Abdullah@123"),
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
            role="superuser",
        ),
        UserDB(
            username="activetenantuser",
            firstname="Admin",
            lastname="Admin",
<<<<<<< HEAD
            hashed_password=mock_hash_password("Abdullah@123"),
=======
            hashed_password=hash_password("Abdullah@123"),
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
            role="tenant-superuser",
            tenant=active_tenant,
        ),
        UserDB(
            username="inactivetenantuser",
            firstname="Admin",
            lastname="Admin",
<<<<<<< HEAD
            hashed_password=mock_hash_password("Abdullah@123"),
=======
            hashed_password=hash_password("Abdullah@123"),
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
            role="tenant-superuser",
            tenant=active_tenant,
            is_active=False,
        ),
        UserDB(
            username="outdatetenantuser",
            firstname="Admin",
            lastname="Admin",
<<<<<<< HEAD
            hashed_password=mock_hash_password("Abdullah@123"),
=======
            hashed_password=hash_password("Abdullah@123"),
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
            role="tenant-superuser",
            tenant=outdate_tenant,
        ),
        UserDB(
            username="disabledtenantuser",
            firstname="Admin",
            lastname="Admin",
<<<<<<< HEAD
            hashed_password=mock_hash_password("Abdullah@123"),
=======
            hashed_password=hash_password("Abdullah@123"),
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
            role="tenant-superuser",
            tenant=disabled_tenant,
        ),
    ]

    session.add_all([active_tenant, outdate_tenant, disabled_tenant])
    session.add_all(users)

    session.commit()

    yield

    session.query(UserDB).delete()
    session.query(TenantDB).delete()


@pytest.mark.parametrize(
    "username, password, expected",
    [
        ("admin", "Abdullah@123", True),
        ("not-found", "Abdullah@123", False),  # user not found
        ("admin@", "Abdullah@123", False),  # tenant is ""
        ("inactivetenantuser@active", "Abdullah@123", False),  # inactive user
        ("activetenantuser@active", "Abdullah@123", True),
        ("outdatetenantuser@outdate", "Abdullah@123", False),  # outdated tenant
        ("disabledtenantuser@disabled", "Abdullah@123", False),  # disabled tenant
        ("activetenantuser@activex", "Abdullah@123", False),  # wrong tenant_slug
        ("outdatetenantuser@outdatex", "Abdullah@123", False),  # wrong tenant_slug
        ("disabledtenantuser@disabledx", "Abdullah@123", False),  # wrong tenant_slug
        ("activetenantuserx@active", "Abdullah@123", False),  # wrong username
        ("outdatetenantuserx@outdate", "Abdullah@123", False),  # wrong username
        ("disabledtenantuserx@disabled", "Abdullah@123", False),  # wrong username
        ("activetenantuser@active", "Abdullah@1234", False),  # wrong password
        ("outdatetenantuser@outdate", "Abdullah@1234", False),  # wrong password
        ("disabledtenantuser@disabled", "Abdullah@1234", False),  # wrong password
    ],
)
<<<<<<< HEAD
def test_authenticate(session: Session, username: str, password: str, expected: bool) -> None:
    user = authenticate(session, username, password, mock_verify_password)
=======
def test_authenticate(session: Session, username: str, password: str, expected: bool) -> None:  # noqa: FBT001
    user = authenticate(session, username, password)
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
    assert bool(user) == expected
