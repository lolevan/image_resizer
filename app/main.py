from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from .routes import router

from .dependencies import get_db

import os


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Можно указать список допустимых источников
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/temp", StaticFiles(directory="temp"), name="temp")


@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open(os.path.join("static", "index.html")) as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.get("/get_api_key", response_class=HTMLResponse)
async def read_get_api_key():
    with open(os.path.join("static", "get_api_key.html")) as f:
        return HTMLResponse(content=f.read(), status_code=200)
