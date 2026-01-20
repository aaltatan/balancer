import re
from typing import Annotated

from pydantic import AfterValidator, Field, SecretStr


def validate_password(v: SecretStr) -> SecretStr:
    value = v.get_secret_value()

    if value.lower() == value:
        message = "Password must have at least one uppercase letter."
        raise ValueError(message)

    if not re.search(r"[0-9]", value):
        message = "Password must have at least one number."
        raise ValueError(message)

    special_characters = "!@#$%^&*()_+-=[]{}|;':,./<>?"
    if not any(special_character in value for special_character in special_characters):
        message = "Password must have at least one special character."
        raise ValueError(message)

    return v


PasswordFld = Annotated[
    SecretStr, Field(min_length=8, max_length=255, exclude=True), AfterValidator(validate_password)
]
