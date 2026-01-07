from pydantic import BaseModel


class Wrapper[T](BaseModel):
    data: T
