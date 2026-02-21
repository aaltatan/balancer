from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Config, get_config
from app.db import get_db
from app.dependencies import get_hasher_fn, get_verifier_fn

ConfigDI = Annotated[Config, Depends(get_config)]

PWDHasherFnDI = Annotated[Callable[[str], str], Depends(get_hasher_fn)]
PWDVerifierFnDI = Annotated[Callable[[str, str], bool], Depends(get_verifier_fn)]

SessionDI = Annotated[Session, Depends(get_db)]
