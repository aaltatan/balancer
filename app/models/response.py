from typing import Literal

from pydantic import BaseModel, computed_field


class Response[T](BaseModel):
    data: T

    @computed_field
    def length(self) -> int:
        if isinstance(self.data, (list, tuple, set, dict)):
            return len(self.data)
        return 1

    @computed_field
    def kind(self) -> Literal["array", "object"]:
        if isinstance(self.data, (list, tuple, set, dict)):
            return "array"
        return "object"
