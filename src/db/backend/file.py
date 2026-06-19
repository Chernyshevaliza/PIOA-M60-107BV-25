# src/db/backend/file.py
import json
from pathlib import Path

from .database import Database
from .errors import InvalidStorageDataError, TableNotFoundError
from .table import Table


class FileDatabase(Database):
    """База данных, которая хранит таблицы в JSON-файлах."""

    def __init__(self, directory: str = "data") -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _table_exists(self, table_name: str) -> bool:
        return self._get_table_path(table_name).exists()

    def _load_table(self, table_name: str) -> Table:
        table_path = self._get_table_path(table_name)
        if not table_path.exists():
            raise TableNotFoundError(
                f"Таблица '{table_name}' не существует."
            )

        try:
            with table_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise InvalidStorageDataError(
                "Файл таблицы содержит некорректный JSON."
            ) from error
        except OSError as error:
            raise InvalidStorageDataError(
                f"Ошибка чтения файла таблицы '{table_name}'."
            ) from error

        return self._deserialize_table(data)

    def _save_table(self, table_name: str, table: Table) -> None:
        table_path = self._get_table_path(table_name)

        try:
            with table_path.open("w", encoding="utf-8") as file:
                json.dump(
                    self._serialize_table(table),
                    file,
                    ensure_ascii=False,
                    indent=2,
                )
        except OSError as error:
            raise InvalidStorageDataError(
                f"Ошибка записи файла таблицы '{table_name}'."
            ) from error

    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.json"

    def _serialize_table(self, table: Table) -> dict:
        return {
            "columns": list(table.columns),
            "records": [record.copy() for record in table.records],
            "indexes": list(table._indexes.keys()) if hasattr(table, '_indexes') else []
        }

    def _deserialize_table(self, data: dict) -> Table:
        if "columns" not in data or "records" not in data:
            raise InvalidStorageDataError(
                "Файл таблицы имеет некорректную структуру."
            )

        if not isinstance(data["columns"], (list, tuple)):
            raise InvalidStorageDataError(
                "Поле 'columns' должно быть списком или кортежем."
            )

        if not isinstance(data["records"], list):
            raise InvalidStorageDataError(
                "Поле 'records' должно быть списком."
            )

        columns = tuple(data["columns"])
        records = data.get("records", [])

        for i, record in enumerate(records):
            if not isinstance(record, dict):
                raise InvalidStorageDataError(
                    f"Запись {i} должна быть словарём."
                )

        table = Table(columns, records)
        
        if "indexes" in data and isinstance(data["indexes"], list):
            for field in data["indexes"]:
                if field in columns:
                    table.create_index(field)

        return table