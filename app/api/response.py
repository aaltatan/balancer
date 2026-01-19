import math
import re
from collections.abc import Sequence
from io import BytesIO
from typing import Annotated, Literal, TypedDict

from fastapi import Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.utils.export import ExportType, Schema, get_export_args


class Links(TypedDict):
    first: str
    next: str | None
    current: str
    previous: str | None
    last: str


class Pagination(TypedDict):
    page: int
    page_size: int

    items_count: int
    total_items_count: int

    total_pages: int
    has_next: bool
    has_previous: bool
    links: Links


class ObjectResponse[T](BaseModel):
    item: T

    @computed_field
    def kind(self) -> Literal["object"]:
        return "object"


class ArrayResponse[T: (list, set, tuple)](BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    items: T
    total_items_count: Annotated[int, Field(exclude=True)] = 0

    request: Annotated[Request, Field(exclude=True)]
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

    def _get_pagination_fullpath(self, page: int) -> str:
        path = self.request.url.path
        query = self.request.url.query

        if "page=" in query:
            query = re.sub(r"page=\d+", f"page={page}", self.request.url.query)

        return f"{path}?{query}"

    @computed_field
    def kind(self) -> Literal["array"]:
        return "array"

    @computed_field
    def pagination(self) -> Pagination:
        first_link = self._get_pagination_fullpath(1)
        last_link = self._get_pagination_fullpath(self.total_pages)
        current_link = self._get_pagination_fullpath(self.page)
        next_link = self._get_pagination_fullpath(self.next_page) if self.has_next else None
        previous_link = (
            self._get_pagination_fullpath(self.previous_page) if self.has_previous else None
        )

        return {
            "page": self.page,
            "page_size": self.page_size,
            "items_count": self.items_count,
            "total_items_count": self.total_items_count,
            "has_next": self.has_next,
            "has_previous": self.has_previous,
            "total_pages": self.total_pages,
            "links": {
                "first": first_link,
                "next": next_link,
                "current": current_link,
                "previous": previous_link,
                "last": last_link,
            },
        }


def get_export_response[T](
    export: ExportType, data: Sequence[T], schema: Schema, suffix: str
) -> StreamingResponse:
    export_fn, media_type = get_export_args(export)

    schema_list = [schema.model_validate(obj) for obj in data]

    file, filename = export_fn(schema_list, suffix)

    buffer = BytesIO()
    file.save(buffer)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
