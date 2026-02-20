from collections.abc import Callable, Sequence
from enum import StrEnum, auto
from functools import wraps
from io import BytesIO
from typing import Any, Protocol, Self

import openpyxl
from fastapi.responses import StreamingResponse

from app.core.timezone import get_default_tz_now


class IExportSchema(Protocol):
    @classmethod
    def model_validate(cls, *args: Any, **kwargs: Any) -> Self: ...
    def model_dump(self, *args: Any, **kwargs: Any) -> dict[str, Any]: ...


class ISaveable(Protocol):
    def save(self, *args: Any, **kwargs: Any) -> None: ...


type Data = Sequence[IExportSchema]
type ExportFn = Callable[[Data, str], tuple[ISaveable, str]]


class ExportFormat(StrEnum):
    CSV = auto()
    XLSX = auto()


class ExporterFnNotFoundError(Exception):
    def __init__(self, fmt: ExportFormat, *args: object) -> None:
        message = f"No export function registered for {fmt.value}"
        super().__init__(message, *args)


class ExporterRegistry:
    def __init__(self) -> None:
        self._exporters: dict[ExportFormat, tuple[ExportFn, str]] = {}

    def __getitem__(self, fmt: ExportFormat) -> tuple[ExportFn, str]:
        if fmt not in self._exporters:
            raise ExporterFnNotFoundError(fmt)

        return self._exporters[fmt]

    def register(self, fmt: ExportFormat, media_type: str) -> Callable[[ExportFn], ExportFn]:
        def decorator(fn: ExportFn) -> ExportFn:
            @wraps(fn)
            def wrapper(schema_list: Data, suffix: str) -> Any:
                now = get_default_tz_now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"{suffix}_{now}.{fmt.value}"
                return fn(schema_list, filename)

            self._exporters[fmt] = (wrapper, media_type)

            return wrapper

        return decorator


exporters = ExporterRegistry()


@exporters.register(
    ExportFormat.XLSX, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
def export_to_xlsx(data: Data, suffix: str) -> tuple[openpyxl.Workbook, str]:
    wb = openpyxl.Workbook()

    if not data:
        return wb, suffix

    ws = wb.active

    if not ws:
        message = "no active worksheet"
        raise ValueError(message)

    ws.append(list(data[0].model_dump().keys()))

    for schema in data:
        ws.append(list(schema.model_dump().values()))

    return wb, suffix


def get_export_response[T](
    fmt: ExportFormat, data: Sequence[T], schema: IExportSchema, suffix: str
) -> StreamingResponse:
    export_fn, media_type = exporters[fmt]

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
