# tests/test_tui.py
import unittest
from unittest.mock import patch, MagicMock, PropertyMock
import sys
from io import StringIO


class TestBookUI(unittest.TestCase):
    
    def test_ensure_books_table_creates_table(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        ui.database.create_table.side_effect = Exception("Table exists")
        try:
            ui._ensure_books_table()
        except:
            pass
        ui.database.create_table.assert_called_once()

    def test_print_menu(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        with patch('builtins.print') as mock_print:
            ui._print_menu()
            self.assertTrue(mock_print.called)

    def test_read_int_valid(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        with patch('builtins.input', return_value='42'):
            result = ui._read_int("Enter: ")
            self.assertEqual(result, 42)

    def test_read_int_invalid_then_valid(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        with patch('builtins.input', side_effect=['abc', '42']):
            result = ui._read_int("Enter: ")
            self.assertEqual(result, 42)

    def test_read_str_valid(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        with patch('builtins.input', return_value='test'):
            result = ui._read_str("Enter: ")
            self.assertEqual(result, 'test')

    def test_read_str_empty_not_allowed(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        with patch('builtins.input', side_effect=['', 'test']):
            result = ui._read_str("Enter: ")
            self.assertEqual(result, 'test')

    def test_read_str_empty_allowed(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        with patch('builtins.input', return_value=''):
            result = ui._read_str("Enter: ", allow_empty=True)
            self.assertEqual(result, '')

    def test_add_book_success(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        with patch('builtins.input', side_effect=['1', '1984', 'Orwell', '1949']):
            with patch('builtins.print'):
                ui._add_book()
                ui.database.insert_record.assert_called_once()

    def test_add_book_missing_column_error(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        from src.db.backend.errors import MissingColumnError
        ui.database.insert_record.side_effect = MissingColumnError("Missing column")
        with patch('builtins.input', side_effect=['1', '1984', 'Orwell', '1949']):
            with patch('builtins.print'):
                ui._add_book()

    def test_add_book_unknown_column_error(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        from src.db.backend.errors import UnknownColumnError
        ui.database.insert_record.side_effect = UnknownColumnError("Unknown column")
        with patch('builtins.input', side_effect=['1', '1984', 'Orwell', '1949']):
            with patch('builtins.print'):
                ui._add_book()

    def test_add_book_table_not_found_error(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        from src.db.backend.errors import TableNotFoundError
        ui.database.insert_record.side_effect = TableNotFoundError("Table not found")
        with patch('builtins.input', side_effect=['1', '1984', 'Orwell', '1949']):
            with patch('builtins.print'):
                ui._add_book()

    def test_show_all_books_empty(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        ui.database.select_records.return_value = []
        with patch('builtins.print') as mock_print:
            ui._show_all_books()
            mock_print.assert_called()

    def test_show_all_books_with_records(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        ui.database.select_records.return_value = [
            {"book_id": 1, "title": "1984", "author": "Orwell", "year": 1949}
        ]
        with patch('builtins.print'):
            ui._show_all_books()

    def test_show_all_books_table_not_found(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        from src.db.backend.errors import TableNotFoundError
        ui.database.select_records.side_effect = TableNotFoundError("Not found")
        with patch('builtins.print'):
            ui._show_all_books()

    def test_find_books_by_filter_no_filters(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        ui.database.select_records.return_value = []
        with patch('builtins.input', return_value=''):
            with patch('builtins.print'):
                ui._find_books_by_filter()

    def test_find_books_by_filter_with_results(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        ui.database.select_records.return_value = [
            {"book_id": 1, "title": "1984", "author": "Orwell", "year": 1949}
        ]
        with patch('builtins.input', side_effect=['', '', 'Orwell', '']):
            with patch('builtins.print'):
                ui._find_books_by_filter()

    def test_find_books_by_filter_no_results(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        ui.database.select_records.return_value = []
        with patch('builtins.input', side_effect=['', '', 'Unknown', '']):
            with patch('builtins.print'):
                ui._find_books_by_filter()

    def test_find_books_invalid_id_and_year(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        ui.database.select_records.return_value = []
        with patch('builtins.input', side_effect=['abc', '', '', 'xyz']):
            with patch('builtins.print'):
                ui._find_books_by_filter()

    def test_find_books_unknown_column_error(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        from src.db.backend.errors import UnknownColumnError
        ui.database.select_records.side_effect = UnknownColumnError("Unknown")
        with patch('builtins.input', side_effect=['1', '', '', '']):
            with patch('builtins.print'):
                ui._find_books_by_filter()

    def test_update_book_success(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        ui.database.update_record.return_value = True
        with patch('builtins.input', side_effect=['1', 'New Title', '', '']):
            with patch('builtins.print'):
                ui._update_book()
                ui.database.update_record.assert_called_once()

    def test_update_book_not_found(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        ui.database.update_record.return_value = False
        with patch('builtins.input', side_effect=['999', '', '', '']):
            with patch('builtins.print'):
                ui._update_book()

    def test_update_book_no_fields_to_update(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        with patch('builtins.input', side_effect=['1', '', '', '']):
            with patch('builtins.print'):
                ui._update_book()

    def test_update_book_invalid_year(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        ui.database.update_record.return_value = True
        with patch('builtins.input', side_effect=['1', '', '', 'abc']):
            with patch('builtins.print'):
                ui._update_book()

    def test_update_book_unknown_column_error(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        from src.db.backend.errors import UnknownColumnError
        ui.database.update_record.side_effect = UnknownColumnError("Unknown")
        with patch('builtins.input', side_effect=['1', 'Title', '', '']):
            with patch('builtins.print'):
                ui._update_book()

    def test_update_book_table_not_found_error(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        from src.db.backend.errors import TableNotFoundError
        ui.database.update_record.side_effect = TableNotFoundError("Not found")
        with patch('builtins.input', side_effect=['1', 'Title', '', '']):
            with patch('builtins.print'):
                ui._update_book()

    def test_delete_book_success(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        ui.database.delete_record.return_value = True
        with patch('builtins.input', return_value='1'):
            with patch('builtins.print'):
                ui._delete_book()
                ui.database.delete_record.assert_called_once()

    def test_delete_book_not_found(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        ui.database.delete_record.return_value = False
        with patch('builtins.input', return_value='999'):
            with patch('builtins.print'):
                ui._delete_book()

    def test_delete_book_unknown_column_error(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        from src.db.backend.errors import UnknownColumnError
        ui.database.delete_record.side_effect = UnknownColumnError("Unknown")
        with patch('builtins.input', return_value='1'):
            with patch('builtins.print'):
                ui._delete_book()

    def test_delete_book_table_not_found_error(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        from src.db.backend.errors import TableNotFoundError
        ui.database.delete_record.side_effect = TableNotFoundError("Not found")
        with patch('builtins.input', return_value='1'):
            with patch('builtins.print'):
                ui._delete_book()

    def test_create_index_success(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        with patch('builtins.input', return_value='3'):
            with patch('builtins.print'):
                ui._create_index()
                ui.database.create_index.assert_called_once_with("books", "author")

    def test_create_index_invalid_choice(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        with patch('builtins.input', return_value='9'):
            with patch('builtins.print'):
                ui._create_index()
                ui.database.create_index.assert_not_called()

    def test_create_index_unknown_column_error(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        from src.db.backend.errors import UnknownColumnError
        ui.database.create_index.side_effect = UnknownColumnError("Unknown")
        with patch('builtins.input', return_value='1'):
            with patch('builtins.print'):
                ui._create_index()

    def test_run_menu_add_book(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        ui._add_book = MagicMock()
        with patch('builtins.input', side_effect=['1', '0']):
            with patch('builtins.print'):
                ui.run()
                ui._add_book.assert_called_once()

    def test_run_menu_show_all_books(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        ui._show_all_books = MagicMock()
        with patch('builtins.input', side_effect=['2', '0']):
            with patch('builtins.print'):
                ui.run()
                ui._show_all_books.assert_called_once()

    def test_run_menu_find_books(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        ui._find_books_by_filter = MagicMock()
        with patch('builtins.input', side_effect=['3', '0']):
            with patch('builtins.print'):
                ui.run()
                ui._find_books_by_filter.assert_called_once()

    def test_run_menu_update_book(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        ui._update_book = MagicMock()
        with patch('builtins.input', side_effect=['4', '0']):
            with patch('builtins.print'):
                ui.run()
                ui._update_book.assert_called_once()

    def test_run_menu_delete_book(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        ui._delete_book = MagicMock()
        with patch('builtins.input', side_effect=['5', '0']):
            with patch('builtins.print'):
                ui.run()
                ui._delete_book.assert_called_once()

    def test_run_menu_create_index(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        ui._create_index = MagicMock()
        with patch('builtins.input', side_effect=['6', '0']):
            with patch('builtins.print'):
                ui.run()
                ui._create_index.assert_called_once()

    def test_run_menu_exit(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        with patch('builtins.input', return_value='0'):
            with patch('builtins.print'):
                ui.run()

    def test_run_menu_invalid_choice(self):
        from src.db.tui import BookUI
        ui = BookUI.__new__(BookUI)
        ui.database = MagicMock()
        with patch('builtins.input', side_effect=['9', '0']):
            with patch('builtins.print'):
                ui.run()


if __name__ == "__main__":
    unittest.main()