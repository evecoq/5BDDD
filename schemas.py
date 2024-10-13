from datetime import date
from pydantic import BaseModel, EmailStr
from typing import List, Optional


#-----------------------USERS------------------------

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


#------------------------BOOKS-----------------------

# Schéma pour les livres
class BookBase(BaseModel):
    book_id : str
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


# Authors
class AuthorBase(BaseModel):
    name: str
    role: Optional[str] = None

class AuthorCreate(AuthorBase):
    book_id: str

class Author(AuthorBase):
    id: int
    book_id: str

    class Config:
        from_attributes = True  # Indique à Pydantic d'utiliser les objets SQLAlchemy comme source de données

class Book(BookBase):
    book_id: str
    authors: List[Author] = []

    class Config:
        from_attributes = True


#NEW
# Schéma de base pour les livres
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


# Schéma de base pour les auteurs
class AuthorBase(BaseModel):
    name: str
    role: Optional[str] = None


# Schéma de création pour les auteurs (sans `book_id`, car il sera ajouté après)
class AuthorCreate(AuthorBase):
    pass


# Schéma de base pour les genres
class GenreBase(BaseModel):
    genre: str


# Schéma de création pour les genres (sans `book_id`, car il sera ajouté après)
class GenreCreate(GenreBase):
    pass


# Schéma de création pour les livres
class BookCreate(BookBase):
    book_id: str
    authors: List[AuthorCreate]  # Liste des auteurs à ajouter
    genres: List[GenreCreate]  # Liste des genres à ajouter


# Schéma de retour d'un livre (avec ID, auteurs et genres)
class Book(BookBase):
    book_id: str
    authors: List[AuthorCreate]  # Auteurs du livre
    genres: List[GenreCreate]  # Genres du livre

    class Config:
        from_attributes = True

#UPDATE
class BookUpdate(BaseModel):
    title: Optional[str] = None
    series: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None
    isbn: Optional[str] = None
    book_format: Optional[str] = None
    edition: Optional[str] = None
    pages: Optional[int] = None
    publisher: Optional[str] = None
    price: Optional[float] = None
    authors: Optional[List[AuthorCreate]] = None
    genres: Optional[List[GenreCreate]] = None

    class Config:
        from_attributes = True
        

#---------------------------BORROWS--------------------------

class BorrowCreate(BaseModel):
    book_id: str
    borrow_date: Optional[date] = None  # Date facultative, prend la date du jour si non fournie
    return_deadline: Optional[date] = None

    class Config:
        from_attributes = True


class BorrowClose(BaseModel):
    book_id: str
    #borrow_id: int
    return_date: Optional[date] = None

    class Config:
        from_attributes = True


# Show my borrows (current + history)
class BorrowDetail(BaseModel):
    borrow_id: int
    book_id: str
    borrow_date: Optional[date]
    return_date: Optional[date]
    return_deadline: Optional[date]
    book: Optional[Book] = None  # Assuming the book schema is already defined

    class Config:
        from_attributes = True
