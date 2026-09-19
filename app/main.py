from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from . import database, models

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Lab CI/CD CRUD App")

templates = Jinja2Templates(directory="templates")


def get_db():
    db = database.SessionLocal()

    try:
        yield db
    finally:
        db.close()


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


@app.post("/items/")
def create_item(
    name: str,
    price: float,
    category: str,
    stock: int,
    description: str = None,
    db: Session = Depends(get_db)
):
    db_item = models.Item(
        name=name,
        price=price,
        category=category,
        stock=stock,
        description=description
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return {
        "status": "success",
        "id": db_item.id
    }


@app.get("/items/")
def get_items(db: Session = Depends(get_db)):
    return db.query(models.Item).all()


@app.get("/items/search/name")
def search_by_name(
    name: str,
    db: Session = Depends(get_db)
):
    return (
        db.query(models.Item)
        .filter(models.Item.name.contains(name))
        .all()
    )


@app.get("/items/filter/price")
def filter_price(
    max_price: float,
    db: Session = Depends(get_db)
):
    return (
        db.query(models.Item)
        .filter(models.Item.price <= max_price)
        .all()
    )


@app.get("/items/filter/category")
def filter_category(
    category: str,
    db: Session = Depends(get_db)
):
    return (
        db.query(models.Item)
        .filter(models.Item.category == category)
        .all()
    )


@app.get("/items/filter/stock")
def filter_stock(
    min_stock: int,
    db: Session = Depends(get_db)
):
    return (
        db.query(models.Item)
        .filter(models.Item.stock >= min_stock)
        .all()
    )


@app.get("/items/count")
def count_items(db: Session = Depends(get_db)):
    return {
        "count": db.query(models.Item).count()
    }


@app.get("/items/{item_id}")
def get_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    item = (
        db.query(models.Item)
        .filter(models.Item.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    return item


@app.put("/items/{item_id}")
def update_item(
    item_id: int,
    name: str,
    price: float,
    category: str,
    stock: int,
    description: str = None,
    db: Session = Depends(get_db)
):
    item = (
        db.query(models.Item)
        .filter(models.Item.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    item.name = name
    item.price = price
    item.category = category
    item.stock = stock
    item.description = description

    db.commit()
    db.refresh(item)

    return {
        "status": "updated",
        "id": item_id
    }


@app.patch("/items/{item_id}/stock")
def change_stock(
    item_id: int,
    stock: int,
    db: Session = Depends(get_db)
):
    item = (
        db.query(models.Item)
        .filter(models.Item.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    if stock < 0:
        raise HTTPException(
            status_code=400,
            detail="Stock cannot be negative"
        )

    item.stock = stock

    db.commit()
    db.refresh(item)

    return {
        "status": "stock updated",
        "id": item_id,
        "stock": stock
    }


@app.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    item = (
        db.query(models.Item)
        .filter(models.Item.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    db.delete(item)
    db.commit()

    return {
        "status": "deleted",
        "id": item_id
    }


@app.delete("/items/")
def delete_all_items(db: Session = Depends(get_db)):
    count = db.query(models.Item).delete()
    db.commit()

    return {
        "status": "deleted",
        "count": count
    }


@app.post("/categories/")
def create_category(
    name: str,
    description: str = None,
    db: Session = Depends(get_db)
):
    existing = (
        db.query(models.Category)
        .filter(models.Category.name == name)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Category already exists"
        )

    category = models.Category(
        name=name,
        description=description
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return {
        "status": "success",
        "id": category.id
    }


@app.get("/categories/")
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()


@app.get("/categories/search/name")
def search_category(
    name: str,
    db: Session = Depends(get_db)
):
    return (
        db.query(models.Category)
        .filter(models.Category.name.contains(name))
        .all()
    )


@app.get("/categories/count")
def count_categories(db: Session = Depends(get_db)):
    return {
        "count": db.query(models.Category).count()
    }


@app.get("/categories/{category_id}")
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = (
        db.query(models.Category)
        .filter(models.Category.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category


@app.get("/categories/{category_id}/items")
def get_category_items(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = (
        db.query(models.Category)
        .filter(models.Category.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return (
        db.query(models.Item)
        .filter(models.Item.category == category.name)
        .all()
    )


@app.put("/categories/{category_id}")
def update_category(
    category_id: int,
    name: str,
    description: str = None,
    db: Session = Depends(get_db)
):
    category = (
        db.query(models.Category)
        .filter(models.Category.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    category.name = name
    category.description = description

    db.commit()
    db.refresh(category)

    return {
        "status": "updated",
        "id": category_id
    }


@app.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = (
        db.query(models.Category)
        .filter(models.Category.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    db.delete(category)
    db.commit()

    return {
        "status": "deleted",
        "id": category_id
    }

