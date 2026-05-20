from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, date
from app.database import SessionLocal
from app import models
from app import templates

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- Главная ----------
@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "base.html", {})

# ---------- Список книг (со ссылками на детали) ----------
@router.get("/books_page", response_class=HTMLResponse)
def books_page(request: Request, db: Session = Depends(get_db)):
    books = db.query(models.Book).all()
    return templates.TemplateResponse(request, "books.html", {"books": books})

# ---------- Детальная страница книги + логирование просмотра ----------
@router.get("/book_detail/{book_id}", response_class=HTMLResponse)
def book_detail(request: Request, book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        return HTMLResponse("Книга не найдена", status_code=404)

    # Логируем просмотр (берём первого читателя, позже заменим на реального пользователя)
    any_reader = db.query(models.Reader).first()
    if any_reader:
        activity = models.UserActivity(
            user_id=any_reader.id,
            book_id=book.id,
            action=models.ActionType.view.value
        )
        db.add(activity)
        db.commit()

    return templates.TemplateResponse(request, "book_detail.html", {"book": book})

# ---------- Страница читателей ----------
@router.get("/readers_page", response_class=HTMLResponse)
def readers_page(request: Request, db: Session = Depends(get_db)):
    readers = db.query(models.Reader).all()
    return templates.TemplateResponse(request, "readers.html", {"readers": readers})

# ---------- Страница выдачи (GET) ----------
@router.get("/issue_page", response_class=HTMLResponse)
def issue_page(request: Request, db: Session = Depends(get_db)):
    books = db.query(models.Book).all()
    readers = db.query(models.Reader).all()
    issues = db.query(models.Issue).all()
    return templates.TemplateResponse(request, "issue.html", {
        "books": books,
        "readers": readers,
        "issues": issues
    })

# ---------- Обработка выдачи (POST) + логирование borrow ----------
@router.post("/issue_page")
def create_issue_page(
    request: Request,
    book_id: int = Form(...),
    reader_id: int = Form(...),
    db: Session = Depends(get_db)
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book or book.status == "issued":
        return RedirectResponse(url="/issue_page", status_code=status.HTTP_303_SEE_OTHER)

    new_issue = models.Issue(
        book_id=book_id,
        reader_id=reader_id,
        status="issued",
        issue_date=datetime.utcnow().date()
    )
    book.status = "issued"
    db.add(new_issue)
    db.commit()

    # Логируем выдачу
    activity = models.UserActivity(
        user_id=reader_id,
        book_id=book_id,
        action=models.ActionType.borrow.value
    )
    db.add(activity)
    db.commit()

    return RedirectResponse(url="/issue_page", status_code=status.HTTP_303_SEE_OTHER)

# ---------- Добавление книги ----------
@router.get("/add_book_page", response_class=HTMLResponse)
def add_book_page(request: Request):
    return templates.TemplateResponse(request, "add_book.html", {})

@router.post("/add_book_page")
def add_book(
    title: str = Form(...),
    author: str = Form(...),
    year: int = Form(...),
    db: Session = Depends(get_db)
):
    new_book = models.Book(title=title, author=author, year=year)
    db.add(new_book)
    db.commit()
    return RedirectResponse(url="/books_page", status_code=303)

@router.post("/delete_book/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if book:
        db.delete(book)
        db.commit()
    return RedirectResponse(url="/books_page", status_code=303)

# ---------- Добавление читателя ----------
@router.get("/add_reader_page", response_class=HTMLResponse)
def add_reader_page(request: Request):
    return templates.TemplateResponse(request, "add_reader.html", {})

@router.post("/add_reader_page")
def add_reader(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    db: Session = Depends(get_db)
):
    new_reader = models.Reader(full_name=full_name, email=email, phone=phone)
    db.add(new_reader)
    db.commit()
    return RedirectResponse(url="/readers_page", status_code=303)

# ---------- Возврат книги + логирование return ----------
@router.post("/return_book/{issue_id}")
def return_book(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(models.Issue).filter(models.Issue.id == issue_id).first()
    if issue and issue.status == "issued":
        issue.status = "returned"
        issue.return_date = date.today()
        issue.book.status = "available"
        db.commit()

        activity = models.UserActivity(
            user_id=issue.reader_id,
            book_id=issue.book_id,
            action=models.ActionType.return_book.value
        )
        db.add(activity)
        db.commit()

    return RedirectResponse(url="/issue_page", status_code=303)