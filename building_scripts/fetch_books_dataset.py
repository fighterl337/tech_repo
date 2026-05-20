import csv
import requests
import os
import tempfile
import zipfile
import io
import random

# --- 1. Загрузка данных из датасета "RusLit" (GitHub) ---
def fetch_russian_literature_dataset():
    """Скачивает и парсит датасет русской литературы, извлекая названия, авторов и годы."""
    print("Обработка датасета русской литературы...")
    books = []
    # Ссылка на ZIP-архив с датасетом из репозитория d0rj/RusLit
    url = "https://github.com/d0rj/RusLit/archive/refs/heads/main.zip"
    try:
        response = requests.get(url)
        response.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
            for file_info in zf.infolist():
                # Ищем все файлы _info.csv в папках prose и poetry
                if file_info.filename.endswith('_info.csv') and ('/prose/' in file_info.filename or '/poems/' in file_info.filename):
                    with zf.open(file_info) as csv_file:
                        # Определяем автора из пути к файлу
                        author_path = file_info.filename.split('/')[-2] if 'prose' in file_info.filename else file_info.filename.split('/')[-2]
                        author = author_path.replace('_', ' ').strip()
                        reader = csv.reader(io.TextIOWrapper(csv_file, encoding='utf-8'))
                        next(reader)  # пропускаем заголовок
                        for row in reader:
                            if len(row) >= 2:
                                title = row[0].strip()
                                year = row[1].strip()
                                # Обработка года
                                year_clean = None
                                if year and year != 'None' and not '-' in year:
                                    try:
                                        year_clean = int(year.split()[0])
                                    except ValueError:
                                        pass
                                if title and author and year_clean:
                                    books.append({
                                        'title': title,
                                        'author': author,
                                        'year': year_clean
                                    })
    except Exception as e:
        print(f"Ошибка при загрузке датасета RusLit: {e}")
        print("Продолжаем с использованием API...")
    print(f"Из датасета получено {len(books)} книг.")
    return books

# --- 2. Получение данных через Open Library API ---
def fetch_from_openlibrary():
    """Получает данные о книгах из Open Library API по ключевым словам."""
    print("Получение данных из Open Library API...")
    books = []
    keywords = [
        "russian literature", "русская литература", "world fiction", "classic novel",
        "contemporary fiction", "historical novel", "science fiction", "detective",
        "romance novel", "thriller", "fantasy"
    ]
    total_needed = 800 # Целевое количество книг, которое нужно получить через API

    for keyword in keywords:
        if len(books) >= total_needed:
            break
        limit = min(100, total_needed - len(books))
        url = f"http://openlibrary.org/search.json?q={keyword}&limit={limit}&fields=key,title,author_name,first_publish_year"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            for doc in data.get('docs', []):
                title = doc.get('title')
                author = doc.get('author_name', [''])[0] if doc.get('author_name') else ''
                year = doc.get('first_publish_year')
                if title and author and year:
                    books.append({
                        'title': title,
                        'author': author,
                        'year': year
                    })
            print(f"  По ключевому слову '{keyword}' получено {len(data.get('docs', []))} книг.")
        except Exception as e:
            print(f"  Ошибка при запросе к OpenLibrary для '{keyword}': {e}")
    print(f"Из Open Library получено {len(books)} книг.")
    return books

# --- 3. Объединение, дедупликация и сохранение ---
def main():
    # Собираем книги из двух источников
    all_books = []
    all_books.extend(fetch_russian_literature_dataset())
    all_books.extend(fetch_from_openlibrary())

    # Удаляем дубликаты по названию + автору
    unique_books = {}
    for book in all_books:
        key = f"{book['title'].lower()}|{book['author'].lower()}"
        if key not in unique_books:
            unique_books[key] = book

    final_books = list(unique_books.values())

    print(f"\nВсего собрано уникальных книг: {len(final_books)}")

    # При необходимости обрезаем или добиваем до 1000 книг
    if len(final_books) > 1000:
        random.shuffle(final_books)
        final_books = final_books[:1000]
        print(f"Случайным образом отобрано 1000 книг.")

    # Сохраняем в CSV
    output_file = 'books_dataset.csv'
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'author', 'year']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_books)

    print(f"Датасет из {len(final_books)} книг сохранён в файл {output_file}")
    print("\nПримеры книг в датасете:")
    for i, book in enumerate(final_books[:10]):
        print(f"  {i+1}. {book['title']} — {book['author']} ({book['year']})")

if __name__ == "__main__":
    main()