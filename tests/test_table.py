# tests/test_table.py
import unittest

from src.db.backend.table import Table
from src.db.backend.errors import MissingColumnError, UnknownColumnError


class TestTableBasic(unittest.TestCase):
    def test_create_table_empty(self):
        table = Table(("book_id", "title", "author", "year"))
        self.assertEqual(len(table.records), 0)
        self.assertEqual(table.columns, ("book_id", "title", "author", "year"))

    def test_create_table_with_records(self):
        records = [
            {"book_id": 1, "title": "1984", "author": "Orwell", "year": 1949}
        ]
        table = Table(("book_id", "title", "author", "year"), records)
        self.assertEqual(len(table.records), 1)

    def test_insert_record_success(self):
        table = Table(("book_id", "title", "author", "year"))
        table.insert_record({"book_id": 1, "title": "1984", "author": "Orwell", "year": 1949})
        self.assertEqual(len(table.records), 1)

    def test_insert_record_missing_column(self):
        table = Table(("book_id", "title", "author", "year"))
        with self.assertRaises(MissingColumnError):
            table.insert_record({"book_id": 1, "title": "1984"})

    def test_insert_record_unknown_column(self):
        table = Table(("book_id", "title", "author", "year"))
        with self.assertRaises(UnknownColumnError):
            table.insert_record({"book_id": 1, "title": "1984", "author": "Orwell", "year": 1949, "genre": "fiction"})

    def test_insert_record_copies_data(self):
        table = Table(("book_id", "title"))
        record = {"book_id": 1, "title": "1984"}
        table.insert_record(record)
        record["title"] = "Changed"
        self.assertEqual(table.records[0]["title"], "1984")

    def test_select_all_records(self):
        table = Table(("book_id", "title", "author", "year"), [
            {"book_id": 1, "title": "1984", "author": "Orwell", "year": 1949},
            {"book_id": 2, "title": "Animal Farm", "author": "Orwell", "year": 1945},
        ])
        records = table.select_records()
        self.assertEqual(len(records), 2)

    def test_select_records_copies_data(self):
        table = Table(("book_id", "title"), [
            {"book_id": 1, "title": "1984"}
        ])
        records = table.select_records()
        records[0]["title"] = "Changed"
        self.assertEqual(table.records[0]["title"], "1984")

    def test_select_with_filter(self):
        table = Table(("book_id", "title", "author", "year"), [
            {"book_id": 1, "title": "1984", "author": "Orwell", "year": 1949},
            {"book_id": 2, "title": "Animal Farm", "author": "Orwell", "year": 1945},
            {"book_id": 3, "title": "Brave New World", "author": "Huxley", "year": 1932},
        ])
        records = table.select_records(author="Orwell")
        self.assertEqual(len(records), 2)

    def test_select_with_multiple_filters(self):
        table = Table(("book_id", "title", "author", "year"), [
            {"book_id": 1, "title": "1984", "author": "Orwell", "year": 1949},
            {"book_id": 2, "title": "Animal Farm", "author": "Orwell", "year": 1945},
        ])
        records = table.select_records(author="Orwell", year=1949)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["title"], "1984")

    def test_select_unknown_filter_column(self):
        table = Table(("book_id", "title", "author", "year"))
        with self.assertRaises(UnknownColumnError):
            table.select_records(genre="fiction")

    def test_select_no_matches(self):
        table = Table(("book_id", "title", "author", "year"), [
            {"book_id": 1, "title": "1984", "author": "Orwell", "year": 1949}
        ])
        records = table.select_records(author="Unknown")
        self.assertEqual(len(records), 0)


class TestTableUpdate(unittest.TestCase):
    def setUp(self):
        self.table = Table(("book_id", "title", "author", "year"), [
            {"book_id": 1, "title": "1984", "author": "Orwell", "year": 1949},
            {"book_id": 2, "title": "Animal Farm", "author": "Orwell", "year": 1945},
        ])

    def test_update_record_found(self):
        result = self.table.update_record("book_id", 1, {"title": "Nineteen Eighty-Four"})
        self.assertTrue(result)
        self.assertEqual(self.table.records[0]["title"], "Nineteen Eighty-Four")

    def test_update_record_not_found(self):
        result = self.table.update_record("book_id", 999, {"title": "X"})
        self.assertFalse(result)

    def test_update_unknown_key_field(self):
        with self.assertRaises(UnknownColumnError):
            self.table.update_record("genre", 1, {"title": "X"})

    def test_update_unknown_field_in_updates(self):
        with self.assertRaises(UnknownColumnError):
            self.table.update_record("book_id", 1, {"genre": "fiction"})

    def test_update_multiple_fields(self):
        self.table.update_record("book_id", 1, {"title": "X", "year": 1950})
        self.assertEqual(self.table.records[0]["title"], "X")
        self.assertEqual(self.table.records[0]["year"], 1950)

    def test_update_preserves_other_fields(self):
        self.table.update_record("book_id", 1, {"title": "X"})
        self.assertEqual(self.table.records[0]["author"], "Orwell")
        self.assertEqual(self.table.records[0]["year"], 1949)


