# src/db/backend/memory.py
from .errors import DuplicateIDError, InvalidYearError, EmptyFieldError, RecordNotFoundError

type BookRecord = tuple[int, str, str, int]


class BookTable:
    def __init__(self) -> None:
        self._books: list[BookRecord] = []

    def create_record(
        self,
        book_id: int,
        title: str,
        author: str,
        year: int,
    ) -> BookRecord:

        if year < 0:
            raise InvalidYearError("Год не может быть отрицательным.")

        if any(record[0] == book_id for record in self._books):
            raise DuplicateIDError(f"Запись с id={book_id} уже существует.")

        new_record: BookRecord = (
            book_id,
            title.strip(),
            author.strip(),
            year,
        )
        self._books.append(new_record)
        return new_record

    def select_record(
        self,
        book_id: int | None = None,
        title: str | None = None,
        author: str | None = None,
        year: int | None = None,
    ) -> list[BookRecord]:

        if (
            book_id is None
            and title is None
            and author is None
            and year is None
        ):
            return self._books.copy()

        result: list[BookRecord] = []

        for record in self._books:
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

    def update_record(
        self,
        book_id: int,
        title: str | None = None,
        author: str | None = None,
        year: int | None = None,
    ) -> BookRecord:
        for i, record in enumerate(self._books):
            if record[0] == book_id:
                new_title = title.strip() if title is not None else record[1]
                new_author = author.strip() if author is not None else record[2]
                new_year = year if year is not None else record[3]

                if not new_title:
                    raise EmptyFieldError("Название не может быть пустым.")
                if not new_author:
                    raise EmptyFieldError("Автор не может быть пустым.")
                if new_year < 0:
                    raise InvalidYearError("Год не может быть отрицательным.")

                updated = (book_id, new_title, new_author, new_year)
                self._books[i] = updated
                return updated

        raise RecordNotFoundError(f"Запись с id={book_id} не найдена.")

    def delete_record(self, book_id: int) -> bool:
        for i, record in enumerate(self._books):
            if record[0] == book_id:
                self._books.pop(i)
                return True
        raise RecordNotFoundError(f"Запись с id={book_id} не найдена.")

    def sort_records(self, key: str, reverse: bool = False) -> list[BookRecord]:
        field_map = {
            "book_id": 0,
            "title": 1,
            "author": 2,
            "year": 3,
        }

        if key not in field_map:
            raise ValueError(f"Недопустимое поле для сортировки: {key}")

        idx = field_map[key]
        return sorted(self._books.copy(), key=lambda x: x[idx], reverse=reverse)