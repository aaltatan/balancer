from collections.abc import Callable
from decimal import Decimal
from enum import StrEnum
from types import NoneType
from typing import Any, NotRequired, TypedDict

from rich import box
from rich.console import JustifyMethod, OverflowMethod
from rich.table import Table

RENDERERS = {
    Decimal: lambda value: f"{value:,.2f}",
    float: lambda value: f"{value:,.2f}",
    bool: lambda value: "✅" if value else "❌",
    NoneType: lambda _: "-",
}


class _ColumnOptions(TypedDict):
    attr_name: str
    header: NotRequired[str]
    style: NotRequired[str]
    justify: NotRequired[JustifyMethod]
    overflow: NotRequired[OverflowMethod]
    no_wrap: NotRequired[bool]
    total: NotRequired[bool]
    renderer_fn: NotRequired[Callable[[Any], str]]


class TableBorderStyle(StrEnum):
    ASCII = "ASCII"
    ASCII2 = "ASCII2"
    ASCII_DOUBLE_HEAD = "ASCII_DOUBLE_HEAD"
    SQUARE = "SQUARE"
    SQUARE_DOUBLE_HEAD = "SQUARE_DOUBLE_HEAD"
    MINIMAL = "MINIMAL"
    MINIMAL_HEAVY_HEAD = "MINIMAL_HEAVY_HEAD"
    MINIMAL_DOUBLE_HEAD = "MINIMAL_DOUBLE_HEAD"
    SIMPLE = "SIMPLE"
    SIMPLE_HEAD = "SIMPLE_HEAD"
    SIMPLE_HEAVY = "SIMPLE_HEAVY"
    HORIZONTALS = "HORIZONTALS"
    ROUNDED = "ROUNDED"
    HEAVY = "HEAVY"
    HEAVY_EDGE = "HEAVY_EDGE"
    HEAVY_HEAD = "HEAVY_HEAD"
    DOUBLE = "DOUBLE"
    DOUBLE_EDGE = "DOUBLE_EDGE"
    MARKDOWN = "MARKDOWN"


def get_table(
    *columns: _ColumnOptions,
    objects: list[Any],
    title: str,
    add_index: bool,
    show_lines: bool,
    border_style: TableBorderStyle,
) -> Table:
    totals: dict[int, Decimal] = {}

    table = Table(title=title, show_lines=show_lines, box=getattr(box, str(border_style)))

    if add_index:
        table.add_column("#")

    for objects_idx, column in enumerate(columns):
        if column.get("total", False):
            totals[objects_idx] = Decimal(0)

        header = column.get("header", column["attr_name"])

        table.add_column(
            header=header,
            style=column.get("style"),
            justify=column.get("justify", "left"),
            overflow=column.get("overflow", "ellipsis"),
            no_wrap=column.get("no_wrap", False),
        )

    for objects_idx, obj in enumerate(objects):
        row = [str(objects_idx + 1)] if add_index else []

        for header_idx, column in enumerate(columns):
            attr_name = column["attr_name"]

            val = getattr(obj, attr_name, None)

            if not hasattr(obj, attr_name):
                msg = f"Schema {obj.__class__.__name__} has no attribute {attr_name}"
                raise AttributeError(msg)

            if header_idx in totals and isinstance(val, (Decimal, float, int)):
                totals[header_idx] += Decimal(val)

            if "renderer_fn" in column:
                renderer_fn = column["renderer_fn"]
            else:
                renderer_fn = RENDERERS.get(type(val), str)

            row.append(renderer_fn(val))

        table.add_row(*row)

    if totals:
        init_total_row = [""] if add_index else []
        total_row = init_total_row + [
            f"{totals[idx]:,.2f}" if idx in totals else "" for idx in range(len(columns))
        ]
        table.add_row(*total_row, style="on white")

    return table
