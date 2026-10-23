from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db

router = APIRouter()


@router.post("/items/")
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

    return {"status": "success", "id": db_item.id}


@router.get("/items/")
def get_items(db: Session = Depends(get_db)):
    return db.query(models.Item).all()


@router.get("/items/search/name")
def search_by_name(name: str, db: Session = Depends(get_db)):
    return db.query(models.Item).filter(models.Item.name.contains(name)).all()


@router.get("/items/filter/price")
def filter_price(max_price: float, db: Session = Depends(get_db)):
    return db.query(models.Item).filter(models.Item.price <= max_price).all()


@router.get("/items/filter/category")
def filter_category(category: str, db: Session = Depends(get_db)):
    return db.query(models.Item).filter(models.Item.category == category).all()


@router.get("/items/filter/stock")
def filter_stock(min_stock: int, db: Session = Depends(get_db)):
    return db.query(models.Item).filter(models.Item.stock >= min_stock).all()


@router.get("/items/count")
def count_items(db: Session = Depends(get_db)):
    return {"count": db.query(models.Item).count()}


@router.get("/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item


@router.put("/items/{item_id}")
def update_item(
    item_id: int,
    name: str,
    price: float,
    category: str,
    stock: int,
    description: str = None,
    db: Session = Depends(get_db)
):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.name = name
    item.price = price
    item.category = category
    item.stock = stock
    item.description = description

    db.commit()
    db.refresh(item)

    return {"status": "updated", "id": item_id}


@router.patch("/items/{item_id}/stock")
def change_stock(item_id: int, stock: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if stock < 0:
        raise HTTPException(status_code=400, detail="Stock cannot be negative")

    item.stock = stock

    db.commit()
    db.refresh(item)

    return {"status": "stock updated", "id": item_id, "stock": stock}


@router.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()

    return {"status": "deleted", "id": item_id}


@router.delete("/items/")
def delete_all_items(db: Session = Depends(get_db)):
    count = db.query(models.Item).delete()
    db.commit()

    return {"status": "deleted", "count": count}
