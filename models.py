from datetime import datetime
from sqlalchemy import Column, Float, Identity, Integer, String, Date, Boolean, ForeignKey, Sequence
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, Identity(start=1), primary_key=True)
    password = Column(String(100))
    name = Column(String(100))
    email = Column(String(100))
    books_borrowed = Column(Integer, default=0) 
    is_admin = Column(Boolean, default=False)

    # One-to-Many relationship: a user can borrow many books
    borrows = relationship('Borrow', back_populates='user')

class Book(Base):
    __tablename__ = 'books'

    book_id = Column(Integer, Identity(start=100000), primary_key=True)
    title = Column(String(1000))
    series = Column(String(1000))
    description = Column(String(4000))
    language = Column(String(200))
    isbn = Column(String(100))
    book_format = Column(String(200))
    edition = Column(String(1000))
    pages = Column(Integer)
    publisher = Column(String(500))
    publish_date = Column(Date)
    first_publish_date = Column(Date)
    cover_image_url = Column(String(200))
    price = Column(Float)

    # One-to-Many relationship: a book can be borrowed many times
    borrows = relationship('Borrow', back_populates='book')
    genres = relationship("Genre", back_populates="book")
    characters = relationship("Characters", back_populates="book")
    awards = relationship("Awards", back_populates="book")
    authors = relationship("Author", back_populates="book")

class Borrow(Base):
    __tablename__ = 'borrows'

    borrow_id = Column(Integer, Identity(start=1), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    book_id = Column(Integer, ForeignKey('books.book_id'))
    borrow_date = Column(Date)
    return_date = Column(Date)
    return_deadline = Column(Date)

    # Many-to-One relationships
    user = relationship('User', back_populates='borrows')
    book = relationship('Book', back_populates='borrows')

class Genre(Base):
    __tablename__ = 'genre'

    id = Column(Integer, Identity(start=1), primary_key=True)
    book_id = Column(Integer, ForeignKey('books.book_id'), nullable=False)
    genre = Column(String(200))

    # Relationship with Book
    book = relationship("Book", back_populates="genres")


class Characters(Base):
    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey('books.book_id'), nullable=False)
    character = Column(String(200))

    # Relationship with Book
    book = relationship("Book", back_populates="characters")


class Awards(Base):
    __tablename__ = 'awards'

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey('books.book_id'), nullable=False)
    name = Column(String(500))

    # Relationship with Book
    book = relationship("Book", back_populates="awards")

class Author(Base):
    __tablename__ = 'author'

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey('books.book_id'), nullable=False)
    name = Column(String(200))
    role = Column(String(200))

    # Relationship with Book
    book = relationship("Book", back_populates="authors")