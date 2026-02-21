from typing import Any


class AlreadyExistsError(Exception):
    def __init__(self, object_name: str, fieldname: str, *args: object) -> None:
        message = f"{object_name.title()} with {fieldname} already exists."
        super().__init__(message, *args)


class UserAlreadyExistsError(Exception):
    def __init__(self, *args: object) -> None:
        message = "Unable to create user. Please try different credentials."
        super().__init__(message, *args)


class NotFoundError(Exception):
    def __init__(self, object_name: str, fieldname: str, field_value: Any, *args: object) -> None:
        message = f"{object_name.title()} with {fieldname} '{field_value}' not found."
        super().__init__(message, *args)


class BulkNotFoundError(Exception):
    def __init__(self, object_name: str, fieldname: str, field_value: Any, *args: object) -> None:
        values = ", ".join(field_value)
        message = f"Some {object_name.title()}s with {fieldname} '{values}' not found."
        super().__init__(message, *args)


class InvalidPasswordError(Exception):
    def __init__(self, username: str, *args: object) -> None:
        message = f"Invalid password for user '{username}'."
        super().__init__(message, *args)


class CannotDeleteError(Exception):
    def __init__(
        self,
        object_name: str,
        fieldname: str,
        field_value: Any,
        reason: str | None = None,
        *args: object,
    ) -> None:
        message = f"Cannot delete {object_name.title()} with {fieldname} '{field_value}'."

        if reason:
            message += f" Reason: {reason}"

        super().__init__(message, *args)
