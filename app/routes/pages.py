from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
from app import templates
from fastapi import Form
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Главная страница
@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


# Страница книг
@router.get("/books_page", response_class=HTMLResponse)
def books_page(request: Request, db: Session = Depends(get_db)):
    books = db.query(models.Book).all()
    return templates.TemplateResponse("books.html", {
        "request": request,
        "books": books
    })


# Страница читателей
@router.get("/readers_page", response_class=HTMLResponse)
def readers_page(request: Request, db: Session = Depends(get_db)):
    readers = db.query(models.Reader).all()
    return templates.TemplateResponse("readers.html", {
        "request": request,
        "readers": readers
    })


# Страница выдачи
@router.get("/issue_page", response_class=HTMLResponse)
def issue_page(request: Request, db: Session = Depends(get_db)):
    books = db.query(models.Book).all()
    readers = db.query(models.Reader).all()
    issues = db.query(models.Issue).all()

    return templates.TemplateResponse("issue.html", {
        "request": request,
        "books": books,
        "readers": readers,
        "issues": issues
    })
from fastapi import status

@router.post("/issue_page")
def create_issue_page(
    request: Request,
    book_id: int = Form(...),
    reader_id: int = Form(...),
    db: Session = Depends(get_db)
):
    # находим книгу
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        # тут можно вернуть ошибку в шаблон, упрощённо просто редиректим назад
        return RedirectResponse(url="/issue_page", status_code=status.HTTP_303_SEE_OTHER)

    # проверяем, что книга свободна
    if book.status == "issued":
        return RedirectResponse(url="/issue_page", status_code=status.HTTP_303_SEE_OTHER)

    # создаём выдачу
    new_issue = models.Issue(
        book_id=book_id,
        reader_id=reader_id,
        status="issued",
        issue_date=datetime.utcnow().date()  # если есть такое поле
    )
    book.status = "issued"

    db.add(new_issue)
    db.commit()

    return RedirectResponse(url="/issue_page", status_code=status.HTTP_303_SEE_OTHER)
@router.get("/add_book_page", response_class=HTMLResponse)
def add_book_page(request: Request):
    return templates.TemplateResponse("add_book.html", {
        "request": request
    })


# Обработка формы
@router.post("/add_book_page")
def add_book(
    title: str = Form(...),
    author: str = Form(...),
    year: int = Form(...),
    db: Session = Depends(get_db)
):
    new_book = models.Book(
        title=title,
        author=author,
        year=year
    )

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

@router.get("/add_reader_page", response_class=HTMLResponse)
def add_reader_page(request: Request):
    return templates.TemplateResponse("add_reader.html", {
        "request": request
    })


@router.post("/add_reader_page")
def add_reader(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    db: Session = Depends(get_db)
):
    new_reader = models.Reader(
        full_name=full_name,
        email=email,
        phone=phone
    )

    db.add(new_reader)
    db.commit()

    return RedirectResponse(url="/readers_page", status_code=303)

@router.post("/return_book/{issue_id}")
def return_book(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(models.Issue).filter(models.Issue.id == issue_id).first()

    if issue and issue.status == "issued":
        issue.status = "returned"
        issue.book.status = "available"
        db.commit()

    return RedirectResponse(url="/issue_page", status_code=303)
