import csv
from app.database import SessionLocal
from app.models import Book
from sqlalchemy.exc import IntegrityError

def load_books_from_csv(csv_file='books_dataset.csv'):
    db = SessionLocal()
    added_count = 0
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Проверяем, существует ли уже книга с таким названием и автором
                existing_book = db.query(Book).filter(
                    Book.title == row['title'],
                    Book.author == row['author']
                ).first()
                if not existing_book:
                    book = Book(
                        title=row['title'],
                        author=row['author'],
                        year=int(row['year']) if row['year'] else None,
                        status='available'  # По умолчанию книги доступны
                    )
                    db.add(book)
                    added_count += 1
                    if added_count % 100 == 0:
                        db.commit()
                        print(f"Загружено {added_count} книг...")
            db.commit()
            print(f"✅ Готово! Добавлено {added_count} новых книг в базу данных.")
    except Exception as e:
        print(f"❌ Ошибка при загрузке: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    load_books_from_csv()