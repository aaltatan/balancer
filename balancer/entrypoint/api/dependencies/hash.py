from collections.abc import Callable
from typing import Annotated

from fastapi import Depends

from balancer.utils.security import hash_password, verify_password


def get_hasher_fn() -> Callable[[str], str]:
    return hash_password


def get_verifier_fn() -> Callable[[str, str], bool]:
    return verify_password


PWDHasherFnDI = Annotated[Callable[[str], str], Depends(get_hasher_fn)]
PWDVerifierFnDI = Annotated[Callable[[str, str], bool], Depends(get_verifier_fn)]
