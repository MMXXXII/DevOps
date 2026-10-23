import os

import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db

router = APIRouter()


@router.post("/categories/")
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
        raise HTTPException(status_code=400, detail="Category already exists")

    category = models.Category(name=name, description=description)

    db.add(category)
    db.commit()
    db.refresh(category)

    return {"status": "success", "id": category.id}


@router.get("/categories/")
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()


@router.get("/categories/search/name")
def search_category(name: str, db: Session = Depends(get_db)):
    return (
        db.query(models.Category)
        .filter(models.Category.name.contains(name))
        .all()
    )


@router.get("/categories/count")
def count_categories(db: Session = Depends(get_db)):
    return {"count": db.query(models.Category).count()}


@router.get("/categories/{category_id}")
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = (
        db.query(models.Category)
        .filter(models.Category.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category


@router.get("/categories/{category_id}/items")
def get_category_items(category_id: int, db: Session = Depends(get_db)):
    category = (
        db.query(models.Category)
        .filter(models.Category.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    items_url = os.getenv("ITEMS_SERVICE_URL")

    if items_url:
        response = requests.get(
            f"{items_url}/items/filter/category",
            params={"category": category.name},
            timeout=5
        )
        response.raise_for_status()
        return response.json()

    return (
        db.query(models.Item)
        .filter(models.Item.category == category.name)
        .all()
    )


@router.put("/categories/{category_id}")
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
        raise HTTPException(status_code=404, detail="Category not found")

    category.name = name
    category.description = description

    db.commit()
    db.refresh(category)

    return {"status": "updated", "id": category_id}


@router.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = (
        db.query(models.Category)
        .filter(models.Category.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()

    return {"status": "deleted", "id": category_id}
