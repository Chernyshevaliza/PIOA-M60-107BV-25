# src/db/backend/database.py
from abc import ABC, abstractmethod
from typing import Any

from .errors import TableAlreadyExistsError
from .table import Table


class Database(ABC):
    """Общий интерфейс базы данных."""

    def create_table(self, table_name: str, columns: tuple[str, ...]) -> None:
        if self._table_exists(table_name):
            raise TableAlreadyExistsError(
                f"Таблица '{table_name}' уже существует."
            )

        self._save_table(table_name, Table(columns))

    def insert_record(self, table_name: str, record: dict[str, Any]) -> None:
        table = self._load_table(table_name)
        table.insert_record(record)
        self._save_table(table_name, table)

    def select_records(self, table_name: str, **filters: Any) -> list[dict[str, Any]]:
        table = self._load_table(table_name)
        return table.select_records(**filters)

    def update_record(self, table_name: str, key_field: str, key_value: Any, updates: dict[str, Any]) -> bool:
        table = self._load_table(table_name)
        updated = table.update_record(key_field, key_value, updates)
        if updated:
            self._save_table(table_name, table)
        return updated

    def delete_record(self, table_name: str, key_field: str, key_value: Any) -> bool:
        table = self._load_table(table_name)
        deleted = table.delete_record(key_field, key_value)
        if deleted:
            self._save_table(table_name, table)
        return deleted

    def create_index(self, table_name: str, field: str) -> None:
        table = self._load_table(table_name)
        table.create_index(field)
        self._save_table(table_name, table)

    @abstractmethod
    def _table_exists(self, table_name: str) -> bool:
        """Проверяет наличие таблицы."""

    @abstractmethod
    def _load_table(self, table_name: str) -> Table:
        """Загружает таблицу."""

    @abstractmethod
    def _save_table(self, table_name: str, table: Table) -> None:
        """Сохраняет таблицу."""