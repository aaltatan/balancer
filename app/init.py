from sqlalchemy.orm import Session

from app.db import init_db
from app.db.permission import init_permissions


def init(session: Session) -> None:
    init_db()
    init_permissions(session)
