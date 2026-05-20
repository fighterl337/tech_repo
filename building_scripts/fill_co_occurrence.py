# fill_co_occurrence.py
from app.database import SessionLocal
from app.models import Book, BookCoOccurrence
from itertools import combinations
from collections import defaultdict

db = SessionLocal()

# 1. Удаляем старые пары
db.query(BookCoOccurrence).delete()
db.commit()

# 2. Группируем книги по автору
books_by_author = defaultdict(list)
for book in db.query(Book).all():
    # Очистка автора от возможных пробелов в конце
    author = book.author.strip()
    books_by_author[author].append(book.id)

# 3. Для каждого автора создаём пары книг с весами
pair_count = 0
for author, book_ids in books_by_author.items():
    if len(book_ids) < 2:
        continue
    # Чем больше книг у автора, тем выше вес (можно также добавить случайность)
    base_weight = min(10, len(book_ids) * 2)
    for book_a, book_b in combinations(book_ids, 2):
        # Чтобы пары были уникальными, сохраняем с (min_id, max_id)
        a, b = sorted([book_a, book_b])
        existing = db.query(BookCoOccurrence).filter(
            BookCoOccurrence.book_id_a == a,
            BookCoOccurrence.book_id_b == b
        ).first()
        if existing:
            existing.co_borrow_count += base_weight
        else:
            co = BookCoOccurrence(book_id_a=a, book_id_b=b, co_borrow_count=base_weight)
            db.add(co)
        pair_count += 1

# 4. Добавляем немного кросс-авторских связей (например, классики XIX века)
#    Для демонстрации возьмём книги с годом выпуска между 1800 и 1900
classic_books = db.query(Book).filter(Book.year.between(1800, 1900)).limit(100).all()
classic_ids = [b.id for b in classic_books]
for i in range(min(200, len(classic_ids) * 2)):
    import random
    a, b = random.sample(classic_ids, 2)
    a, b = sorted([a, b])
    existing = db.query(BookCoOccurrence).filter(
        BookCoOccurrence.book_id_a == a,
        BookCoOccurrence.book_id_b == b
    ).first()
    if existing:
        existing.co_borrow_count += 5
    else:
        db.add(BookCoOccurrence(book_id_a=a, book_id_b=b, co_borrow_count=5))

db.commit()
print(f"Создано {pair_count} пар книг в таблице co-occurrence")
db.close()