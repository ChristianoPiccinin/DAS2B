"""Unit tests for ETL trigger extraction functions.

Tests cover three scenarios per trigger:
1. Successful extraction with data
2. Empty source table
3. SQL error during execution
"""

import unittest
from unittest.mock import patch, MagicMock
import pyodbc


class BaseTriggerTest(unittest.TestCase):
    """Base class for trigger unit tests."""

    def setUp(self):
        """Set up mock objects for database connections and logging."""
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_connection.cursor.return_value = self.mock_cursor
        self.mock_connection.__enter__ = MagicMock(return_value=self.mock_connection)
        self.mock_connection.__exit__ = MagicMock(return_value=None)

    def _test_success(self, trigger_module, trigger_name, table_name):
        """Test successful extraction when data exists."""
        with patch.dict('os.environ', {
            'SQL_SERVER_SOURCE': 'test_server_source',
            'SQL_DATABASE_SOURCE': 'test_db_source',
            'SQL_USER_SOURCE': 'test_user_source',
            'SQL_PASSWORD_SOURCE': 'test_pass_source',
            'SQL_SERVER_TARGET': 'test_server_target',
            'SQL_DATABASE_TARGET': 'test_db_target',
            'SQL_USER_TARGET': 'test_user_target',
            'SQL_PASSWORD_TARGET': 'test_pass_target',
        }):
            with patch(f'triggers.{trigger_module}.pyodbc.connect') as mock_connect:
                with patch(f'triggers.{trigger_module}.logging') as mock_logging:
                    mock_connect.return_value = self.mock_connection
                    test_rows = [('id1', 'val1'), ('id2', 'val2')]
                    self.mock_cursor.fetchall.return_value = test_rows
                    self.mock_cursor.description = [('id',), ('val',)]

                    trigger_func = getattr(__import__(f'triggers.{trigger_module}', fromlist=[trigger_name]), trigger_name)
                    import azure.functions as func
                    timer_request = MagicMock(spec=func.TimerRequest)
                    trigger_func(timer_request)

                    # Verify DELETE was called
                    self.assertTrue(any('DELETE' in str(call_args) for call_args in self.mock_cursor.execute.call_args_list))
                    # Verify executemany was called
                    self.mock_cursor.executemany.assert_called()
                    # Verify commit was called
                    self.mock_connection.commit.assert_called()

    def _test_empty_table(self, trigger_module, trigger_name, table_name):
        """Test extraction when source table is empty."""
        with patch.dict('os.environ', {
            'SQL_SERVER_SOURCE': 'test_server_source',
            'SQL_DATABASE_SOURCE': 'test_db_source',
            'SQL_USER_SOURCE': 'test_user_source',
            'SQL_PASSWORD_SOURCE': 'test_pass_source',
            'SQL_SERVER_TARGET': 'test_server_target',
            'SQL_DATABASE_TARGET': 'test_db_target',
            'SQL_USER_TARGET': 'test_user_target',
            'SQL_PASSWORD_TARGET': 'test_pass_target',
        }):
            with patch(f'triggers.{trigger_module}.pyodbc.connect') as mock_connect:
                with patch(f'triggers.{trigger_module}.logging') as mock_logging:
                    mock_connect.return_value = self.mock_connection
                    self.mock_cursor.fetchall.return_value = []

                    trigger_func = getattr(__import__(f'triggers.{trigger_module}', fromlist=[trigger_name]), trigger_name)
                    import azure.functions as func
                    timer_request = MagicMock(spec=func.TimerRequest)
                    trigger_func(timer_request)

                    # Verify warning was logged
                    mock_logging.warning.assert_called()
                    # Verify no INSERT occurred
                    self.mock_cursor.executemany.assert_not_called()

    def _test_sql_error(self, trigger_module, trigger_name, table_name):
        """Test extraction when SQL error occurs."""
        with patch.dict('os.environ', {
            'SQL_SERVER_SOURCE': 'test_server_source',
            'SQL_DATABASE_SOURCE': 'test_db_source',
            'SQL_USER_SOURCE': 'test_user_source',
            'SQL_PASSWORD_SOURCE': 'test_pass_source',
            'SQL_SERVER_TARGET': 'test_server_target',
            'SQL_DATABASE_TARGET': 'test_db_target',
            'SQL_USER_TARGET': 'test_user_target',
            'SQL_PASSWORD_TARGET': 'test_pass_target',
        }):
            with patch(f'triggers.{trigger_module}.pyodbc.connect') as mock_connect:
                with patch(f'triggers.{trigger_module}.logging') as mock_logging:
                    mock_connect.return_value = self.mock_connection
                    self.mock_cursor.execute.side_effect = pyodbc.Error('SQL Error')

                    trigger_func = getattr(__import__(f'triggers.{trigger_module}', fromlist=[trigger_name]), trigger_name)
                    import azure.functions as func
                    timer_request = MagicMock(spec=func.TimerRequest)

                    with self.assertRaises(pyodbc.Error):
                        trigger_func(timer_request)

                    # Verify error was logged
                    mock_logging.error.assert_called()


# List of all triggers to test: (module_name, function_name, table_name)
TRIGGERS = [
    ('extract_cliente', 'extract_cliente', 'cliente'),
    ('extract_pedido', 'extract_pedido', 'pedido'),
    ('extract_entrega', 'extract_entrega', 'entrega'),
    ('extract_representante', 'extract_representante', 'representante'),
    ('extract_estoque_movimentacao', 'extract_estoque_movimentacao', 'estoque_movimentacao'),
    ('extract_estoque_saldo', 'extract_estoque_saldo', 'estoque_saldo'),
    ('extract_fornecedor', 'extract_fornecedor', 'fornecedor'),
    ('extract_titulo_receber', 'extract_titulo_receber', 'titulo_receber'),
    ('extract_transportadora', 'extract_transportadora', 'transportadora'),
    ('extract_categoria_produto', 'extract_categoria_produto', 'categoria_produto'),
    ('extract_pedido_item', 'extract_pedido_item', 'pedido_item'),
    ('extract_produto', 'extract_produto', 'produto'),
    ('extract_regiao', 'extract_regiao', 'regiao'),
]


def create_trigger_test_class(module_name, function_name, table_name):
    """Factory function to create test classes for each trigger."""
    class_name = f'Test{function_name.title().replace("_", "")}'

    class TriggerTestClass(BaseTriggerTest):
        def test_success(self):
            self._test_success(module_name, function_name, table_name)

        def test_empty_table(self):
            self._test_empty_table(module_name, function_name, table_name)

        def test_sql_error(self):
            self._test_sql_error(module_name, function_name, table_name)

    TriggerTestClass.__name__ = class_name
    TriggerTestClass.__qualname__ = class_name
    return TriggerTestClass


# Dynamically create test classes for all triggers
for module_name, function_name, table_name in TRIGGERS:
    test_class = create_trigger_test_class(module_name, function_name, table_name)
    globals()[test_class.__name__] = test_class


if __name__ == '__main__':
    unittest.main()
