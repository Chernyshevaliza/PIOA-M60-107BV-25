
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


def update_record(
    book_id: int,
    title: Optional[str] = None,
    author: Optional[str] = None,
    year: Optional[int] = None,
) -> BookRecord:
    for i, record in enumerate(Books):
        if record[0] == book_id:
            new_title = title if title is not None else record[1]
            new_author = author if author is not None else record[2]
            new_year = year if year is not None else record[3]
            
            if new_title is not None:
                new_title = new_title.strip()
                if not new_title:
                    raise ValueError("Название книги не может быть пустым.")
            
            if new_author is not None:
                new_author = new_author.strip()
                if not new_author:
                    raise ValueError("Автор не может быть пустым.")
            
            if new_year is not None and new_year < 0:
                raise ValueError("Год не может быть отрицательным.")
            
            updated_record: BookRecord = (book_id, new_title, new_author, new_year)
            Books[i] = updated_record
            return updated_record
    
    raise ValueError(f"Запись с id={book_id} не найдена.")


def delete_record(book_id: int) -> bool:
    for i, record in enumerate(Books):
        if record[0] == book_id:
            Books.pop(i)
            return True
    
    raise ValueError(f"Запись с id={book_id} не найдена.")