class TestTableDelete(unittest.TestCase):
    def setUp(self):
        self.table = Table(("book_id", "title", "author", "year"), [
            {"book_id": 1, "title": "1984", "author": "Orwell", "year": 1949},
            {"book_id": 2, "title": "Animal Farm", "author": "Orwell", "year": 1945},
            {"book_id": 3, "title": "Brave New World", "author": "Huxley", "year": 1932},
        ])

    def test_delete_record_found(self):
        result = self.table.delete_record("book_id", 2)
        self.assertTrue(result)
        self.assertEqual(len(self.table.records), 2)

    def test_delete_record_not_found(self):
        result = self.table.delete_record("book_id", 999)
        self.assertFalse(result)
        self.assertEqual(len(self.table.records), 3)

    def test_delete_unknown_key_field(self):
        with self.assertRaises(UnknownColumnError):
            self.table.delete_record("genre", 1)

    def test_delete_first_record(self):
        self.table.delete_record("book_id", 1)
        self.assertEqual(self.table.records[0]["book_id"], 2)

    def test_delete_last_record(self):
        self.table.delete_record("book_id", 3)
        self.assertEqual(len(self.table.records), 2)

    def test_delete_all_records(self):
        self.table.delete_record("book_id", 1)
        self.table.delete_record("book_id", 2)
        self.table.delete_record("book_id", 3)
        self.assertEqual(len(self.table.records), 0)


class TestTableIndexes(unittest.TestCase):
    def setUp(self):
        self.table = Table(("book_id", "title", "author", "year"), [
            {"book_id": 1, "title": "1984", "author": "Orwell", "year": 1949},
            {"book_id": 2, "title": "Animal Farm", "author": "Orwell", "year": 1945},
            {"book_id": 3, "title": "Brave New World", "author": "Huxley", "year": 1932},
        ])

    def test_has_index_initially_false(self):
        self.assertFalse(self.table.has_index("author"))

    def test_create_index(self):
        self.table.create_index("author")
        self.assertTrue(self.table.has_index("author"))

    def test_create_index_twice(self):
        self.table.create_index("author")
        self.table.create_index("author")
        self.assertTrue(self.table.has_index("author"))

    def test_create_index_unknown_field(self):
        with self.assertRaises(UnknownColumnError):
            self.table.create_index("genre")

    def test_select_with_index_single_match(self):
        self.table.create_index("author")
        records = self.table.select_records(author="Huxley")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["title"], "Brave New World")

    def test_select_with_index_multiple_matches(self):
        self.table.create_index("author")
        records = self.table.select_records(author="Orwell")
        self.assertEqual(len(records), 2)

    def test_select_with_index_no_match(self):
        self.table.create_index("author")
        records = self.table.select_records(author="Unknown")
        self.assertEqual(len(records), 0)

    def test_select_without_index_still_works(self):
        records = self.table.select_records(author="Orwell")
        self.assertEqual(len(records), 2)

    def test_index_after_insert(self):
        self.table.create_index("author")
        self.table.insert_record({"book_id": 4, "title": "Homage to Catalonia", "author": "Orwell", "year": 1938})
        records = self.table.select_records(author="Orwell")
        self.assertEqual(len(records), 3)

    def test_index_after_update_same_value(self):
        self.table.create_index("author")
        self.table.update_record("book_id", 1, {"title": "X"})
        records = self.table.select_records(author="Orwell")
        self.assertEqual(len(records), 2)

    def test_index_after_update_changed_value(self):
        self.table.create_index("author")
        self.table.update_record("book_id", 2, {"author": "Huxley"})
        records = self.table.select_records(author="Huxley")
        self.assertEqual(len(records), 2)
        records = self.table.select_records(author="Orwell")
        self.assertEqual(len(records), 1)

    def test_index_after_delete(self):
        self.table.create_index("author")
        self.table.delete_record("book_id", 1)
        records = self.table.select_records(author="Orwell")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["title"], "Animal Farm")

    def test_multiple_indexes(self):
        self.table.create_index("author")
        self.table.create_index("year")
        records = self.table.select_records(author="Orwell", year=1949)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["title"], "1984")

    def test_update_indexed_field(self):
        self.table.create_index("year")
        self.table.update_record("book_id", 1, {"year": 1950})
        records = self.table.select_records(year=1950)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["book_id"], 1)

    def test_delete_all_records_with_index(self):
        self.table.create_index("author")
        self.table.delete_record("book_id", 1)
        self.table.delete_record("book_id", 2)
        self.table.delete_record("book_id", 3)
        records = self.table.select_records()
        self.assertEqual(len(records), 0)

    def test_index_on_empty_table(self):
        table = Table(("book_id", "title"))
        table.create_index("title")
        records = table.select_records(title="X")
        self.assertEqual(len(records), 0)

    def test_insert_into_indexed_empty_table(self):
        table = Table(("book_id", "title"))
        table.create_index("title")
        table.insert_record({"book_id": 1, "title": "Book1"})
        records = table.select_records(title="Book1")
        self.assertEqual(len(records), 1)


class TestTableIndexesComplex(unittest.TestCase):
    def test_index_with_none_values(self):
        table = Table(("book_id", "title", "author"), [
            {"book_id": 1, "title": "1984", "author": "Orwell"},
            {"book_id": 2, "title": "Book2", "author": None},
        ])
        table.create_index("author")
        records = table.select_records(author=None)
        self.assertEqual(len(records), 1)

    def test_update_to_none_with_index(self):
        table = Table(("book_id", "title", "author"), [
            {"book_id": 1, "title": "1984", "author": "Orwell"},
        ])
        table.create_index("author")
        table.update_record("book_id", 1, {"author": None})
        records = table.select_records(author=None)
        self.assertEqual(len(records), 1)

    def test_complex_filter_with_index(self):
        table = Table(("book_id", "title", "author", "year"), [
            {"book_id": i, "title": f"Book{i}", "author": f"Author{i%3}", "year": 2000+i}
            for i in range(10)
        ])
        table.create_index("author")
        records = table.select_records(author="Author0", year=2000)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["book_id"], 0)