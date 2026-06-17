import csv
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
                for row in rows[1:]:
                    if len(row) != len(columns):
                        raise InvalidStorageDataError(
                            "Некорректное количество полей в CSV-файле."
                        )
                    record = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        if col == "book_id" or col == "year":
                            try:
                                value = int(value)
                            except ValueError:
                                pass
                        record[col] = value
                    records.append(record)
                
                return Table(columns, records)
        except (csv.Error, ValueError) as error:
            raise InvalidStorageDataError(
                "Ошибка при чтении CSV-файла."
            ) from error

    def _save_table(self, table_name: str, table: Table) -> None:
        table_path = self._get_table_path(table_name)

        with table_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(table.columns)
            for record in table.records:
                row = [str(record.get(col, "")) for col in table.columns]
                writer.writerow(row)

    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.csv"