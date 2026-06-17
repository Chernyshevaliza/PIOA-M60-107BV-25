# src/db/tui.py
from .backend.memory import BookTable
from .backend.errors import (
    DuplicateIDError,
    InvalidYearError,
    EmptyFieldError,
    RecordNotFoundError,
)


class BookUI:
    """Текстовый интерфейс для управления библиотекой."""

    def __init__(self) -> None:
        self.table = BookTable()

    def _print_menu(self) -> None:
        print("\n=== База данных книг ===")
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Найти записи по фильтру")
        print("4. Обновить запись")
        print("5. Удалить запись")
        print("6. Сортировать записи")
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

            self.table.create_record(book_id, title, author, year)
            print("Книга успешно добавлена.")
        except DuplicateIDError as e:
            print(f"Ошибка: {e}")
        except InvalidYearError as e:
            print(f"Ошибка: {e}")
        except EmptyFieldError as e:
            print(f"Ошибка: {e}")

    def _show_all_books(self) -> None:
        print("\n--- Все книги ---")
        books = self.table.select_record()
        if not books:
            print("Нет книг в библиотеке.")
            return

        print(f"{'ID':<5} {'Название':<30} {'Автор':<20} {'Год':<5}")
        print("-" * 65)
        for book in books:
            print(f"{book[0]:<5} {book[1]:<30} {book[2]:<20} {book[3]:<5}")
        print(f"\nВсего записей: {len(books)}")

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

        books = self.table.select_record(**filters)

        if not books:
            print("\nНичего не найдено.")
        else:
            print(f"\nНайдено {len(books)} записей:")
            print(f"{'ID':<5} {'Название':<30} {'Автор':<20} {'Год':<5}")
            print("-" * 65)
            for book in books:
                print(f"{book[0]:<5} {book[1]:<30} {book[2]:<20} {book[3]:<5}")

    def _update_book(self) -> None:
        print("\n--- Обновление записи ---")
        try:
            book_id = self._read_int("ID книги для обновления: ")
            print("Оставьте поле пустым, если не хотите менять значение.")

            title = input("Новое название: ").strip()
            author = input("Новый автор: ").strip()
            year = input("Новый год: ").strip()

            updates = {}
            if title:
                updates["title"] = title
            if author:
                updates["author"] = author
            if year:
                try:
                    updates["year"] = int(year)
                except ValueError:
                    print("Год пропущен (не число)")

            if not updates:
                print("Нет полей для обновления.")
                return

            updated = self.table.update_record(book_id, **updates)
            print(f"Запись обновлена: {updated[0]} - {updated[1]}")
        except RecordNotFoundError as e:
            print(f"Ошибка: {e}")
        except InvalidYearError as e:
            print(f"Ошибка: {e}")
        except EmptyFieldError as e:
            print(f"Ошибка: {e}")

    def _delete_book(self) -> None:
        print("\n--- Удаление записи ---")
        try:
            book_id = self._read_int("ID книги для удаления: ")
            self.table.delete_record(book_id)
            print("Запись успешно удалена.")
        except RecordNotFoundError as e:
            print(f"Ошибка: {e}")

    def _sort_books(self) -> None:
        print("\n--- Сортировка записей ---")
        print("1. По ID")
        print("2. По названию")
        print("3. По автору")
        print("4. По году")

        choice = input("Выберите поле (1-4): ").strip()
        field_map = {"1": "book_id", "2": "title", "3": "author", "4": "year"}

        if choice not in field_map:
            print("Неверный выбор.")
            return

        reverse_choice = input("По убыванию? (y/n): ").strip().lower()
        reverse = reverse_choice == "y"

        books = self.table.sort_records(field_map[choice], reverse)

        print(f"\n{'ID':<5} {'Название':<30} {'Автор':<20} {'Год':<5}")
        print("-" * 65)
        for book in books:
            print(f"{book[0]:<5} {book[1]:<30} {book[2]:<20} {book[3]:<5}")

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
            elif choice == "4":
                self._update_book()
            elif choice == "5":
                self._delete_book()
            elif choice == "6":
                self._sort_books()
            elif choice == "0":
                print("До свидания!")
                break
            else:
                print("Неверный выбор. Попробуйте снова.")