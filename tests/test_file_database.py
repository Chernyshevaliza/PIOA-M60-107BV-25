# tests/test_file_database_extended.py
import tempfile
import unittest
import json
import os

from src.db.backend.file import FileDatabase
from src.db.backend.errors import (
    TableNotFoundError,
    TableAlreadyExistsError,
    MissingColumnError,
    UnknownColumnError,
    InvalidStorageDataError,
)


class TestFileDatabaseErrors(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db = FileDatabase(self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_invalid_json_structure_missing_columns(self):
        self.db.create_table("books", ("book_id", "title"))
        table_path = self.db._get_table_path("books")
        with table_path.open("w", encoding="utf-8") as f:
            json.dump({"records": []}, f)
        with self.assertRaises(InvalidStorageDataError):
            self.db.select_records("books")

    def test_invalid_json_structure_missing_records(self):
        self.db.create_table("books", ("book_id", "title"))
        table_path = self.db._get_table_path("books")
        with table_path.open("w", encoding="utf-8") as f:
            json.dump({"columns": ["book_id", "title"]}, f)
        with self.assertRaises(InvalidStorageDataError):
            self.db.select_records("books")

    def test_invalid_columns_type(self):
        self.db.create_table("books", ("book_id", "title"))
        table_path = self.db._get_table_path("books")
        with table_path.open("w", encoding="utf-8") as f:
            json.dump({"columns": "not_a_list", "records": []}, f)
        with self.assertRaises(InvalidStorageDataError):
            self.db.select_records("books")

    def test_invalid_records_type(self):
        self.db.create_table("books", ("book_id", "title"))
        table_path = self.db._get_table_path("books")
        with table_path.open("w", encoding="utf-8") as f:
            json.dump({"columns": ["book_id", "title"], "records": "not_a_list"}, f)
        with self.assertRaises(InvalidStorageDataError):
            self.db.select_records("books")

    def test_record_not_dict(self):
        self.db.create_table("books", ("book_id", "title"))
        table_path = self.db._get_table_path("books")
        with table_path.open("w", encoding="utf-8") as f:
            json.dump({"columns": ["book_id", "title"], "records": ["not_a_dict"]}, f)
        with self.assertRaises(InvalidStorageDataError):
            self.db.select_records("books")

    def test_invalid_json_syntax(self):
        self.db.create_table("books", ("book_id", "title"))
        table_path = self.db._get_table_path("books")
        with table_path.open("w", encoding="utf-8") as f:
            f.write("{invalid json")
        with self.assertRaises(InvalidStorageDataError):
            self.db.select_records("books")


class TestFileDatabaseUpdateDelete(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db = FileDatabase(self.temp_dir)
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        self.db.insert_record("books", {"book_id": 1, "title": "1984", "author": "Orwell", "year": 1949})
        self.db.insert_record("books", {"book_id": 2, "title": "Animal Farm", "author": "Orwell", "year": 1945})

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_update_record(self):
        result = self.db.update_record("books", "book_id", 1, {"title": "Nineteen Eighty-Four"})
        self.assertTrue(result)
        records = self.db.select_records("books", book_id=1)
        self.assertEqual(records[0]["title"], "Nineteen Eighty-Four")

    def test_update_not_found(self):
        result = self.db.update_record("books", "book_id", 999, {"title": "X"})
        self.assertFalse(result)

    def test_update_persists(self):
        self.db.update_record("books", "book_id", 1, {"title": "X"})
        db2 = FileDatabase(self.temp_dir)
        records = db2.select_records("books", book_id=1)
        self.assertEqual(records[0]["title"], "X")

    def test_delete_record(self):
        result = self.db.delete_record("books", "book_id", 1)
        self.assertTrue(result)
        records = self.db.select_records("books")
        self.assertEqual(len(records), 1)

    def test_delete_not_found(self):
        result = self.db.delete_record("books", "book_id", 999)
        self.assertFalse(result)

    def test_delete_persists(self):
        self.db.delete_record("books", "book_id", 1)
        db2 = FileDatabase(self.temp_dir)
        records = db2.select_records("books")
        self.assertEqual(len(records), 1)


class TestFileDatabaseLargeData(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db = FileDatabase(self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_many_records(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        for i in range(100):
            self.db.insert_record("books", {"book_id": i, "title": f"Book{i}", "author": f"Author{i}", "year": 2000+i})
        records = self.db.select_records("books")
        self.assertEqual(len(records), 100)

    def test_filter_on_many_records(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        for i in range(100):
            self.db.insert_record("books", {"book_id": i, "title": f"Book{i}", "author": f"Author{i%5}", "year": 2000+i})
        records = self.db.select_records("books", author="Author0")
        self.assertEqual(len(records), 20)