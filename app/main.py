
from fastapi import FastAPI
from app.endpoints import (
    endpoints_characters,
    endpoints_comic
)


app = FastAPI()

app.include_router(endpoints_characters.router, tags=["Characters"])
app.include_router(endpoints_comic.router, tags=["Comics"])
