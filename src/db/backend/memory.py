
from typing import Optional

BookRecord = tuple[int, str, str, int]

Books: list[BookRecord] = []


def create_record(
    book_id: int,
    title: str,
    author: str,
    year: int,
) -> BookRecord:
    if year < 0:
        raise ValueError("Год не может быть отрицательным.")
    
    if any(record[0] == book_id for record in Books):
        raise ValueError(f"Запись с id={book_id} уже существует.")
    
    title = title.strip()
    author = author.strip()
    
    if not title:
        raise ValueError("Название книги не может быть пустым.")
    if not author:
        raise ValueError("Автор не может быть пустым.")
    
    new_record: BookRecord = (book_id, title, author, year)
    Books.append(new_record)
    return new_record


def select_record(
    book_id: Optional[int] = None,
    title: Optional[str] = None,
    author: Optional[str] = None,
    year: Optional[int] = None,
) -> list[BookRecord]:
    if book_id is None and title is None and author is None and year is None:
        return Books.copy()
    
    result: list[BookRecord] = []
    
    for record in Books:
        if book_id is not None and record[0] != book_id:
            continue
        if title is not None and record[1] != title:
            continue
        if author is not None and record[2] != author:
            continue
        if year is not None and record[3] != year:
            continue
        result.append(record)
    
    return result


def get_all_records() -> list[BookRecord]:
    return Books.copy()