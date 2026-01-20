from typing import Self

from pydantic import BaseModel, model_validator

from ._fields import PasswordFld


class AccessTokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class ChangePasswordSchema(BaseModel):
    old_password: PasswordFld
    new_password: PasswordFld
    confirm_password: PasswordFld

    @model_validator(mode="after")
    def validate_passwords(self) -> Self:
        if self.new_password.get_secret_value() != self.confirm_password.get_secret_value():
            message = "Passwords do not match."
            raise ValueError(message)

        return self
