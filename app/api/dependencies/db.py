from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db

SessionDI = Annotated[Session, Depends(get_db)]
