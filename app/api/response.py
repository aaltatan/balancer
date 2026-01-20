import math
from collections.abc import Sequence
from typing import Annotated, Literal, TypedDict

from pydantic import BaseModel, Field, computed_field


class ObjectResponse[T](BaseModel):
    item: T

    @computed_field
    def kind(self) -> Literal["object"]:
        return "object"


class ArrayResponse[T](BaseModel):
    items: Sequence[T]

    @property
    def items_count(self) -> int:
        return len(self.items)

    @computed_field
    def kind(self) -> Literal["array"]:
        return "array"

    @computed_field
    def meta(self) -> dict[str, int]:
        return {"items_count": self.items_count}


class Pagination(TypedDict):
    page: int
    page_size: int
    total_pages: int

    items_count: int
    total_items_count: int

    has_next: bool
    has_previous: bool


class PageResponse[T](BaseModel):
    items: Sequence[T]
    total_items_count: Annotated[int, Field(exclude=True)]

    page: Annotated[int, Field(exclude=True)]
    page_size: Annotated[int, Field(exclude=True)]

    @property
    def items_count(self) -> int:
        return len(self.items)

    @property
    def total_pages(self) -> int:
        return math.ceil(self.total_items_count / self.page_size)

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def next_page(self) -> int:
        return self.page + 1 if self.has_next else self.page

    @property
    def has_previous(self) -> bool:
        return self.page > 1

    @property
    def previous_page(self) -> int:
        return self.page - 1 if self.has_previous else 1

    @computed_field
    def kind(self) -> Literal["array"]:
        return "array"

    @computed_field
    def meta(self) -> Pagination:
        return {
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": self.total_pages,
            "items_count": self.items_count,
            "total_items_count": self.total_items_count,
            "has_next": self.has_next,
            "has_previous": self.has_previous,
        }
