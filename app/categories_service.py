from fastapi import FastAPI

from .routers import categories

app = FastAPI(title="Categories Service")

app.include_router(categories.router)
