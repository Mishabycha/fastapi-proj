from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from db import schemas, crud, models
from db.engine import session_local, create_db
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt

app = FastAPI(title="Books Library API", version="1.0.0")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
create_db()

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Підтримка обох схем для сумісності
pwd_context = CryptContext(schemes=["sha256_crypt", "bcrypt"], deprecated="auto")

# Схема для отримання токену
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    '''Отримуємо сесію бази даних'''
    db = session_local()
    try:
        yield db
    finally:
        db.close()

def create_token(data: dict):
    '''Створюємо токен'''
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode = data.copy()
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    '''Перевіряємо токен'''
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username =  payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return payload
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    '''Отримуємо поточного користувача'''
    payload = verify_token(token)
    username = payload.get("sub")
    user = crud.get_user(db, username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.get("/books")
def all_books(request: Request, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    '''Отримуємо всі книги'''
    books = crud.get_books(db)
    return templates.TemplateResponse("all_books.html", {"request": request, "books": books})

@app.post("/books/create")
def create_book(request: Request, book: schemas.BookCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    '''Створюємо книгу'''
    created_book = crud.create_book(db, book)
    return templates.TemplateResponse("create_book.html", {"request": request, "book": created_book, "user": current_user})

@app.post("/authors/create")
def create_author(request: Request, author: schemas.AuthorCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    '''Створюємо автора'''
    created_author = crud.create_author(db, author)
    return templates.TemplateResponse(
        "create_author.html",
        {
            "request": request,
            "author": created_author,
            "user": current_user
        }
    )

@app.get("/authors")
def all_authors(request: Request, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    '''Отримуємо всіх авторів'''
    authors = crud.get_authors(db)
    return templates.TemplateResponse("all_authors.html", {"request": request, "authors": authors})

@app.delete("/books/delete/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    '''Видаляємо книгу'''
    crud.delete_book(db, book_id)
    return None

@app.post("/token")
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    '''Отримуємо токен'''
    user_data = crud.get_user(db, form_data.username)
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    if not pwd_context.verify(form_data.password, user_data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    access_token = create_token({"sub": user_data.username})    
    # Повертаємо токен як JSON для OAuth2PasswordBearer
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    '''Створюємо користувача'''
    return crud.create_user(db, user)
    