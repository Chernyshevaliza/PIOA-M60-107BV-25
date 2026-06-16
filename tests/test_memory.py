import unittest
from src.db.backend.memory import BookTable
from src.db.backend.errors import InvalidYearError, DuplicateIDError


class TestMemory(unittest.TestCase):
    def setUp(self):
        self.book_table = BookTable()
        self.assertIsInstance(self.book_table, BookTable)

    def test_create_record(self):
        cases = [
            (1, "1984", "George Orwell", 1949),
            (2, "Brave New World", "Aldous Huxley", 1932),
            (3, "Fahrenheit 451", "Ray Bradbury", 1953),
            (4, "The Catcher in the Rye", "J.D. Salinger", 1951),
            (5, "To Kill a Mockingbird", "Harper Lee", 1960),
            (6, "The Great Gatsby", "F. Scott Fitzgerald", 1925),
            (7, "Moby Dick", "Herman Melville", 1851),
            (8, "Pride and Prejudice", "Jane Austen", 1813),
            (9, "The Hobbit", "J.R.R. Tolkien", 1937),
            (10, "The Lord of the Rings", "J.R.R. Tolkien", 1954),
            (11, "The Shining", "Stephen King", 1977),
            (12, "It", "Stephen King", 1986),
        ]

        for test_data in cases:
            with self.subTest(test_data=test_data):
                record = self.book_table.create_record(*test_data)
                self.assertEqual(record, test_data)

    def test_create_record_negative_year(self):
        cases = [
            (1, "1984", "George Orwell", -1),
            (2, "Brave New World", "Aldous Huxley", -5),
            (3, "Fahrenheit 451", "Ray Bradbury", -10),
        ]
        error_message = "Год не может быть отрицательным."

        for test_data in cases:
            with self.subTest(test_data=test_data):
                with self.assertRaises(InvalidYearError) as context:
                    self.book_table.create_record(*test_data)

        self.assertEqual(str(context.exception), error_message)

    def test_create_record_duplicate_id(self):
        test_data_1 = (1, "1984", "George Orwell", 1949)
        test_data_2 = (1, "Animal Farm", "George Orwell", 1945)
        error_message = "Запись с id=1 уже существует."

        self.book_table.create_record(*test_data_1)

        with self.assertRaises(DuplicateIDError) as context:
            self.book_table.create_record(*test_data_2)

        self.assertEqual(str(context.exception), error_message)

    def test_select_record(self):
        test_datas = [
            (1, "1984", "George Orwell", 1949),
            (2, "Brave New World", "Aldous Huxley", 1932),
            (3, "Fahrenheit 451", "Ray Bradbury", 1953),
            (4, "The Catcher in the Rye", "J.D. Salinger", 1951),
            (5, "To Kill a Mockingbird", "Harper Lee", 1960),
            (6, "The Great Gatsby", "F. Scott Fitzgerald", 1925),
            (7, "Moby Dick", "Herman Melville", 1851),
            (8, "Pride and Prejudice", "Jane Austen", 1813),
            (9, "The Hobbit", "J.R.R. Tolkien", 1937),
            (10, "The Lord of the Rings", "J.R.R. Tolkien", 1954),
        ]

        for test_data in test_datas:
            self.book_table.create_record(*test_data)

        cases = [
            {
                "name": "Выбор без фильтров",
                "filters": {},
                "expected": test_datas,
            },
            {
                "name": "Фильтр по ID",
                "filters": {"book_id": 1},
                "expected": [test_datas[0]],
            },
            {
                "name": "Фильтр по названию",
                "filters": {"title": "1984"},
                "expected": [test_datas[0]],
            },
            {
                "name": "Фильтр по автору",
                "filters": {"author": "J.R.R. Tolkien"},
                "expected": [test_datas[8], test_datas[9]],
            },
            {
                "name": "Фильтр по году",
                "filters": {"year": 1953},
                "expected": [test_datas[2]],
            },
            {
                "name": "Фильтр по автору и году",
                "filters": {"author": "George Orwell", "year": 1949},
                "expected": [test_datas[0]],
            },
        ]

        for case in cases:
            with self.subTest(
                case=case["name"], filters=case["filters"], expected=case["expected"]
            ):
                records = self.book_table.select_record(**case["filters"])
                self.assertEqual(records, case["expected"])

    def test_update_record(self):
        self.book_table.create_record(1, "1984", "George Orwell", 1949)
        updated = self.book_table.update_record(1, title="Nineteen Eighty-Four")
        self.assertEqual(updated, (1, "Nineteen Eighty-Four", "George Orwell", 1949))

    def test_delete_record(self):
        self.book_table.create_record(1, "1984", "George Orwell", 1949)
        self.book_table.delete_record(1)
        result = self.book_table.select_record()
        self.assertEqual(result, [])

    def test_sort_records(self):
        test_datas = [
            (2, "Brave New World", "Aldous Huxley", 1932),
            (1, "1984", "George Orwell", 1949),
            (3, "Fahrenheit 451", "Ray Bradbury", 1953),
        ]
        for data in test_datas:
            self.book_table.create_record(*data)

        sorted_by_id = self.book_table.sort_records("book_id")
        self.assertEqual(sorted_by_id, [
            (1, "1984", "George Orwell", 1949),
            (2, "Brave New World", "Aldous Huxley", 1932),
            (3, "Fahrenheit 451", "Ray Bradbury", 1953),
        ])

        sorted_by_title_desc = self.book_table.sort_records("title", reverse=True)
        self.assertEqual(sorted_by_title_desc, [
            (3, "Fahrenheit 451", "Ray Bradbury", 1953),
            (2, "Brave New World", "Aldous Huxley", 1932),
            (1, "1984", "George Orwell", 1949),
        ])

        sorted_by_author = self.book_table.sort_records("author")
        self.assertEqual(sorted_by_author, [
            (2, "Brave New World", "Aldous Huxley", 1932),
            (1, "1984", "George Orwell", 1949),
            (3, "Fahrenheit 451", "Ray Bradbury", 1953),
        ])

        sorted_by_year_desc = self.book_table.sort_records("year", reverse=True)
        self.assertEqual(sorted_by_year_desc, [
            (3, "Fahrenheit 451", "Ray Bradbury", 1953),
            (1, "1984", "George Orwell", 1949),
            (2, "Brave New World", "Aldous Huxley", 1932),
        ])

        with self.assertRaises(ValueError):
            self.book_table.sort_records("invalid_field")


if __name__ == "__main__":
    unittest.main()