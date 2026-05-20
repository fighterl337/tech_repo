from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
import enum

class BookStatus(str, enum.Enum):
    available = "available"
    issued = "issued"

class IssueStatus(str, enum.Enum):
    issued = "issued"
    returned = "returned"

class ActionType(str, enum.Enum):
    view = "view"
    borrow = "borrow"
    return_book = "return"

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    year = Column(Integer)
    status = Column(String, default="available")

    issues = relationship("Issue", back_populates="book")
    activities = relationship("UserActivity", back_populates="book")

class Reader(Base):
    __tablename__ = "readers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True)
    phone = Column(String)

    issues = relationship("Issue", back_populates="reader")
    activities = relationship("UserActivity", back_populates="reader")

class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"))
    reader_id = Column(Integer, ForeignKey("readers.id", ondelete="CASCADE"))
    issue_date = Column(Date)
    due_date = Column(DateTime, nullable=True)
    return_date = Column(Date, nullable=True)
    status = Column(String, default="issued")

    book = relationship("Book", back_populates="issues")
    reader = relationship("Reader", back_populates="issues")

class UserActivity(Base):
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("readers.id", ondelete="CASCADE"))
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"))
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    reader = relationship("Reader", back_populates="activities")
    book = relationship("Book", back_populates="activities")

class BookCoOccurrence(Base):
    __tablename__ = "book_co_occurrence"

    id = Column(Integer, primary_key=True, index=True)
    book_id_a = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"))
    book_id_b = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"))
    co_borrow_count = Column(Integer, default=0)

    book_a = relationship("Book", foreign_keys=[book_id_a])
    book_b = relationship("Book", foreign_keys=[book_id_b])