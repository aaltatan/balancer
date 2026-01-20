from collections.abc import Callable, Sequence
from enum import StrEnum, auto
from functools import wraps
from io import BytesIO
from typing import Any, Protocol, Self

import openpyxl
from fastapi.responses import StreamingResponse

from app.core.timezone import get_default_tz_now


class ExportType(StrEnum):
    CSV = auto()
    XLSX = auto()


class IExportSchema(Protocol):
    @classmethod
    def model_validate(cls, *args: Any, **kwargs: Any) -> Self: ...
    def model_dump(self, *args: Any, **kwargs: Any) -> dict[str, Any]: ...


class ISaveable(Protocol):
    def save(self, *args: Any, **kwargs: Any) -> None: ...


type ExportFn = Callable[[Sequence[IExportSchema], str], tuple[ISaveable, str]]


_export_fns: dict[ExportType, tuple[ExportFn, str]] = {}


def get_export_args(export_type: ExportType) -> tuple[ExportFn, str]:
    if export_type not in _export_fns:
        message = f"no export function registered for {export_type}"
        raise ValueError(message)

    return _export_fns[export_type]


def register_exporter(export_type: ExportType, media_type: str) -> Callable[[ExportFn], ExportFn]:
    def decorator(fn: ExportFn) -> ExportFn:
        @wraps(fn)
        def wrapper(schema_list: Sequence[IExportSchema], suffix: str) -> Any:
            now = get_default_tz_now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{suffix}_{now}.{export_type.value}"
            return fn(schema_list, filename)

        _export_fns[export_type] = (wrapper, media_type)

        return wrapper

    return decorator


@register_exporter(
    ExportType.XLSX, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
def export_to_xlsx(
    schema_list: Sequence[IExportSchema], suffix: str
) -> tuple[openpyxl.Workbook, str]:
    wb = openpyxl.Workbook()

    if not schema_list:
        return wb, suffix

    ws = wb.active

    if not ws:
        message = "no active worksheet"
        raise ValueError(message)

    ws.append(list(schema_list[0].model_dump().keys()))

    for schema in schema_list:
        ws.append(list(schema.model_dump().values()))

    return wb, suffix


def get_export_response[T](
    export: ExportType, data: Sequence[T], schema: IExportSchema, suffix: str
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
