from pydantic import BaseModel
from datetime import date


class BookCreate(BaseModel):
    title: str
    author: str
    year: int


class ReaderCreate(BaseModel):
    full_name: str
    phone: str
    email: str


class IssueCreate(BaseModel):
    reader_id: int
    book_id: int
    issue_date: date
    due_date: date



