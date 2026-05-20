# clean_books.py
import csv
from app.database import SessionLocal
from app.models import Book

db = SessionLocal()

# Удаляем все книги
deleted = db.query(Book).delete()
db.commit()
print(f"Удалено {deleted} старых книг")

# Загружаем из CSV
with open('books_dataset.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        book = Book(
            title=row['title'],
            author=row['author'],
            year=int(row['year']) if row['year'] else None,
            status='available'
        )
        db.add(book)
        count += 1
    db.commit()
    print(f"Загружено {count} новых книг")

db.close()