import tempfile
import unittest

from src.db.backend.file import FileDatabase
from src.db.backend.errors import TableNotFoundError


class TestFileDatabase(unittest.TestCase):
    def test_data_is_saved_between_instances(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first_db = FileDatabase(directory)
            first_db.create_table("books", ("book_id", "title", "author", "year"))
            first_db.insert_record(
                "books",
                {"book_id": 1, "title": "1984", "author": "George Orwell", "year": 1949},
            )

            second_db = FileDatabase(directory)
            records = second_db.select_records("books")

            self.assertEqual(
                records,
                [{"book_id": 1, "title": "1984", "author": "George Orwell", "year": 1949}],
            )

    def test_select_with_filters(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = FileDatabase(directory)
            db.create_table("books", ("book_id", "title", "author", "year"))
            db.insert_record("books", {"book_id": 1, "title": "1984", "author": "George Orwell", "year": 1949})
            db.insert_record("books", {"book_id": 2, "title": "Brave New World", "author": "Aldous Huxley", "year": 1932})

            records = db.select_records("books", author="Aldous Huxley")

            self.assertEqual(
                records,
                [{"book_id": 2, "title": "Brave New World", "author": "Aldous Huxley", "year": 1932}],
            )

    def test_select_from_missing_table(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = FileDatabase(directory)

            with self.assertRaises(TableNotFoundError):
                db.select_records("books")