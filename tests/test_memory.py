# tests/test_memory.py
import unittest

from src.db.backend.memory import MemoryDatabase
from src.db.backend.errors import (
    TableNotFoundError,
    TableAlreadyExistsError,
    MissingColumnError,
    UnknownColumnError,
)


class TestMemoryDatabase(unittest.TestCase):
    def setUp(self):
        self.db = MemoryDatabase()

    def test_create_table(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        self.assertTrue(self.db._table_exists("books"))

    def test_create_duplicate_table(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("books", ("book_id", "title", "author", "year"))

    def test_insert_record(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        self.db.insert_record("books", {"book_id": 1, "title": "1984", "author": "George Orwell", "year": 1949})
        records = self.db.select_records("books")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["title"], "1984")

    def test_insert_record_missing_column(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        with self.assertRaises(MissingColumnError):
            self.db.insert_record("books", {"book_id": 1, "title": "1984"})

    def test_insert_record_unknown_column(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        with self.assertRaises(UnknownColumnError):
            self.db.insert_record("books", {
                "book_id": 1,
                "title": "1984",
                "author": "Orwell",
                "year": 1949,
                "genre": "fiction"
            })

    def test_select_with_filters(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        self.db.insert_record("books", {"book_id": 1, "title": "1984", "author": "George Orwell", "year": 1949})
        self.db.insert_record("books", {"book_id": 2, "title": "Brave New World", "author": "Aldous Huxley", "year": 1932})

        records = self.db.select_records("books", author="Aldous Huxley")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["title"], "Brave New World")

    def test_select_unknown_filter_column(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        with self.assertRaises(UnknownColumnError):
            self.db.select_records("books", genre="fiction")

    def test_select_from_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("books")

    def test_update_record(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        self.db.insert_record("books", {"book_id": 1, "title": "1984", "author": "George Orwell", "year": 1949})
        updated = self.db.update_record("books", "book_id", 1, {"title": "Nineteen Eighty-Four"})
        self.assertTrue(updated)
        records = self.db.select_records("books", book_id=1)
        self.assertEqual(records[0]["title"], "Nineteen Eighty-Four")

    def test_update_record_not_found(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        updated = self.db.update_record("books", "book_id", 999, {"title": "X"})
        self.assertFalse(updated)

    def test_delete_record(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        self.db.insert_record("books", {"book_id": 1, "title": "1984", "author": "George Orwell", "year": 1949})
        deleted = self.db.delete_record("books", "book_id", 1)
        self.assertTrue(deleted)
        records = self.db.select_records("books")
        self.assertEqual(len(records), 0)

    def test_delete_record_not_found(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        deleted = self.db.delete_record("books", "book_id", 999)
        self.assertFalse(deleted)

    def test_create_index(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        self.db.create_index("books", "author")
        self.db.insert_record("books", {"book_id": 1, "title": "1984", "author": "Orwell", "year": 1949})
        records = self.db.select_records("books", author="Orwell")
        self.assertEqual(len(records), 1)


if __name__ == "__main__":
    unittest.main()