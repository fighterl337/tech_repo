from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from ..database import get_db
from ..models import Issue, Book, IssueStatus, BookStatus
from ..schemas import IssueCreate

router = APIRouter(prefix="/issues", tags=["Issues"])


@router.post("/")
def create_issue(issue: IssueCreate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == issue.book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book.status == BookStatus.issued:
        raise HTTPException(status_code=400, detail="Book already issued")

    new_issue = Issue(**issue.dict())
    book.status = BookStatus.issued

    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)

    return new_issue


@router.post("/return/{issue_id}")
def return_book(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    book = db.query(Book).filter(Book.id == issue.book_id).first()

    issue.status = IssueStatus.returned
    issue.return_date = date.today()
    book.status = BookStatus.available

    db.commit()

    return {"message": "Book returned"}
