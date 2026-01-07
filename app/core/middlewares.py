import sqltap
from fastapi import Request


async def profiler_middleware(request: Request, call_next):  # noqa: ANN001
    profiler = sqltap.start()
    response = await call_next(request)
    stats = profiler.stop()
    sqltap.report(stats, "profiler.txt", report_format="text")
    profiler.stop()
    return response
