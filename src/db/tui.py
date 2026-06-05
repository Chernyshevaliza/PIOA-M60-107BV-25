from .backend.memory import create_record, select_record, get_all_records


def _print_menu() -> None:
    print("\n=== База данных книг ===")
    print("1. Добавить запись")
    print("2. Показать все записи")
    print("3. Найти записи по фильтру")
    print("0. Выход")


def _read_int(prompt: str) -> int:
    while True:
        try:
            value = input(prompt).strip()
            if not value:
                print("Ошибка: введите число.")
                continue
            return int(value)
        except ValueError:
            print("Ошибка: введите целое число.")


def _read_str(prompt: str, allow_empty: bool = False) -> str:
    while True:
        value = input(prompt).strip()
        if value or allow_empty:
            return value
        print("Ошибка: это поле не может быть пустым.")


def _add_book() -> None:
    print("\n--- Добавление новой книги ---")
    
    try:
        book_id = _read_int("ID книги: ")
        title = _read_str("Название: ")
        author = _read_str("Автор: ")
        year = _read_int("Год издания: ")
        
        record = create_record(book_id, title, author, year)
        print(f"Книга добавлена. ID: {record[0]}, Название: {record[1]}, Автор: {record[2]}, Год: {record[3]}")
        
    except ValueError as e:
        print(f"Ошибка: {e}")


def _show_all_books() -> None:
    records = get_all_records()
    
    if not records:
        print("\nНет записей в базе данных.")
        return
    
    print("\nСписок всех книг:")
    print("-" * 60)
    for r in records:
        print(f"  ID: {r[0]} | {r[1]} | {r[2]} | {r[3]}")
    print("-" * 60)
    print(f"Всего записей: {len(records)}")


def _find_books_by_filter() -> None:
    print("\n--- Поиск книг ---")
    print("(оставьте поле пустым, если не нужно фильтровать)")
    
    filter_id = None
    filter_title = None
    filter_author = None
    filter_year = None
    
    id_input = input("ID: ").strip()
    if id_input:
        try:
            filter_id = int(id_input)
        except ValueError:
            print("ID игнорируется (не число)")
    
    title_input = input("Название: ").strip()
    if title_input:
        filter_title = title_input
    
    author_input = input("Автор: ").strip()
    if author_input:
        filter_author = author_input
    
    year_input = input("Год: ").strip()
    if year_input:
        try:
            filter_year = int(year_input)
        except ValueError:
            print("Год игнорируется (не число)")
    
    try:
        results = select_record(filter_id, filter_title, filter_author, filter_year)
        
        if not results:
            print("\nНичего не найдено.")
            return
        
        print(f"\nНайдено {len(results)} записей:")
        print("-" * 60)
        for r in results:
            print(f"  ID: {r[0]} | {r[1]} | {r[2]} | {r[3]}")
        print("-" * 60)
        
    except Exception as e:
        print(f"Ошибка при поиске: {e}")


def run() -> None:
    print("Запуск базы данных книг")
    
    while True:
        _print_menu()
        choice = input("Выберите действие: ").strip()
        
        if choice == "1":
            _add_book()
        elif choice == "2":
            _show_all_books()
        elif choice == "3":
            _find_books_by_filter()
        elif choice == "0":
            print("До свидания!")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")