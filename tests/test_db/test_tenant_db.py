from datetime import UTC, datetime, timedelta

import pytest
from app.db.tenant import TenantDB
from sqlalchemy.orm import Session


@pytest.fixture(autouse=True)
def init_tenants(session: Session):
    tenants_db = [
        TenantDB(
            name="Company 1",
            code="aaaa",
            valid_until=datetime.now(tz=UTC) + timedelta(days=5),
        ),
        TenantDB(
            name="Company 2",
            code="bbbb",
            valid_until=datetime.now(tz=UTC) - timedelta(days=5),
        ),
        TenantDB(
            name="Company 3",
            code="cccc",
            valid_until=datetime.now(tz=UTC) + timedelta(days=5),
            disabled=True,
        ),
    ]
    session.add_all(tenants_db)
    session.commit()
    yield
    session.query(TenantDB).delete()


def test_get_is_not_active_query(session: Session) -> None:
    tenants = session.query(TenantDB).filter(~TenantDB.is_active).all()
    assert len(tenants) == 2
