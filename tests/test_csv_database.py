# tests/test_csv_database.py
import tempfile
import unittest
import os

from src.db.backend.csv_file import CsvDatabase
from src.db.backend.errors import (
    TableNotFoundError,
    TableAlreadyExistsError,
    MissingColumnError,
    UnknownColumnError,
    InvalidStorageDataError,
)


class TestCsvDatabaseBasic(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db = CsvDatabase(self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_create_table(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        self.assertTrue(self.db._table_exists("books"))

    def test_create_duplicate_table(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("books", ("book_id", "title", "author", "year"))

    def test_insert_record(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        self.db.insert_record("books", {"book_id": 1, "title": "1984", "author": "Orwell", "year": 1949})
        records = self.db.select_records("books")
        self.assertEqual(len(records), 1)

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

    def test_select_from_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("books")


class TestCsvDatabasePersistence(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_data_persists_between_instances(self):
        db1 = CsvDatabase(self.temp_dir)
        db1.create_table("books", ("book_id", "title", "author", "year"))
        db1.insert_record("books", {"book_id": 1, "title": "1984", "author": "Orwell", "year": 1949})

        db2 = CsvDatabase(self.temp_dir)
        records = db2.select_records("books")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["title"], "1984")

    def test_multiple_records_persist(self):
        db1 = CsvDatabase(self.temp_dir)
        db1.create_table("books", ("book_id", "title", "author", "year"))
        for i in range(5):
            db1.insert_record("books", {"book_id": i, "title": f"Book{i}", "author": f"Author{i}", "year": 2000+i})

        db2 = CsvDatabase(self.temp_dir)
        records = db2.select_records("books")
        self.assertEqual(len(records), 5)


class TestCsvDatabaseFilters(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db = CsvDatabase(self.temp_dir)
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        self.db.insert_record("books", {"book_id": 1, "title": "1984", "author": "Orwell", "year": 1949})
        self.db.insert_record("books", {"book_id": 2, "title": "Animal Farm", "author": "Orwell", "year": 1945})
        self.db.insert_record("books", {"book_id": 3, "title": "Brave New World", "author": "Huxley", "year": 1932})

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_select_all(self):
        records = self.db.select_records("books")
        self.assertEqual(len(records), 3)

    def test_select_by_author(self):
        records = self.db.select_records("books", author="Orwell")
        self.assertEqual(len(records), 2)

    def test_select_by_year(self):
        records = self.db.select_records("books", year=1949)
        self.assertEqual(len(records), 1)

    def test_select_by_multiple_filters(self):
        records = self.db.select_records("books", author="Orwell", year=1949)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["title"], "1984")

    def test_select_no_matches(self):
        records = self.db.select_records("books", author="Unknown")
        self.assertEqual(len(records), 0)

    def test_select_unknown_filter_column(self):
        with self.assertRaises(UnknownColumnError):
            self.db.select_records("books", genre="fiction")


class TestCsvDatabaseUpdateDelete(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db = CsvDatabase(self.temp_dir)
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

    def test_update_record_not_found(self):
        result = self.db.update_record("books", "book_id", 999, {"title": "X"})
        self.assertFalse(result)

    def test_update_persists(self):
        self.db.update_record("books", "book_id", 1, {"title": "X"})
        db2 = CsvDatabase(self.temp_dir)
        records = db2.select_records("books", book_id=1)
        self.assertEqual(records[0]["title"], "X")

    def test_delete_record(self):
        result = self.db.delete_record("books", "book_id", 1)
        self.assertTrue(result)
        records = self.db.select_records("books")
        self.assertEqual(len(records), 1)

    def test_delete_record_not_found(self):
        result = self.db.delete_record("books", "book_id", 999)
        self.assertFalse(result)

    def test_delete_persists(self):
        self.db.delete_record("books", "book_id", 1)
        db2 = CsvDatabase(self.temp_dir)
        records = db2.select_records("books")
        self.assertEqual(len(records), 1)


class TestCsvDatabaseErrors(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db = CsvDatabase(self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_empty_csv_file(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        table_path = self.db._get_table_path("books")
        with table_path.open("w", encoding="utf-8") as f:
            f.write("")
        with self.assertRaises(InvalidStorageDataError):
            self.db.select_records("books")

    def test_wrong_column_count(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        table_path = self.db._get_table_path("books")
        with table_path.open("w", encoding="utf-8") as f:
            f.write("book_id,title,author,year\n1,1984,Orwell\n")
        with self.assertRaises(InvalidStorageDataError):
            self.db.select_records("books")

    def test_missing_table_file(self):
        with self.assertRaises(TableNotFoundError):
            self.db._load_table("nonexistent")


class TestCsvDatabaseEdgeCases(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db = CsvDatabase(self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_empty_table(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        records = self.db.select_records("books")
        self.assertEqual(len(records), 0)

    def test_special_characters_in_data(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        self.db.insert_record("books", {"book_id": 1, "title": "Book, with \"quotes\"", "author": "O'Brien", "year": 1949})
        records = self.db.select_records("books")
        self.assertEqual(records[0]["title"], "Book, with \"quotes\"")

    def test_unicode_characters(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        self.db.insert_record("books", {"book_id": 1, "title": "Книга", "author": "Автор", "year": 2000})
        records = self.db.select_records("books")
        self.assertEqual(records[0]["title"], "Книга")

    def test_large_number_of_records(self):
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        for i in range(100):
            self.db.insert_record("books", {"book_id": i, "title": f"Book{i}", "author": f"Author{i}", "year": 2000+i})
        records = self.db.select_records("books")
        self.assertEqual(len(records), 100)


class TestCsvDatabaseDirectory(unittest.TestCase):
    def test_custom_directory_created(self):
        temp_dir = tempfile.mkdtemp()
        custom_dir = os.path.join(temp_dir, "custom_data")
        db = CsvDatabase(custom_dir)
        db.create_table("books", ("book_id", "title"))
        self.assertTrue(os.path.exists(custom_dir))
        import shutil
        shutil.rmtree(temp_dir)


class TestCsvDatabaseIndexes(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db = CsvDatabase(self.temp_dir)
        self.db.create_table("books", ("book_id", "title", "author", "year"))
        self.db.insert_record("books", {"book_id": 1, "title": "1984", "author": "Orwell", "year": 1949})
        self.db.insert_record("books", {"book_id": 2, "title": "Animal Farm", "author": "Orwell", "year": 1945})
        self.db.insert_record("books", {"book_id": 3, "title": "Brave New World", "author": "Huxley", "year": 1932})

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_create_index(self):
        self.db.create_index("books", "author")
        records = self.db.select_records("books", author="Orwell")
        self.assertEqual(len(records), 2)

    def test_index_after_insert(self):
        self.db.create_index("books", "author")
        self.db.insert_record("books", {"book_id": 4, "title": "Homage to Catalonia", "author": "Orwell", "year": 1938})
        records = self.db.select_records("books", author="Orwell")
        self.assertEqual(len(records), 3)

    def test_index_after_update(self):
        self.db.create_index("books", "author")
        self.db.update_record("books", "book_id", 3, {"author": "Orwell"})
        records = self.db.select_records("books", author="Orwell")
        self.assertEqual(len(records), 3)

    def test_index_after_delete(self):
        self.db.create_index("books", "author")
        self.db.delete_record("books", "book_id", 1)
        records = self.db.select_records("books", author="Orwell")
        self.assertEqual(len(records), 1)