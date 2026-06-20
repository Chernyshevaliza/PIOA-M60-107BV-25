# Лабораторная работа №4


### Структура проекта
- `src/db/backend/database.py` — абстрактный класс Database
- `src/db/backend/table.py` — класс Table (структура таблицы + индексация)
- `src/db/backend/memory.py` — MemoryDatabase (данные в памяти)
- `src/db/backend/file.py` — FileDatabase (данные в JSON-файлах)
- `src/db/backend/csv_file.py` — CsvDatabase (данные в CSV-файлах)
- `src/db/backend/errors.py` — пользовательские исключения
- `src/db/tui.py` — текстовый интерфейс (класс BookUI)
- `src/db/__main__.py` — точка входа
- `tests/test_memory.py` — тесты для in-memory БД
- `tests/test_file_database.py` — тесты для JSON БД
- `tests/test_csv_database.py` — тесты для CSV БД
- `tests/test_table.py`
- `tests/test_tui.py`
- `data/` — папка для JSON-файлов
- `data_csv/` — папка для CSV-файлов

### Функциональность
- Создание таблицы `books` (book_id, title, author, year)
- Добавление записей
- Чтение записей с фильтрацией по одному или нескольким полям
- Выбор типа базы данных при запуске:
  - In-memory (данные в оперативной памяти)
  - File database (JSON) — данные сохраняются в `data/`
  - File database (CSV) — данные сохраняются в `data_csv/`
- Индексация по полям таблицы для ускорения поиска
- Данные сохраняются на диск и загружаются при следующем запуске

### Запуск
```bash
python3 -m src.db