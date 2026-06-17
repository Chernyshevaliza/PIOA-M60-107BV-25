from .backend.file import FileDatabase
from .backend.memory import MemoryDatabase
from .backend.csv_file import CsvDatabase
from .backend.errors import (
    DatabaseError,
    TableAlreadyExistsError,
    TableNotFoundError,
    MissingColumnError,
    UnknownColumnError,
)


class BookUI:
    def __init__(self) -> None:
        print("\n=== Выбор типа базы данных ===")
        print("1. In-memory (данные в оперативной памяти)")
        print("2. File database (JSON)")
        print("3. File database (CSV)")

        choice = input("Введите номер: ").strip()
        if choice == "2":
            self.database = FileDatabase()
            print("Используется файловая база данных (JSON, папка 'data/')")
        elif choice == "3":
            self.database = CsvDatabase()
            print("Используется файловая база данных (CSV, папка 'data_csv/')")
        else:
            self.database = MemoryDatabase()
            print("Используется in-memory база данных")

        self._ensure_books_table()

    def _ensure_books_table(self) -> None:
        """Создаёт таблицу books, если её ещё нет."""
        try:
            self.database.create_table(
                "books",
                ("book_id", "title", "author", "year")
            )
        except TableAlreadyExistsError:
            pass

    def _print_menu(self) -> None:
        print("\n=== База данных книг ===")
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Найти записи по фильтру")
        print("0. Выход")

    def _read_int(self, prompt: str) -> int:
        while True:
            try:
                value = input(prompt).strip()
                if not value:
                    print("Ошибка: введите число.")
                    continue
                return int(value)
            except ValueError:
                print("Ошибка: введите целое число.")

    def _read_str(self, prompt: str, allow_empty: bool = False) -> str:
        while True:
            value = input(prompt).strip()
            if value or allow_empty:
                return value
            print("Ошибка: это поле не может быть пустым.")

    def _add_book(self) -> None:
        print("\n--- Добавление новой книги ---")
        try:
            book_id = self._read_int("ID книги: ")
            title = self._read_str("Название: ")
            author = self._read_str("Автор: ")
            year = self._read_int("Год издания: ")

            self.database.insert_record(
                "books",
                {"book_id": book_id, "title": title, "author": author, "year": year}
            )
            print("Книга успешно добавлена.")
        except (MissingColumnError, UnknownColumnError, TableNotFoundError) as e:
            print(f"Ошибка: {e}")

    def _show_all_books(self) -> None:
        try:
            records = self.database.select_records("books")
            if not records:
                print("\nНет записей в базе данных.")
                return

            print("\nСписок всех книг:")
            print("-" * 60)
            for r in records:
                print(f"  ID: {r['book_id']} | {r['title']} | {r['author']} | {r['year']}")
            print("-" * 60)
            print(f"Всего записей: {len(records)}")
        except TableNotFoundError as e:
            print(f"Ошибка: {e}")

    def _find_books_by_filter(self) -> None:
        print("\n--- Поиск книг ---")
        print("(оставьте поле пустым, если не нужно фильтровать)")

        filters = {}

        book_id = input("ID книги: ").strip()
        if book_id:
            try:
                filters["book_id"] = int(book_id)
            except ValueError:
                print("ID игнорируется (не число)")

        title = input("Название: ").strip()
        if title:
            filters["title"] = title

        author = input("Автор: ").strip()
        if author:
            filters["author"] = author

        year = input("Год: ").strip()
        if year:
            try:
                filters["year"] = int(year)
            except ValueError:
                print("Год игнорируется (не число)")

        try:
            records = self.database.select_records("books", **filters)
            if not records:
                print("\nНичего не найдено.")
            else:
                print(f"\nНайдено {len(records)} записей:")
                print("-" * 60)
                for r in records:
                    print(f"  ID: {r['book_id']} | {r['title']} | {r['author']} | {r['year']}")
                print("-" * 60)
        except (UnknownColumnError, TableNotFoundError) as e:
            print(f"Ошибка: {e}")

    def run(self) -> None:
        while True:
            self._print_menu()
            choice = input("Выберите действие: ").strip()

            if choice == "1":
                self._add_book()
            elif choice == "2":
                self._show_all_books()
            elif choice == "3":
                self._find_books_by_filter()
            elif choice == "0":
                print("До свидания!")
                break
            else:
                print("Неверный выбор. Попробуйте снова.")