# tests/test_tui.py
import unittest
from unittest.mock import patch, MagicMock

from src.db.tui import BookUI
from src.db.backend.errors import (
    DuplicateIDError,
    InvalidYearError,
    EmptyFieldError,
    RecordNotFoundError,
)


class TestBookUI(unittest.TestCase):
    def setUp(self):
        self.ui = BookUI()

    def test_print_menu(self):
        with patch('builtins.print') as mock_print:
            self.ui._print_menu()
            self.assertTrue(mock_print.called)

    def test_read_int_valid(self):
        with patch('builtins.input', return_value='42'):
            result = self.ui._read_int("Enter: ")
            self.assertEqual(result, 42)

    def test_read_int_invalid_then_valid(self):
        with patch('builtins.input', side_effect=['abc', '42']):
            result = self.ui._read_int("Enter: ")
            self.assertEqual(result, 42)

    def test_read_str_valid(self):
        with patch('builtins.input', return_value='test'):
            result = self.ui._read_str("Enter: ")
            self.assertEqual(result, 'test')

    def test_read_str_empty_not_allowed(self):
        with patch('builtins.input', side_effect=['', 'test']):
            result = self.ui._read_str("Enter: ")
            self.assertEqual(result, 'test')

    def test_read_str_empty_allowed(self):
        with patch('builtins.input', return_value=''):
            result = self.ui._read_str("Enter: ", allow_empty=True)
            self.assertEqual(result, '')

    def test_add_book_success(self):
        with patch('builtins.input', side_effect=['1', '1984', 'Orwell', '1949']):
            with patch('builtins.print'):
                self.ui._add_book()
                books = self.ui.table.select_record()
                self.assertEqual(len(books), 1)

    def test_add_book_duplicate_id(self):
        self.ui.table.create_record(1, "1984", "Orwell", 1949)
        with patch('builtins.input', side_effect=['1', 'Book', 'Author', '2000']):
            with patch('builtins.print'):
                self.ui._add_book()
                books = self.ui.table.select_record()
                self.assertEqual(len(books), 1)

    def test_add_book_invalid_year(self):
        with patch('builtins.input', side_effect=['1', 'Book', 'Author', '-1']):
            with patch('builtins.print'):
                self.ui._add_book()
                books = self.ui.table.select_record()
                self.assertEqual(len(books), 0)

    def test_show_all_books_empty(self):
        with patch('builtins.print') as mock_print:
            self.ui._show_all_books()
            mock_print.assert_called()

    def test_show_all_books_with_records(self):
        self.ui.table.create_record(1, "1984", "Orwell", 1949)
        with patch('builtins.print'):
            self.ui._show_all_books()

    def test_find_books_by_filter_no_filters(self):
        self.ui.table.create_record(1, "1984", "Orwell", 1949)
        with patch('builtins.input', return_value=''):
            with patch('builtins.print'):
                self.ui._find_books_by_filter()

    def test_find_books_by_filter_with_results(self):
        self.ui.table.create_record(1, "1984", "Orwell", 1949)
        with patch('builtins.input', side_effect=['', '', 'Orwell', '']):
            with patch('builtins.print'):
                self.ui._find_books_by_filter()

    def test_find_books_by_filter_no_results(self):
        with patch('builtins.input', side_effect=['', '', 'Unknown', '']):
            with patch('builtins.print'):
                self.ui._find_books_by_filter()

    def test_find_books_invalid_id_and_year(self):
        with patch('builtins.input', side_effect=['abc', '', '', 'xyz']):
            with patch('builtins.print'):
                self.ui._find_books_by_filter()

    def test_update_book_success(self):
        self.ui.table.create_record(1, "1984", "Orwell", 1949)
        with patch('builtins.input', side_effect=['1', 'New Title', '', '']):
            with patch('builtins.print'):
                self.ui._update_book()
                books = self.ui.table.select_record(book_id=1)
                self.assertEqual(books[0][1], "New Title")

    def test_update_book_not_found(self):
        with patch('builtins.input', side_effect=['999', '', '', '']):
            with patch('builtins.print'):
                self.ui._update_book()

    def test_update_book_no_fields_to_update(self):
        self.ui.table.create_record(1, "1984", "Orwell", 1949)
        with patch('builtins.input', side_effect=['1', '', '', '']):
            with patch('builtins.print'):
                self.ui._update_book()

    def test_update_book_invalid_year(self):
        self.ui.table.create_record(1, "1984", "Orwell", 1949)
        with patch('builtins.input', side_effect=['1', '', '', 'abc']):
            with patch('builtins.print'):
                self.ui._update_book()

    def test_delete_book_success(self):
        self.ui.table.create_record(1, "1984", "Orwell", 1949)
        with patch('builtins.input', return_value='1'):
            with patch('builtins.print'):
                self.ui._delete_book()
                books = self.ui.table.select_record()
                self.assertEqual(len(books), 0)

    def test_delete_book_not_found(self):
        with patch('builtins.input', return_value='999'):
            with patch('builtins.print'):
                self.ui._delete_book()

    def test_sort_books_by_id(self):
        self.ui.table.create_record(2, "Animal Farm", "Orwell", 1945)
        self.ui.table.create_record(1, "1984", "Orwell", 1949)
        with patch('builtins.input', side_effect=['1', 'n']):
            with patch('builtins.print'):
                self.ui._sort_books()

    def test_sort_books_by_title_descending(self):
        self.ui.table.create_record(1, "1984", "Orwell", 1949)
        self.ui.table.create_record(2, "Animal Farm", "Orwell", 1945)
        with patch('builtins.input', side_effect=['2', 'y']):
            with patch('builtins.print'):
                self.ui._sort_books()

    def test_sort_books_invalid_choice(self):
        with patch('builtins.input', return_value='9'):
            with patch('builtins.print'):
                self.ui._sort_books()

    def test_run_menu_add_book(self):
        self.ui._add_book = MagicMock()
        with patch('builtins.input', side_effect=['1', '0']):
            with patch('builtins.print'):
                self.ui.run()
                self.ui._add_book.assert_called_once()

    def test_run_menu_show_all_books(self):
        self.ui._show_all_books = MagicMock()
        with patch('builtins.input', side_effect=['2', '0']):
            with patch('builtins.print'):
                self.ui.run()
                self.ui._show_all_books.assert_called_once()

    def test_run_menu_find_books(self):
        self.ui._find_books_by_filter = MagicMock()
        with patch('builtins.input', side_effect=['3', '0']):
            with patch('builtins.print'):
                self.ui.run()
                self.ui._find_books_by_filter.assert_called_once()

    def test_run_menu_update_book(self):
        self.ui._update_book = MagicMock()
        with patch('builtins.input', side_effect=['4', '0']):
            with patch('builtins.print'):
                self.ui.run()
                self.ui._update_book.assert_called_once()

    def test_run_menu_delete_book(self):
        self.ui._delete_book = MagicMock()
        with patch('builtins.input', side_effect=['5', '0']):
            with patch('builtins.print'):
                self.ui.run()
                self.ui._delete_book.assert_called_once()

    def test_run_menu_sort_books(self):
        self.ui._sort_books = MagicMock()
        with patch('builtins.input', side_effect=['6', '0']):
            with patch('builtins.print'):
                self.ui.run()
                self.ui._sort_books.assert_called_once()

    def test_run_menu_exit(self):
        with patch('builtins.input', return_value='0'):
            with patch('builtins.print'):
                self.ui.run()

    def test_run_menu_invalid_choice(self):
        with patch('builtins.input', side_effect=['9', '0']):
            with patch('builtins.print'):
                self.ui.run()


if __name__ == "__main__":
    unittest.main()