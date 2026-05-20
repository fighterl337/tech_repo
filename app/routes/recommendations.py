# app/routes/recommendations.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Book, BookCoOccurrence

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/for-book/{book_id}")
def recommend_for_book(book_id: int, limit: int = 6, db: Session = Depends(get_db)):
    # Проверяем, существует ли книга
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Ищем все пары, где участвует данная книга
    pairs = db.query(BookCoOccurrence).filter(
        (BookCoOccurrence.book_id_a == book_id) | (BookCoOccurrence.book_id_b == book_id)
    ).order_by(BookCoOccurrence.co_borrow_count.desc()).limit(limit).all()

    # Извлекаем ID рекомендованных книг
    recommended_ids = []
    for pair in pairs:
        if pair.book_id_a == book_id:
            recommended_ids.append(pair.book_id_b)
        else:
            recommended_ids.append(pair.book_id_a)

    # Получаем объекты книг
    recommended_books = db.query(Book).filter(Book.id.in_(recommended_ids)).all()
    # Сохраняем порядок
    ordered_books = sorted(recommended_books, key=lambda b: recommended_ids.index(b.id))
    return ordered_books