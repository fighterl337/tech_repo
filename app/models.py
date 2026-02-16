from sqlalchemy import Column, DateTime, Integer, String, Date, Enum, ForeignKey, Boolean, DECIMAL
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


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    year = Column(Integer)
    status = Column(String, default="available")

    issues = relationship("Issue", back_populates="book")


class Reader(Base):
    __tablename__ = "readers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True)
    phone = Column(String)

    issues = relationship("Issue", back_populates="reader")



class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"))
    reader_id = Column(Integer, ForeignKey("readers.id", ondelete="CASCADE"))
    issue_date = Column(Date)
    due_date = Column(DateTime)
    return_date = Column(Date, nullable=True)
    status = Column(String, default="issued")

    book = relationship("Book", back_populates="issues")
    reader = relationship("Reader", back_populates="issues")

