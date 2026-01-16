import math
from collections.abc import Sequence
from io import BytesIO
from typing import Annotated, Literal, TypedDict

from fastapi import Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.utils.export import ExportType, Schema, get_export_args


class Pagination(TypedDict):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class ObjectResponse[T](BaseModel):
    item: T

    @computed_field
    def kind(self) -> Literal["object"]:
        return "object"


class ArrayResponse[T: (list, set, tuple)](BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    items: T

    request: Annotated[Request, Field(exclude=True)]
    items_count: Annotated[int, Field(exclude=True)] = 0
    skip: Annotated[int, Field(exclude=True)] = 0

    @property
    def page_size(self) -> int:
        return len(self.items)

    @property
    def total_pages(self) -> int:
        return math.ceil(self.items_count / self.page_size)

    @property
    def page(self) -> int:
        return self.skip // self.page_size + 1

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        return self.page > 1

    @property
    def next_page(self) -> int:
        return self.page + 1 if self.has_next else self.page

    @property
    def previous_page(self) -> int:
        return self.page - 1 if self.has_previous else 1

    @computed_field
    def kind(self) -> Literal["array"]:
        return "array"

    @computed_field
    def pagination(self) -> Pagination:
        return {
            "page": self.page,
            "page_size": self.page_size,
            "total_items": self.items_count,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_previous": self.has_previous,
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
