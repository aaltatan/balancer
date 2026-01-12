from dataclasses import dataclass
from typing import Any

import pytest
from app.db.user import UserDB
from app.exceptions import AlreadyExistsError
from app.services.generic_user import GenericUserService
from app.services.superuser import SuperuserService
from sqlalchemy.orm import Session


def mock_hash_password(plain_password: str) -> str:
    return f"hashed-{plain_password}"


def mock_verify_password(plain_password: str, hashed_password: str) -> bool:
    return f"hashed-{plain_password}" == hashed_password


@dataclass
class MockCreateSchema:
    username: str
    firstname: str
    lastname: str
    permissions: set

    def model_dump(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "permissions": self.permissions,
        }


@dataclass
class MockUpdateSchema:
    firstname: str | None = None
    lastname: str | None = None

    def model_dump(self) -> dict[str, Any]:
        return {
            "firstname": self.firstname,
            "lastname": self.lastname,
        }


@pytest.fixture(autouse=True, scope="function")
def init_superusers_db(session: Session):
    admin1 = UserDB(
        username="admin1",
        firstname="Admin",
        lastname="One",
        hashed_password=mock_hash_password("admin"),
        role="superuser",
    )
    admin2 = UserDB(
        username="admin2",
        firstname="Admin",
        lastname="Two",
        hashed_password=mock_hash_password("admin"),
        role="superuser",
    )

    session.add_all([admin1, admin2])
    session.commit()

    yield

    session.query(UserDB).delete()
    session.commit()


@pytest.fixture()
def service(session: Session) -> SuperuserService:
    return SuperuserService(session, service=GenericUserService(session, mock_hash_password))


def test_get_all(service: SuperuserService) -> None:
    users = service.get_all()
    assert len(users) == 2


def test_create(service: SuperuserService) -> None:
    schema = MockCreateSchema(
        username="admin3", firstname="Admin", lastname="Three", permissions=set()
    )

    user = service.create(schema=schema, plain_password="admin")  # noqa: S106

    assert user.username == "admin3"
    assert user.firstname == "Admin"
    assert user.lastname == "Three"
    assert user.fullname == "Admin Three"
    assert user.role == "superuser"
    assert mock_verify_password("admin", user.hashed_password)
    assert user.is_active is True
    assert len(service.get_all()) == 3


def test_create_exists_username(service: SuperuserService) -> None:
    with pytest.raises(AlreadyExistsError):
        service.create(
            schema=MockCreateSchema(
                username="admin1", firstname="Admin Admin", lastname="One One", permissions=set()
            ),
            plain_password=mock_hash_password("adminss"),
        )


def test_update(service: SuperuserService) -> None:
    schema = MockUpdateSchema(firstname="Abdullah")

    user = service.update("admin1", schema)

    assert user.username == "admin1"
    assert user.firstname == "Abdullah"
    assert user.lastname == "One"
    assert user.fullname == "Abdullah One"
    assert user.role == "superuser"
    assert mock_verify_password("admin", user.hashed_password)
    assert user.is_active is True
    assert len(service.get_all()) == 2

    schema = MockUpdateSchema(lastname="Altatan")

    user = service.update("admin1", schema)

    assert user.username == "admin1"
    assert user.firstname == "Abdullah"
    assert user.lastname == "Altatan"
    assert user.fullname == "Abdullah Altatan"
    assert user.role == "superuser"
    assert mock_verify_password("admin", user.hashed_password)
    assert user.is_active is True
    assert len(service.get_all()) == 2


def test_delete(service: SuperuserService) -> None:
    service.delete("admin1")

    assert len(service.get_all()) == 1


def test_activation(service: SuperuserService) -> None:
    user = service.deactivate("admin1")

    assert user.username == "admin1"
    assert user.firstname == "Admin"
    assert user.lastname == "One"
    assert user.fullname == "Admin One"
    assert user.role == "superuser"
    assert mock_verify_password("admin", user.hashed_password)
    assert user.is_active is False
    assert len(service.get_all()) == 2

    user = service.activate("admin1")

    assert user.username == "admin1"
    assert user.firstname == "Admin"
    assert user.lastname == "One"
    assert user.fullname == "Admin One"
    assert user.role == "superuser"
    assert mock_verify_password("admin", user.hashed_password)
    assert user.is_active is True
    assert len(service.get_all()) == 2


def test_reset_password(service: SuperuserService) -> None:
    user = service.reset_password("admin1", "new-password")

    assert user.username == "admin1"
    assert user.firstname == "Admin"
    assert user.lastname == "One"
    assert user.fullname == "Admin One"
    assert user.role == "superuser"
    assert mock_verify_password("new-password", user.hashed_password)
    assert user.is_active is True
