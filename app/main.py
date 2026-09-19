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
def read_root(request: Request, db: Session = Depends(get_db)):
    items = db.query(models.Item).all()
    return templates.TemplateResponse("index.html", {"request": request, "items": items})

@app.post("/items/")
def create_item(name: str, price: float, category: str, stock: int, description: str = None, db: Session = Depends(get_db)):
    db_item = models.Item(name=name, price=price, category=category, stock=stock, description=description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return {"status": "success", "id": db_item.id}

@app.get("/items/")
def get_items(db: Session = Depends(get_db)):
    return db.query(models.Item).all()

@app.get("/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/items/{item_id}")
def update_item(item_id: int, name: str, price: float, category: str, stock: int, description: str = None, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.name = name
    item.price = price
    item.category = category
    item.stock = stock
    item.description = description
    db.commit()
    return {"status": "updated", "id": item_id}

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"status": "deleted", "id": item_id}


@app.get("/items/search/name")
def search_by_name(name: str, db: Session = Depends(get_db)):
    return db.query(models.Item).filter(models.Item.name.contains(name)).all()

@app.get("/items/filter/price")
def filter_price(max_price: float, db: Session = Depends(get_db)):
    return db.query(models.Item).filter(models.Item.price <= max_price).all()