from fastapi import HTTPException
from sqlalchemy.orm import Session
from db import models, schemas
from passlib.context import CryptContext

# Підтримка обох схем для сумісності
pwd_context = CryptContext(schemes=["sha256_crypt", "bcrypt"], deprecated="auto")

def create_book(db: Session, book: schemas.BookCreate):
    author = db.query(models.Author).filter(models.Author.id == book.author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    new_book = models.Book(name=book.name, description=book.description, pages=book.pages, img=book.img, author_id=book.author_id)    
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

def get_books(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Book).offset(skip).limit(limit).all()

def create_author(db: Session, author: schemas.AuthorCreate):
    new_author = models.Author(**author.model_dump())
    db.add(new_author)
    db.commit()
    db.refresh(new_author)
    return new_author

def get_authors(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Author).offset(skip).limit(limit).all()


def delete_book(db: Session, book_id: int):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return book

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    db_user = models.User(username=user.username, email=user.email, password=pwd_context.hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    pass