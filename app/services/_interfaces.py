from typing import Any, Literal, Protocol

type FilteringType = Literal["and", "or"]


class IPaginationSchema(Protocol):
    @property
    def offset(self) -> int: ...

    @property
    def limit(self) -> int: ...


class ISchema(Protocol):
    def model_dump(*args: Any, **kwargs: Any) -> dict[str, Any]: ...


class IUserCreateSchema(Protocol):
    username: str
    permissions: set[Any]

    def model_dump(*args: Any, **kwargs: Any) -> dict[str, Any]: ...
