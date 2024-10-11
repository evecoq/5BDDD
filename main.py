from datetime import date
from fastapi import FastAPI, Depends, HTTPException, Query, status, Security
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import SessionLocal, engine
from dateutil.relativedelta import relativedelta
from models import Base, User
import models
from auth import ALGORITHM, SECRET_KEY, create_access_token
from jose import JWTError, jwt
from pydantic import BaseModel




import crud, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dépendance pour obtenir la session de la base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TokenData(BaseModel):
    email: Optional[str] = None
    is_admin: Optional[bool] = False

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},  
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        is_admin: bool = payload.get("is_admin", False)
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email, is_admin=is_admin)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


@app.get("/protected-route/")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Bonjour {current_user.name}, vous êtes authentifié."}

# Authentification via token
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.email, "is_admin": user.is_admin})
    return {"access_token": access_token, "token_type": "bearer"}        

# Endpoint Utilisateur
# Créer un utilisateur
@app.post("/utilisateurs/", response_model=schemas.Utilisateur)
def create_utilisateur(user: schemas.UtilisateurCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")
    return crud.create_user(db=db, user=user)

# Endpoint pour Livre
# Recherche de livre
@app.get("/search/", response_model=dict)
def search(
    name: str = Query(None, min_length=2),  # Paramètre pour le nom de l'auteur
    title: str = Query(None, min_length=2),  # Paramètre pour le titre du livre
    db: Session = Depends(get_db)
):
    # Appel de la fonction de recherche dans le CRUD avec les deux paramètres
    result = crud.search_books_and_authors(db=db, name=name, title=title)

    # Convertir les objets SQLAlchemy en schémas Pydantic
    books = [schemas.Book.from_orm(book) for book in result["books"]]
    authors = [schemas.Author.from_orm(author) for author in result["authors"]]

    return {
        "books": books,
        "authors": authors
    }

@app.post("/borrows/", response_model=schemas.BorrowCreate)
def create_borrow(borrow: schemas.BorrowCreate,  db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Vérifier si le livre existe
    book = db.query(models.Book).filter(models.Book.book_id == borrow.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")

    # Si la date d'emprunt n'est pas fournie, utiliser la date du jour
    if not borrow.borrow_date:
        borrow.borrow_date = date.today()

      # Utiliser la date du jour pour borrow_date et return_deadline
    borrow.borrow_date = date.today()
    borrow.return_deadline = borrow.borrow_date + relativedelta(months=2)

    # Appel à la fonction CRUD pour créer l'emprunt
    return crud.create_borrow(db=db, borrow=borrow, user_id=current_user.user_id)


@app.post("/borrows/close/{book_id}")
def close_borrow(book_id: int, db: Session = Depends(get_db), current_user: schemas.Utilisateur = Depends(get_current_user)):
    return crud.close_borrow(db=db, book_id=book_id, user_id=current_user.user_id)


@app.get("/users/borrows", response_model=List[schemas.BorrowDetail])
def get_borrows(db: Session = Depends(get_db), current_user: schemas.Utilisateur = Depends(get_current_user)):
    borrows = crud.get_user_borrows(db=db, user_id=current_user.user_id)
    return borrows


@app.post("/books/", response_model=schemas.Book)
def add_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    return crud.create_book(db=db, book=book)

"""
@app.put("/books/{book_id}")
def modify_book(book_id: int, book: BookCreate, db: Session = Depends(get_db)):
    updated_book = update_book(db, book_id, book)
    if updated_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book

@app.delete("/books/{book_id}")
def remove_book(book_id: int, db: Session = Depends(get_db)):
    deleted_book = delete_book(db, book_id)
    if deleted_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}
"""