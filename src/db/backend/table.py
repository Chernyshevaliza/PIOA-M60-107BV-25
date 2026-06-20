# src/db/backend/table.py
from typing import Any

from .errors import MissingColumnError, UnknownColumnError


class Table:
    """Таблица с фиксированным набором колонок и поддержкой индексов."""

    def __init__(self, columns: tuple[str, ...], records: list[dict[str, Any]] | None = None) -> None:
        self.columns = columns
        self.records: list[dict[str, Any]] = []
        self._indexes: dict[str, dict[Any, set[int]]] = {}

        if records is not None:
            for record in records:
                self.insert_record(record)

    def create_index(self, field: str) -> None:
        if field not in self.columns:
            raise UnknownColumnError(
                f"Поле '{field}' не определено в структуре таблицы."
            )
        if field in self._indexes:
            return  # Индекс уже существует, ничего не делаем
        index: dict[Any, set[int]] = {}
        for i, record in enumerate(self.records):
            value = record[field]
            if value not in index:
                index[value] = set()
            index[value].add(i)
        self._indexes[field] = index

    def has_index(self, field: str) -> bool:
        return field in self._indexes

    def get_index_fields(self) -> list[str]:
        """Возвращает список полей, по которым созданы индексы."""
        return list(self._indexes.keys())

    def insert_record(self, record: dict[str, Any]) -> None:
        missing_columns = [column for column in self.columns if column not in record]
        if missing_columns:
            raise MissingColumnError(
                f"Отсутствует поле '{missing_columns[0]}' в записи."
            )

        extra_columns = [column for column in record if column not in self.columns]
        if extra_columns:
            raise UnknownColumnError(
                f"Поле '{extra_columns[0]}' не определено в структуре таблицы."
            )

        idx = len(self.records)
        self.records.append(record.copy())

        for field, index in self._indexes.items():
            value = record[field]
            if value not in index:
                index[value] = set()
            index[value].add(idx)

    def select_records(self, **filters: Any) -> list[dict[str, Any]]:
        unknown_filters = [key for key in filters if key not in self.columns]
        if unknown_filters:
            raise UnknownColumnError(
                f"Поле '{unknown_filters[0]}' не определено в структуре таблицы."
            )

        if not filters:
            return [record.copy() for record in self.records]

        indexed_field = None
        for field in filters:
            if field in self._indexes:
                indexed_field = field
                break

        if indexed_field is not None:
            value = filters[indexed_field]
            candidate_indices = self._indexes[indexed_field].get(value, set())
            result: list[dict[str, Any]] = []
            for idx in candidate_indices:
                record = self.records[idx]
                if all(record.get(key) == val for key, val in filters.items()):
                    result.append(record.copy())
            return result

        result = []
        for record in self.records:
            if all(record.get(key) == value for key, value in filters.items()):
                result.append(record.copy())
        return result

    def update_record(self, key_field: str, key_value: Any, updates: dict[str, Any]) -> bool:
        if key_field not in self.columns:
            raise UnknownColumnError(
                f"Поле '{key_field}' не определено в структуре таблицы."
            )

        for extra_col in updates:
            if extra_col not in self.columns:
                raise UnknownColumnError(
                    f"Поле '{extra_col}' не определено в структуре таблицы."
                )

        for i, record in enumerate(self.records):
            if record.get(key_field) == key_value:
                old_values = {}
                for field in self._indexes:
                    if field in updates or field == key_field:
                        old_values[field] = record[field]

                for key, value in updates.items():
                    record[key] = value

                for field, index in self._indexes.items():
                    if field in old_values:
                        old_value = old_values[field]
                        new_value = record[field]
                        
                        if old_value != new_value:
                            index[old_value].discard(i)
                            if not index[old_value]:
                                del index[old_value]
                            
                            if new_value not in index:
                                index[new_value] = set()
                            index[new_value].add(i)

                return True
        return False

    def delete_record(self, key_field: str, key_value: Any) -> bool:
        if key_field not in self.columns:
            raise UnknownColumnError(
                f"Поле '{key_field}' не определено в структуре таблицы."
            )

        for i, record in enumerate(self.records):
            if record.get(key_field) == key_value:
                for field, index in self._indexes.items():
                    value = record[field]
                    index[value].discard(i)
                    new_index: dict[Any, set[int]] = {}
                    for v, positions in index.items():
                        new_index[v] = {p - 1 if p > i else p for p in positions}
                    self._indexes[field] = new_index

                del self.records[i]
                return True
        return False