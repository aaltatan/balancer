from datetime import UTC, datetime

import pytest
from app.db.tenant import TenantDB
from sqlalchemy.orm import Session


@pytest.fixture(autouse=True)
def init_tenants(session: Session):
    tenants_db = [
        TenantDB(
            name="Company 1",
            valid_from=datetime(2026, 1, 1, tzinfo=UTC),
            valid_to=datetime(2026, 12, 31, tzinfo=UTC),
        ),
        TenantDB(
            name="Company 2",
            valid_from=datetime(2026, 1, 1, tzinfo=UTC),
            valid_to=datetime(2026, 1, 5, tzinfo=UTC),
        ),
        TenantDB(
            name="Company 3",
            valid_from=datetime(2026, 1, 1, tzinfo=UTC),
            valid_to=datetime(2026, 12, 31, tzinfo=UTC),
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
