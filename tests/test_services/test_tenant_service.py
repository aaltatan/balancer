from datetime import UTC, datetime, timedelta

import pytest
from app.db.tenant import TenantDB
from app.exceptions import AlreadyExistsError, NotFoundError
from app.services.tenant import TenantService
from sqlalchemy.orm import Session


@pytest.fixture
def service(session: Session) -> TenantService:
    return TenantService(session)


@pytest.fixture(autouse=True)
def init_tenants(session: Session):
    tenants_db = [
        TenantDB(
            name="Dabbagh",
            valid_from=datetime.now(tz=UTC) - timedelta(days=7),
            valid_to=datetime.now(tz=UTC) + timedelta(days=7),
        ),
        TenantDB(
            name="almostafa ceramica",
            valid_from=datetime.now(tz=UTC) - timedelta(days=7),
            valid_to=datetime.now(tz=UTC) + timedelta(days=7),
        ),
    ]
    session.add_all(tenants_db)
    session.commit()
    yield
    session.query(TenantDB).delete()


def test_get_all(service: TenantService) -> None:
    tenants = service.get_all()
    assert len(tenants) == 2


def test_get_by_slug(service: TenantService) -> None:
    tenant = service.get_by_slug("almostafa-ceramica")
    assert tenant.name == "almostafa ceramica"
    assert tenant.slug == "almostafa-ceramica"
    assert tenant.disabled is False
    assert tenant.is_active is True


def test_get_by_slug_not_found(service: TenantService) -> None:
    with pytest.raises(NotFoundError):
        service.get_by_slug("not-found")


def test_create(service: TenantService) -> None:
    tenant = service.create(
        "Dabbagh Supermarket", datetime(2022, 1, 1, tzinfo=UTC), datetime(2023, 1, 1, tzinfo=UTC)
    )

    assert tenant.name == "Dabbagh Supermarket"
    assert tenant.disabled is False
    assert tenant.is_active is False
    assert tenant.slug == "dabbagh-supermarket"
    assert len(service.get_all()) == 3


def test_create_already_exists(service: TenantService) -> None:
    with pytest.raises(AlreadyExistsError):
        service.create(
            "Dabbagh", datetime(2022, 1, 1, tzinfo=UTC), datetime(2023, 1, 1, tzinfo=UTC)
        )


def test_create_with_arabic_chars(service: TenantService) -> None:
    tenant = service.create(
        "ميني ماركت", datetime(2022, 1, 1, tzinfo=UTC), datetime(2023, 1, 1, tzinfo=UTC)
    )

    assert tenant.name == "ميني ماركت"
    assert tenant.disabled is False
    assert tenant.is_active is False
    assert tenant.slug == "ميني-ماركت"


def test_update(service: TenantService) -> None:
    tenant = service.update("dabbagh", name="Dabbagh Supermarket")

    assert tenant.name == "Dabbagh Supermarket"
    assert tenant.disabled is False
    assert tenant.is_active is True
    assert tenant.slug == "dabbagh-supermarket"
    assert len(service.get_all()) == 2


def test_activation(service: TenantService) -> None:
    tenant = service.deactivate("dabbagh")

    assert tenant.name == "Dabbagh"
    assert tenant.disabled is True
    assert tenant.is_active is False
    assert tenant.slug == "dabbagh"

    tenant = service.activate("dabbagh")

    assert tenant.name == "Dabbagh"
    assert tenant.disabled is False
    assert tenant.is_active is True
    assert tenant.slug == "dabbagh"
    assert len(service.get_all()) == 2


def test_delete(service: TenantService) -> None:
    service.delete("dabbagh")
    assert len(service.get_all()) == 1
