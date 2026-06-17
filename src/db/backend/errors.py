class BookTableError(Exception):
    """Базовый класс для ошибок таблицы Book."""
    pass

class InvalidYearError(BookTableError):
    """Ошибка: некорректный год (отрицательный)."""
    pass

class DuplicateIDError(BookTableError):
    """Ошибка: дубликат ID."""
    pass

class EmptyFieldError(BookTableError):
    """Ошибка: пустое обязательное поле."""
    pass

class RecordNotFoundError(BookTableError):
    """Ошибка: запись не найдена."""
    pass