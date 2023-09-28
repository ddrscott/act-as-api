import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse

from . import bots

app = FastAPI()

from pydantic import BaseModel


class Reply(BaseModel):
    message: str
    reply: str

@app.on_event("startup")
async def startup():
    logging.basicConfig(level=logging.INFO)

@app.exception_handler(Exception)
async def value_error_exception_handler(request: Request, exc: Exception):
    logger = logging.getLogger(__name__)
    logger.exception(exc)
    return JSONResponse(
        status_code=500,
        content={"message": str(exc)},
    )

@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    logger = logging.getLogger(__name__)
    logger.exception(exc)
    return JSONResponse(
        status_code=400,
        content={"message": str(exc)},
    )

@app.get("/")
async def root():
    return {"status": "okay"}

@app.get("/bots")
async def list_bot():
    return [b.name for b in bots.fetch_all()]

@app.get("/bots/{name}")
async def bot_by_name(name):
    return bots.fetch(name)

@app.get("/bots/{name}/reply")
async def reply(name: str, message: str, request: Request):
    """
    responds as text/plain
    """
    bot = bots.fetch(name)
    bot_args = dict(request.query_params)
    return {'reply': bot.one_shot(**bot_args), **bot_args}


@app.get("/bots/{name}/stream")
async def stream_reply(name: str, message: str, request: Request):
    bot = bots.fetch(name)
    bot_args = request.query_params
    return StreamingResponse(bot.async_one_shot(**bot_args), media_type="text/event-stream")
