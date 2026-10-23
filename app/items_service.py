from fastapi import FastAPI

from .routers import items

app = FastAPI(title="Items Service")

app.include_router(items.router)
