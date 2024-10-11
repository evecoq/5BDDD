from datetime import date
from pydantic import BaseModel, EmailStr
from typing import List, Optional


# Schéma pour la gestion des utilisateurs
class UtilisateurCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class Utilisateur(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    is_admin: bool

    class Config:
        from_attributes = True


# Schéma pour les auteurs
class AuthorBase(BaseModel):
    name: str
    role: Optional[str] = None

class AuthorCreate(AuthorBase):
    book_id: int

class Author(AuthorBase):
    id: int
    book_id: int

    class Config:
        from_attributes = True  # Indique à Pydantic d'utiliser les objets SQLAlchemy comme source de données


# Schéma pour les livres
class BookBase(BaseModel):
    title: str
    series: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None
    isbn: Optional[str] = None
    book_format: Optional[str] = None
    edition: Optional[str] = None
    pages: Optional[int] = None
    publisher: Optional[str] = None
    price: Optional[float] = None

class BookCreate(BaseModel):
    title: str
    series: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None
    isbn: Optional[str] = None
    book_format: Optional[str] = None
    edition: Optional[str] = None
    pages: Optional[int] = None
    publisher: Optional[str] = None
    price: Optional[float] = None


# Schéma pour mettre à jour un livre (peut être le même que BookCreate)
class BookUpdate(BookBase):
    pass

class Book(BookBase):
    book_id: int
    authors: List[Author] = []

    class Config:
        from_attributes = True

class BorrowCreate(BaseModel):
    book_id: int
    borrow_date: Optional[date] = None  # Date facultative, prend la date du jour si non fournie
    return_deadline: Optional[date] = None

    class Config:
        from_attributes = True

class BorrowClose(BaseModel):
    book_id: int
    #borrow_id: int
    return_date: Optional[date] = None

    class Config:
        from_attributes = True


# Schéma pour afficher les emprunts de l'utilisateur
class BorrowDetail(BaseModel):
    borrow_id: int
    book_id: int
    borrow_date: Optional[date]
    return_date: Optional[date]
    return_deadline: Optional[date]
    book: Optional[Book] = None  # Assuming the book schema is already defined

    class Config:
        from_attributes = True
