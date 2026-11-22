from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from models import Products
from database import SessionLocal, engine
import database_models
from sqlalchemy.orm import Session

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"]
)
database_models.Base.metadata.create_all(bind = engine)

@app.get("/")
def greet():
    return {"message": f"Hello, user!"}

products = [
    Products(id = 1, name = "Phone", description = "iphone 18 pro", price = 999.99, quantity = 10),
    Products(id = 2, name = "Laptop", description = "Macbook pro 2026 M6", price = 1999.99, quantity = 8),
    Products(id = 3, name = "Tablet", description = "iPad Pro 2026", price = 799.99, quantity = 15),
    Products(id = 4, name = "Smartwatch", description = "Apple Watch Series 8", price = 399.99, quantity = 20)
    ]


# if any function wants to access the database, it creates a new session everytime and it may close or may not close
# so we create a get_db function and ensures the session is closed after the function is executed.
# This is done using the yield statement, which allows the function to return a value and then continue executing after the function has returned.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    db = SessionLocal()

    # not want to add duplicate products to the database, so we will check if the product already exists in the database before adding it.
    count = db.query(database_models.Product).count()
    # .query function create a query object that can be used to retrieve data from the database.
    #  The .count() method is used to count the number of rows in the products table.

    if count == 0:
        for product in products:
            # Class Products in models.py is not same as Product in database_models.py.
            #  So, we need to convert the Products object to Product object before adding it to the database.
            # model_dump() method is used to convert the Products pydantic object to a dictionary, which can then be unpacked into Key : value pair using **.  
            db.add(database_models.Product(**product.model_dump()))
    
    db.commit()

init_db()

@app.get("/products")
def get_all_products(db : Session = Depends(get_db)):
    return db.query(database_models.Product).all()


# @app.get("/products")
# def get_all_products():
#     return products

@app.get("/products/{product_id}")
def get_product_by_id(product_id: int, db : Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == product_id).first()
    
    if db_product:
        return db_product
    return {"message": "Product not found"}



@app.post("/products")
def add_product(product: Products, db : Session = Depends(get_db)):
    db.add(database_models.Product(**product.model_dump()))
    db.commit()
    return { "message": "product added succcessfully" }



@app.put("/products/{id}")
def update_product(id: int, product: Products, db : Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        db_product.name = product.name
        db_product.description = product.description
        db_product.price = product.price
        db_product.quantity = product.quantity
        db.commit()
        return {"message": "Product updated successfully"}
    else:
        return {"message": "Product not found"}


@app.delete("/products/{id}")
def delete_product(id: int ,db : Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if not db_product:
        return {"message": "Product not found"}
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"}