import logging
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

import secure

from . import bots, env
from .dependencies import validate_token

csp = secure.ContentSecurityPolicy().default_src("'self'").frame_ancestors("'none'")
hsts = secure.StrictTransportSecurity().max_age(31536000).include_subdomains()
referrer = secure.ReferrerPolicy().no_referrer()
cache_value = secure.CacheControl().no_cache().no_store().max_age(0).must_revalidate()
x_frame_options = secure.XFrameOptions().deny()

app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)

from pydantic import BaseModel

class Reply(BaseModel):
    message: str
    reply: str

secure_headers = secure.Secure(
    csp=csp,
    hsts=hsts,
    referrer=referrer,
    cache=cache_value,
    xfo=x_frame_options,
)


@app.middleware("http")
async def set_secure_headers(request, call_next):
    response = await call_next(request)
    secure_headers.framework.fastapi(response)
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=[env.CLIENT_ORIGIN_URL],
    allow_methods=["GET"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=86400,
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    message = str(exc.detail)
    return JSONResponse({"error": message}, status_code=exc.status_code)

@app.on_event("startup")
async def startup():
    logging.basicConfig(level=logging.INFO)

@app.exception_handler(Exception)
async def value_error_exception_handler(request: Request, exc: Exception):
    logger = logging.getLogger(__name__)
    logger.exception(exc)
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)},
    )

@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    logger = logging.getLogger(__name__)
    logger.exception(exc)
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)},
    )

@app.get("/")
async def root():
    return {"status": "okay"}

@app.get("/bots")
async def list_bot():
    return [b.name for b in bots.fetch_all()]

@app.get("/bots/{name}", dependencies=[Depends(validate_token)])
async def bot_by_name(name):
    return bots.fetch(name)

@app.get("/bots/{name}/reply", dependencies=[Depends(validate_token)])
async def reply(name: str, message: str, request: Request):
    """
    responds as text/plain
    """
    bot = bots.fetch(name)
    bot_args = dict(request.query_params)
    return {'reply': bot.one_shot(**bot_args), **bot_args}

@app.get("/bots/{name}/stream", dependencies=[Depends(validate_token)])
async def stream_reply(name: str, message: str, request: Request):
    bot = bots.fetch(name)
    bot_args = request.query_params
    return StreamingResponse(bot.async_one_shot(**bot_args), media_type="text/event-stream")
