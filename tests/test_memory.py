import unittest
from src.db.backend.memory import MemoryDatabase
from src.db.backend.errors import TableNotFoundError


class TestMemoryDatabase(unittest.TestCase):
    def setUp(self):
        self.db = MemoryDatabase()

    def test_create_table(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        self.assertTrue(self.db._table_exists("books"))

    def test_insert_record(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        self.db.insert_record("books", {"book_id": 1, "title": "1984", "author": "George Orwell", "year": 1949})
        records = self.db.select_records("books")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["title"], "1984")

    def test_select_with_filters(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        self.db.insert_record("books", {"book_id": 1, "title": "1984", "author": "George Orwell", "year": 1949})
        self.db.insert_record("books", {"book_id": 2, "title": "Brave New World", "author": "Aldous Huxley", "year": 1932})

        records = self.db.select_records("books", author="Aldous Huxley")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["title"], "Brave New World")

    def test_select_from_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("books")


if __name__ == "__main__":
    unittest.main()