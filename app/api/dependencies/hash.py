from typing import Annotated

from fastapi import Depends

from app.utils.security import PWDHasherFn, PWDVerifierFn, hash_password, verify_password


def get_hasher_fn() -> PWDHasherFn:
    return hash_password


def get_verifier_fn() -> PWDVerifierFn:
    return verify_password


PWDHasherFnDI = Annotated[PWDHasherFn, Depends(get_hasher_fn)]
PWDVerifierFnDI = Annotated[PWDVerifierFn, Depends(get_verifier_fn)]
