# src/db/backend/csv_file.py
import csv
import json
from pathlib import Path

from .database import Database
from .errors import InvalidStorageDataError, TableNotFoundError
from .table import Table


class CsvDatabase(Database):
    """База данных, хранящая таблицы в CSV-файлах."""

    def __init__(self, directory: str = "data_csv") -> None:
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
                reader = csv.reader(file)
                rows = list(reader)
                if not rows:
                    raise InvalidStorageDataError("CSV-файл пуст.")

                columns = tuple(rows[0])
                records = []
                for row_idx, row in enumerate(rows[1:], start=2):
                    if len(row) != len(columns):
                        raise InvalidStorageDataError(
                            f"Некорректное количество полей в строке {row_idx} CSV-файла."
                        )
                    record = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        if col in ("book_id", "year"):
                            try:
                                value = int(value)
                            except ValueError:
                                pass
                        record[col] = value
                    records.append(record)

                table = Table(columns, records)
                
                metadata_path = self._get_metadata_path(table_name)
                if metadata_path.exists():
                    with metadata_path.open("r", encoding="utf-8") as meta_file:
                        metadata = json.load(meta_file)
                        if "indexes" in metadata and isinstance(metadata["indexes"], list):
                            for field in metadata["indexes"]:
                                if field in columns:
                                    table.create_index(field)

                return table
        except (csv.Error, ValueError) as error:
            raise InvalidStorageDataError(
                "Ошибка при чтении CSV-файла."
            ) from error
        except OSError as error:
            raise InvalidStorageDataError(
                f"Ошибка чтения файла таблицы '{table_name}'."
            ) from error

    def _save_table(self, table_name: str, table: Table) -> None:
        table_path = self._get_table_path(table_name)

        try:
            with table_path.open("w", encoding="utf-8", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(table.columns)
                for record in table.records:
                    row = [str(record.get(col, "")) for col in table.columns]
                    writer.writerow(row)
            
            metadata_path = self._get_metadata_path(table_name)
            metadata = {
                "indexes": table.get_index_fields()
            }
            with metadata_path.open("w", encoding="utf-8") as meta_file:
                json.dump(metadata, meta_file, ensure_ascii=False, indent=2)
        except OSError as error:
            raise InvalidStorageDataError(
                f"Ошибка записи файла таблицы '{table_name}'."
            ) from error

    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.csv"

    def _get_metadata_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.meta.json"

    def update_record(self, table_name: str, key_field: str, key_value: any, updates: dict[str, any]) -> bool:
        table = self._load_table(table_name)
        updated = table.update_record(key_field, key_value, updates)
        if updated:
            self._save_table(table_name, table)
        return updated

    def delete_record(self, table_name: str, key_field: str, key_value: any) -> bool:
        table = self._load_table(table_name)
        deleted = table.delete_record(key_field, key_value)
        if deleted:
            self._save_table(table_name, table)
        return deleted