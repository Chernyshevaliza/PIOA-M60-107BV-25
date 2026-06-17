# src/db/backend/errors.py
class DatabaseError(Exception):
    """Базовый класс для ошибок базы данных."""


class TableAlreadyExistsError(DatabaseError):
    """Ошибка при попытке создать уже существующую таблицу."""


class TableNotFoundError(DatabaseError):
    """Ошибка при обращении к несуществующей таблице."""


class MissingColumnError(DatabaseError):
    """Ошибка при отсутствии обязательного поля в записи."""


class UnknownColumnError(DatabaseError):
    """Ошибка при использовании поля, которого нет в схеме таблицы."""


class InvalidStorageDataError(DatabaseError):
    """Ошибка при чтении повреждённых данных из файла."""