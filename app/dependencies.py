from collections.abc import Callable

from bcrypt import checkpw, gensalt, hashpw


def hash_password(password: str) -> str:
    return hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_hasher_fn() -> Callable[[str], str]:
    return hash_password


def get_verifier_fn() -> Callable[[str, str], bool]:
    return verify_password
