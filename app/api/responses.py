from collections.abc import Sequence
from io import BytesIO

from fastapi.responses import StreamingResponse

from app.utils.export import ExportType, Schema, get_export_args


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
