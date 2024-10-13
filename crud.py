from models import User, Book, Author
import models
from schemas import UtilisateurCreate
import schemas
from utils import hash_password, verify_password
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from fastapi import Depends, HTTPException, status


#----------------------USERS-----------------------

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


#----------------------------------BOOKS------------------------------

#Search a book by name or by author
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

#CREATE
def create_book_with_author_and_genre(db: Session, book_data: schemas.BookCreate):
    # Créer le livre avec un book_id manuel, mais ne pas explicitement définir l'id
    db_book = models.Book(
        book_id=book_data.book_id,  # Utilisation du book_id fourni manuellement
        title=book_data.title,
        series=book_data.series,
        description=book_data.description,
        language=book_data.language,
        isbn=book_data.isbn,
        book_format=book_data.book_format,
        edition=book_data.edition,
        pages=book_data.pages,
        publisher=book_data.publisher,
        price=book_data.price
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)  # Cela renvoie les données mises à jour, y compris l'ID auto-généré

    # Créer les auteurs et genres en utilisant le book_id généré
    for author_data in book_data.authors:
        db_author = models.Author(
            name=author_data.name,
            role=author_data.role,
            book_id=db_book.book_id  # Utiliser le book_id manuellement fourni
        )
        db.add(db_author)

    for genre_data in book_data.genres:
        db_genre = models.Genre(
            genre=genre_data.genre,
            book_id=db_book.book_id  # Utiliser le book_id manuellement fourni
        )
        db.add(db_genre)

    db.commit()  # Valider les transactions pour les auteurs et genres
    return db_book


#UPDATE
def update_book(db: Session, book_id: str, book_data: schemas.BookUpdate, current_user: User):
    # Ensure the current user is an admin
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied")

    # Find the book by book_id
    db_book = db.query(models.Book).filter(models.Book.book_id == book_id).first()

    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Update the book fields if provided in the request
    if book_data.title:
        db_book.title = book_data.title
    if book_data.series:
        db_book.series = book_data.series
    if book_data.description:
        db_book.description = book_data.description
    if book_data.language:
        db_book.language = book_data.language
    if book_data.isbn:
        db_book.isbn = book_data.isbn
    if book_data.book_format:
        db_book.book_format = book_data.book_format
    if book_data.edition:
        db_book.edition = book_data.edition
    if book_data.pages:
        db_book.pages = book_data.pages
    if book_data.publisher:
        db_book.publisher = book_data.publisher
    if book_data.price:
        db_book.price = book_data.price

    # Update authors if provided
    if book_data.authors is not None:
        # Delete existing authors and add new ones
        db.query(models.Author).filter(models.Author.book_id == book_id).delete()
        for author_data in book_data.authors:
            db_author = models.Author(
                name=author_data.name,
                role=author_data.role,
                book_id=book_id
            )
            db.add(db_author)

    # Update genres if provided
    if book_data.genres is not None:
        # Delete existing genres and add new ones
        db.query(models.Genre).filter(models.Genre.book_id == book_id).delete()
        for genre_data in book_data.genres:
            db_genre = models.Genre(
                genre=genre_data.genre,
                book_id=book_id
            )
            db.add(db_genre)

    # Commit the changes
    db.commit()
    db.refresh(db_book)

    return db_book


#DELETE
def delete_book(db: Session, book_id: str, current_user: User):
    # Ensure the current user is an admin
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied")

    # Find the book by book_id
    db_book = db.query(models.Book).filter(models.Book.book_id == book_id).first()

    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Delete associated authors, genres, characters, and awards
    db.query(models.Author).filter(models.Author.book_id == book_id).delete()
    db.query(models.Genre).filter(models.Genre.book_id == book_id).delete()
    db.query(models.Characters).filter(models.Characters.book_id == book_id).delete()
    db.query(models.Awards).filter(models.Awards.book_id == book_id).delete()

    # Finally, delete the book itself
    db.delete(db_book)
    db.commit()

    return {"detail": "Book deleted successfully"}



#-----------------------------BORROWS-----------------------------

def create_borrow(db: Session, borrow: schemas.BorrowCreate, user_id: int):
    # Vérifier si le livre est déjà emprunté et non retourné
    existing_borrow = db.query(models.Borrow).filter(
        models.Borrow.book_id == borrow.book_id,
        models.Borrow.return_date == None  # Vérifie si le livre n'a pas encore été retourné
    ).first()

    if existing_borrow:
        raise HTTPException(status_code=400, detail="Le livre est déjà emprunté et n'a pas été retourné.")

    # Check if book is available, borrow it if it is
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

    # Number of borrowed books by user
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


