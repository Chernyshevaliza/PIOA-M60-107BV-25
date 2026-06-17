# tests/test_memory.py
import unittest

from src.db.backend.memory import BookTable
from src.db.backend.errors import (
    DuplicateIDError,
    InvalidYearError,
    EmptyFieldError,
    RecordNotFoundError,
)


class TestBookTableCreate(unittest.TestCase):
    def setUp(self):
        self.table = BookTable()

    def test_create_record_success(self):
        record = self.table.create_record(1, "1984", "George Orwell", 1949)
        self.assertEqual(record, (1, "1984", "George Orwell", 1949))
        self.assertEqual(len(self.table._books), 1)

    def test_create_record_duplicate_id(self):
        self.table.create_record(1, "1984", "Orwell", 1949)
        with self.assertRaises(DuplicateIDError):
            self.table.create_record(1, "Animal Farm", "Orwell", 1945)

    def test_create_record_invalid_year(self):
        with self.assertRaises(InvalidYearError):
            self.table.create_record(1, "Book", "Author", -1)

    def test_create_record_strips_whitespace(self):
        record = self.table.create_record(1, "  1984  ", "  Orwell  ", 1949)
        self.assertEqual(record[1], "1984")
        self.assertEqual(record[2], "Orwell")

    def test_create_multiple_records(self):
        self.table.create_record(1, "1984", "Orwell", 1949)
        self.table.create_record(2, "Animal Farm", "Orwell", 1945)
        self.assertEqual(len(self.table._books), 2)


class TestBookTableSelect(unittest.TestCase):
    def setUp(self):
        self.table = BookTable()
        self.table.create_record(1, "1984", "George Orwell", 1949)
        self.table.create_record(2, "Animal Farm", "George Orwell", 1945)
        self.table.create_record(3, "Brave New World", "Aldous Huxley", 1932)

    def test_select_all_records(self):
        books = self.table.select_record()
        self.assertEqual(len(books), 3)

    def test_select_by_id(self):
        books = self.table.select_record(book_id=1)
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0][1], "1984")

    def test_select_by_title(self):
        books = self.table.select_record(title="1984")
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0][0], 1)

    def test_select_by_author(self):
        books = self.table.select_record(author="George Orwell")
        self.assertEqual(len(books), 2)

    def test_select_by_year(self):
        books = self.table.select_record(year=1949)
        self.assertEqual(len(books), 1)

    def test_select_by_multiple_filters(self):
        books = self.table.select_record(author="George Orwell", year=1949)
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0][1], "1984")

    def test_select_no_matches(self):
        books = self.table.select_record(author="Unknown")
        self.assertEqual(len(books), 0)

    def test_select_returns_copy(self):
        books = self.table.select_record()
        books.clear()
        self.assertEqual(len(self.table._books), 3)


class TestBookTableUpdate(unittest.TestCase):
    def setUp(self):
        self.table = BookTable()
        self.table.create_record(1, "1984", "George Orwell", 1949)
        self.table.create_record(2, "Animal Farm", "George Orwell", 1945)

    def test_update_record_success(self):
        updated = self.table.update_record(1, title="Nineteen Eighty-Four")
        self.assertEqual(updated[1], "Nineteen Eighty-Four")
        self.assertEqual(updated[0], 1)

    def test_update_record_not_found(self):
        with self.assertRaises(RecordNotFoundError):
            self.table.update_record(999, title="X")

    def test_update_record_invalid_year(self):
        with self.assertRaises(InvalidYearError):
            self.table.update_record(1, year=-1)

    def test_update_record_preserves_other_fields(self):
        self.table.update_record(1, title="X")
        books = self.table.select_record(book_id=1)
        self.assertEqual(books[0][2], "George Orwell")
        self.assertEqual(books[0][3], 1949)

    def test_update_multiple_fields(self):
        updated = self.table.update_record(1, title="X", year=1950)
        self.assertEqual(updated[1], "X")
        self.assertEqual(updated[3], 1950)


class TestBookTableDelete(unittest.TestCase):
    def setUp(self):
        self.table = BookTable()
        self.table.create_record(1, "1984", "Orwell", 1949)
        self.table.create_record(2, "Animal Farm", "Orwell", 1945)

    def test_delete_record_success(self):
        result = self.table.delete_record(1)
        self.assertTrue(result)
        self.assertEqual(len(self.table._books), 1)

    def test_delete_record_not_found(self):
        with self.assertRaises(RecordNotFoundError):
            self.table.delete_record(999)

    def test_delete_all_records(self):
        self.table.delete_record(1)
        self.table.delete_record(2)
        self.assertEqual(len(self.table._books), 0)


class TestBookTableSort(unittest.TestCase):
    def setUp(self):
        self.table = BookTable()
        self.table.create_record(1, "1984", "George Orwell", 1949)
        self.table.create_record(2, "Animal Farm", "George Orwell", 1945)
        self.table.create_record(3, "Brave New World", "Aldous Huxley", 1932)

    def test_sort_by_id_ascending(self):
        books = self.table.sort_records("book_id", reverse=False)
        self.assertEqual(books[0][0], 1)
        self.assertEqual(books[2][0], 3)

    def test_sort_by_id_descending(self):
        books = self.table.sort_records("book_id", reverse=True)
        self.assertEqual(books[0][0], 3)
        self.assertEqual(books[2][0], 1)

    def test_sort_by_title(self):
        books = self.table.sort_records("title")
        self.assertEqual(books[0][1], "1984")
        self.assertEqual(books[1][1], "Animal Farm")
        self.assertEqual(books[2][1], "Brave New World")

    def test_sort_by_author(self):
        books = self.table.sort_records("author")
        self.assertEqual(books[0][2], "Aldous Huxley")
        self.assertEqual(books[2][2], "George Orwell")

    def test_sort_by_year(self):
        books = self.table.sort_records("year")
        self.assertEqual(books[0][3], 1932)
        self.assertEqual(books[2][3], 1949)

    def test_sort_invalid_field(self):
        with self.assertRaises(ValueError):
            self.table.sort_records("invalid_field")

    def test_sort_returns_copy(self):
        books = self.table.sort_records("book_id")
        books.clear()
        self.assertEqual(len(self.table._books), 3)


if __name__ == "__main__":
    unittest.main()