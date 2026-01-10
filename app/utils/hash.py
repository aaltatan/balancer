from collections.abc import Callable

from bcrypt import checkpw, gensalt, hashpw

type PWDHasherFn = Callable[[str], str]
type PWDVerifierFn = Callable[[str, str], bool]


def hash_password(password: str) -> str:
    return hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
