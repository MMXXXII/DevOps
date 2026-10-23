from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from . import database, models
from .database import get_db
from .routers import categories, items as items_router

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Lab CI/CD CRUD App")

templates = Jinja2Templates(directory="templates")

app.include_router(items_router.router)
app.include_router(categories.router)


@app.get("/", response_class=HTMLResponse)
def read_root(
    request: Request,
    db: Session = Depends(get_db)
):
    items = db.query(models.Item).all()

    return templates.TemplateResponse(
        request,
        "index.html",
        {"items": items}
    )
