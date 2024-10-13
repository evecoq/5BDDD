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


#----------------------------USERS--------------------------------

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


# Create user
@app.post("/utilisateurs/", response_model=schemas.Utilisateur)
def create_utilisateur(user: schemas.UtilisateurCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")
    return crud.create_user(db=db, user=user)


#------------------------BOOKS------------------------------

# Search a book
@app.get("/search/", response_model=dict)
def search(
    name: str = Query(None, min_length=2),  # Author's name parameter
    title: str = Query(None, min_length=2),  # Title paramether
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



#NEW
@app.post("/books/", response_model=schemas.Book)
def create_book(
    book: schemas.BookCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")
    
    return crud.create_book_with_author_and_genre(db=db, book_data=book)


#-----------------------------------BORROWS---------------------------------

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


