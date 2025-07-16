from typing import List, Optional
from pydantic import BaseModel


class BookBase(BaseModel):
    name: str
    description: str
    pages: int
    img: Optional[str] = None
    author_id: int

class AuthorBase(BaseModel):
    first_name: str
    last_name: str
    bio: Optional[str] = None

class Book(BookBase):
    id: int
    author: AuthorBase

    class Config:
        from_attributes = True

class Author(AuthorBase):
    id: int

    class Config:
        from_attributes = True

class BookCreate(BookBase):
    pass

class AuthorCreate(AuthorBase):
    pass

class UserBase(BaseModel):
    username: str
    password: str

class UserLogin(UserBase):
    pass

class UserCreate(UserBase):
    email: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True