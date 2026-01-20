from collections.abc import Callable
from typing import Annotated

from fastapi import Depends

from app.dependencies import get_hasher_fn, get_verifier_fn

PWDHasherFnDI = Annotated[Callable[[str], str], Depends(get_hasher_fn)]
PWDVerifierFnDI = Annotated[Callable[[str, str], bool], Depends(get_verifier_fn)]
