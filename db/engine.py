from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./library.db"

engine = create_engine(
    url=SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def create_db():
    Base.metadata.create_all(bind=engine)