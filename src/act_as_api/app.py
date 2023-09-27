import logging
from fastapi import FastAPI, Request, Body
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.exception_handler(Exception)
async def value_error_exception_handler(request: Request, exc: Exception):
    logger = logging.getLogger(__name__)
    logger.exception(exc)
    return JSONResponse(
        status_code=500,
        content={"message": str(exc)},
    )

@app.get("/")
async def root():
    return {"status": "okay"}
