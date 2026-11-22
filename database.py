from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_url = "postgresql+psycopg2://postgres:123456789@localhost:5432/fastapi_products"
engine = create_engine(url = db_url)

SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)