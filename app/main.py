from __future__ import annotations

import time as time_mod
from pathlib import Path
from urllib.parse import urlencode

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
)

from .render_html import render_html
from .render_png import render_png
from .time_logic import (
    InvalidTimeFormatError,
    InvalidTimezoneError,
    compute_state,
)

NO_CACHE_HEADERS = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
}

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@app.get("/healthz", response_class=PlainTextResponse)
def healthz() -> PlainTextResponse:
    return PlainTextResponse("ok")


@app.get("/helper.html", response_class=HTMLResponse)
def helper_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "helper.html", media_type="text/html")


@app.get("/time.png")
def time_png(
    request: Request,
    tz: str = Query(...),
    start: str = Query(...),
    end: str = Query(...),
    ts: int | None = Query(None),
) -> Response:
    if ts is None:
        params = urlencode(
            {"tz": tz, "start": start, "end": end, "ts": int(time_mod.time())}
        )
        return RedirectResponse(
            url=f"{request.url.path}?{params}",
            status_code=302,
            headers=NO_CACHE_HEADERS,
        )

    try:
        state = compute_state(tz, start, end)
    except InvalidTimezoneError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except InvalidTimeFormatError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    png = render_png(state)
    return Response(content=png, media_type="image/png", headers=NO_CACHE_HEADERS)


@app.get("/time.html", response_class=HTMLResponse)
def time_html(
    tz: str = Query(...),
    start: str = Query(...),
    end: str = Query(...),
) -> HTMLResponse:
    try:
        state = compute_state(tz, start, end)
    except InvalidTimezoneError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except InvalidTimeFormatError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return HTMLResponse(content=render_html(state), headers=NO_CACHE_HEADERS)


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException) -> PlainTextResponse:
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> PlainTextResponse:
    missing = [
        ".".join(str(p) for p in err["loc"][1:])
        for err in exc.errors()
        if err.get("type") == "missing"
    ]
    if missing:
        detail = f"Missing parameter(s): {', '.join(missing)}"
    else:
        detail = "Invalid parameters"
    return PlainTextResponse(detail, status_code=400)
