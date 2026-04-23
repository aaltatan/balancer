from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, Field

from balancer.config import get_config

config = get_config()


class Pagination(BaseModel):
    page: Annotated[int, Field(ge=1)]
    page_size: Annotated[int, Field(ge=1, le=config.default_max_page_size)]

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


def get_pagination(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=config.default_max_page_size)] = (
        config.default_page_size
    ),
) -> Pagination:
    return Pagination(page=page, page_size=page_size)
