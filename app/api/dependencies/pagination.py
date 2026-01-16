from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, Field

from app.core.config import get_config

config = get_config()


class SkipLimitParams(BaseModel):
    skip: Annotated[int, Field(ge=0)]
    limit: Annotated[int, Field(ge=1, le=config.default_max_limit)]


def get_skip_limit_params(
    skip: Annotated[
        int,
        Query(
            ge=0,
            description="Number of items to skip",
        ),
    ] = config.default_skip,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=config.default_max_limit,
            description="Number of items to return",
        ),
    ] = config.default_limit,
) -> SkipLimitParams:
    return SkipLimitParams(skip=skip, limit=limit)
