from models import User, Book, Author
import models
from schemas import UtilisateurCreate
import schemas
from utils import hash_password, verify_password
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from fastapi import Depends, HTTPException, status



def create_user(db: Session, user: UtilisateurCreate):
    hashed_pw = hash_password(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        password=hashed_pw,
        is_admin=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def get_user_by_email(db:Session, email: str):
    return db.query(User).filter(User.email == email).first()


def search_books_and_authors(db: Session, name: str = None, title: str = None):
    books = []
    authors = []

    # Rechercher les livres par titre si 'titre' est fourni
    if title:
        books = db.query(Book).filter(Book.title.ilike(f"%{title}%")).all()

    # Rechercher les auteurs par nom si 'nom' est fourni
    if name:
        authors = db.query(Author).filter(Author.name.ilike(f"%{name}%")).all()

        # Ajouter les livres associés aux auteurs trouvés
        author_books = []
        for author in authors:
            book = db.query(Book).filter(Book.book_id == author.book_id).first()
            if book:
                author_books.append(book)

        # Fusionner les résultats : livres trouvés par titre + livres trouvés par auteurs
        books = list(set(books + author_books))  # Utilisation de set pour éviter les doublons

    return {
        "books": books,
        "authors": authors
    }


def create_borrow(db: Session, borrow: schemas.BorrowCreate, user_id: int):
    # Vérifier si le livre est déjà emprunté et non retourné
    existing_borrow = db.query(models.Borrow).filter(
        models.Borrow.book_id == borrow.book_id,
        models.Borrow.return_date == None  # Vérifie si le livre n'a pas encore été retourné
    ).first()

    if existing_borrow:
        raise HTTPException(status_code=400, detail="Le livre est déjà emprunté et n'a pas été retourné.")

    # Si le livre est disponible, créer un nouvel emprunt
    db_borrow = models.Borrow(
        user_id=user_id,
        book_id=borrow.book_id,
        borrow_date=borrow.borrow_date or date.today(),  # Prend la date du jour si non fournie
        return_deadline=borrow.return_deadline or (date.today() + relativedelta(months=2)),
        return_date=None  # Le livre n'a pas encore été retourné
    )
    db.add(db_borrow)
    db.commit()
    db.refresh(db_borrow)

    # Incrémenter le nombre de livres empruntés par l'utilisateur
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    user.books_borrowed = (user.books_borrowed or 0) + 1
    db.commit()

    return db_borrow


def close_borrow(db: Session, book_id: int, user_id: int):
    # Fetch the borrow record by user_id and book_id
    db_borrow = db.query(models.Borrow).filter(
        models.Borrow.book_id == book_id,
        models.Borrow.user_id == user_id
    ).first()

    # Check if the borrow exists
    if not db_borrow:
        raise HTTPException(status_code=404, detail="Emprunt non trouvé pour ce livre et cet utilisateur")

    # Check if the borrow has already been closed (return_date already set)
    if db_borrow.return_date:
        raise HTTPException(status_code=400, detail="Le livre a déjà été retourné")

    # Update the borrow record with the return date as today's date
    db_borrow.return_date = date.today()

    # Decrement books_borrowed count for the user
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user:
        user.books_borrowed -= 1  # Decrement the borrowed books count

    # Commit the changes to the database
    db.commit()
    db.refresh(db_borrow)
    

def get_user_borrows(db: Session, user_id: int):
    return db.query(models.Borrow).filter(models.Borrow.user_id == user_id).all()


# Ajouter un livre

def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(**book.dict())  # Create the book from schema
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def update_book(db: Session, book_id: int, book: schemas.BookCreate):
    db_book = db.query(models.Book).filter(models.Book.book_id == book_id).first()
    if db_book is None:
        return None
    for key, value in book.dict().items():
        setattr(db_book, key, value)
    db.commit()
    db.refresh(db_book)
    return db_book


def delete_book(db: Session, book_id: int):
    db_book = db.query(models.Book).filter(models.Book.book_id == book_id).first()
    if db_book is None:
        return None
    db.delete(db_book)
    db.commit()
    return db_book

