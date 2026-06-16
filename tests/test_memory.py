import unittest
from src.db.backend.memory import BookTable
from src.db.backend.errors import InvalidYearError, DuplicateIDError, EmptyFieldError, RecordNotFoundError


class TestBookTable(unittest.TestCase):
    def setUp(self) -> None:
        self.table = BookTable()
        self.assertIsInstance(self.table, BookTable)

    def test_create_record(self) -> None:
        cases = [
            (1, "1984", "George Orwell", 1949),
            (2, "Brave New World", "Aldous Huxley", 1932),
            (3, "Fahrenheit 451", "Ray Bradbury", 1953),
        ]

        for test_data in cases:
            with self.subTest(test_data=test_data):
                record = self.table.create_record(*test_data)
                self.assertEqual(record, test_data)

    def test_create_record_negative_year(self) -> None:
        cases = [
            (1, "1984", "George Orwell", -1),
            (2, "Brave New World", "Aldous Huxley", -5),
        ]

        error_message = "Год не может быть отрицательным."

        for test_data in cases:
            with self.subTest(test_data=test_data):
                with self.assertRaises(InvalidYearError) as context:
                    self.table.create_record(*test_data)
                self.assertEqual(str(context.exception), error_message)

    def test_create_record_duplicate_id(self) -> None:
        test_data_1 = (1, "1984", "George Orwell", 1949)
        test_data_2 = (1, "Animal Farm", "George Orwell", 1945)
        error_message = "Запись с id=1 уже существует."

        self.table.create_record(*test_data_1)

        with self.assertRaises(DuplicateIDError) as context:
            self.table.create_record(*test_data_2)

        self.assertEqual(str(context.exception), error_message)

    def test_create_record_empty_fields(self) -> None:
        with self.assertRaises(EmptyFieldError):
            self.table.create_record(1, "", "Author", 2000)

        with self.assertRaises(EmptyFieldError):
            self.table.create_record(2, "Title", "", 2000)

    def test_select_record_no_filters(self) -> None:
        test_data = (1, "1984", "George Orwell", 1949)
        self.table.create_record(*test_data)
        result = self.table.select_record()
        self.assertEqual(result, [test_data])

    def test_select_record_by_id(self) -> None:
        test_data = (1, "1984", "George Orwell", 1949)
        self.table.create_record(*test_data)
        result = self.table.select_record(book_id=1)
        self.assertEqual(result, [test_data])

    def test_update_record(self) -> None:
        self.table.create_record(1, "1984", "George Orwell", 1949)
        updated = self.table.update_record(1, title="Nineteen Eighty-Four")
        self.assertEqual(updated, (1, "Nineteen Eighty-Four", "George Orwell", 1949))

    def test_delete_record(self) -> None:
        self.table.create_record(1, "1984", "George Orwell", 1949)
        self.table.delete_record(1)
        result = self.table.get_all()
        self.assertEqual(result, [])

    def test_get_all(self) -> None:
        test_data = (1, "1984", "George Orwell", 1949)
        self.table.create_record(*test_data)
        result = self.table.get_all()
        self.assertEqual(result, [test_data])


if __name__ == "__main__":
    unittest.main()