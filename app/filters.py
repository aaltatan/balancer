from collections.abc import Callable
from enum import StrEnum
from typing import Any, Literal, Protocol

from sqlalchemy import ColumnElement, UnaryExpression, and_, or_
from sqlalchemy.ext.hybrid import _HybridClassLevelAccessor
from sqlalchemy.orm import InstrumentedAttribute

type AttrType = InstrumentedAttribute[Any] | _HybridClassLevelAccessor[Any]
type FieldsMapper = dict[str, AttrType]
type ModifierFn = Callable[[Any, AttrType], Any]


class ModifierNotDefinedError(Exception):
    def __init__(self, name: str, *args: object) -> None:
        self.message = f"Modifier '{name}' not defined"
        super().__init__(*args)


class FieldNotInMapperError(Exception):
    def __init__(self, name: str, *args: object) -> None:
        self.message = f"Field '{name}' not in mapper"
        super().__init__(*args)


class IFilterSchema(Protocol):
    def model_dump(self, *args: Any, **kwargs: Any) -> dict[str, Any]: ...


GLOBAL_MODIFIERS: dict[str, ModifierFn] = {
    "contains": lambda value, attr: attr.ilike(f"%{value.replace(' ', '%')}%"),
    "notcontains": lambda value, attr: ~attr.ilike(f"%{value.replace(' ', '%')}%"),
    "startswith": lambda value, attr: attr.ilike(f"{value}%"),
    "notstartswith": lambda value, attr: ~attr.ilike(f"{value}%"),
    "endswith": lambda value, attr: attr.ilike(f"%{value}"),
    "notendswith": lambda value, attr: ~attr.ilike(f"%{value}"),
    "eq": lambda value, attr: attr == value,
    "ne": lambda value, attr: attr != value,
    "gt": lambda value, attr: attr > value,
    "gte": lambda value, attr: attr >= value,
    "lt": lambda value, attr: attr < value,
    "lte": lambda value, attr: attr <= value,
    "in": lambda value, attr: attr.in_(value),
    "notin": lambda value, attr: ~attr.in_(value),
    "isnull": lambda _, attr: attr.is_(None),
    "notnull": lambda _, attr: ~attr.is_(None),
    "between": lambda value, attr: attr.between(value[0], value[1]),
}


def get_order_by[T: StrEnum](order_by: list[T], mapper: dict[T, UnaryExpression[Any]]):
    return [mapper[order_by] for order_by in order_by]


def get_criterion(
    fields_mapper: FieldsMapper,
    schema: IFilterSchema,
    *,
    kind: Literal["and", "or"] = "and",
    **custom_modifiers: ModifierFn,
) -> ColumnElement[bool]:
    """Get a SQLAlchemy criterion from a FilterSchema.

    Args:
        fields_mapper (FieldsMapper): A dictionary of field names maps field names in DTO to SQLAlchemy attributes.
        schema (FilterSchema): A FilterSchema instance.
        kind (Literal["and", "or"]): The kind of criterion to return. Defaults to "and".
        custom_modifiers (dict[str, ModifierFn]): A dictionary of custom modifiers.

    Returns:
        ColumnElement[bool]: A SQLAlchemy criterion.

    Raises:
        ModifierNotDefinedError: If a modifier is not defined in the MODIFIERS dictionary.

    Usage:
        >>> from app.filters import get_criterion
        >>> from app.db.User import UserDB
        >>> from app.models.user import UserFilterSchema
        >>> from app.db import get_db
        >>> filter = UserFilterSchema(name__contains="Ali", age__gt=18)
        >>> fields_mapper = {"name": UserDB.name, "age": UserDB.age}
        >>> users = get_db().query(UserDB).filter(get_criterion(fields_mapper, filter)).all()

    """  # noqa: E501
    criterions = []

    modifiers = {**GLOBAL_MODIFIERS, **custom_modifiers}

    for full_fieldname, field_value in schema.model_dump().items():
        if field_value is not None:
            if "__" in full_fieldname:
                fieldname, modifier = full_fieldname.split("__")
            else:
                fieldname = full_fieldname
                modifier = ""

            if fieldname not in fields_mapper:
                raise FieldNotInMapperError(fieldname)

            if not modifier or modifier not in modifiers:
                raise ModifierNotDefinedError(modifier)

            modifier_fn = modifiers[modifier]

            criterion = modifier_fn(field_value, fields_mapper[fieldname])

            criterions.append(criterion)

    if kind == "and":
        return and_(*criterions)

    return or_(*criterions)
