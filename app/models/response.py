from pydantic import BaseModel


class Response[T](BaseModel):
    data: T
