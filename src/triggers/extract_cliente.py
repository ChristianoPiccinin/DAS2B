import logging
import azure.functions as func
import os
import pyodbc
import time
from datetime import datetime
from uuid import uuid4

from ..base import (
    BaseTrigger,
    TriggerStartEvent,
    TriggerSuccessEvent,
    TriggerFailureEvent,
    TriggerCompleteEvent,
)

bp = func.Blueprint()


class ExtractClienteTrigger(BaseTrigger):
    """Trigger for extracting cliente data from ERP to Azure SQL."""

    def __init__(self):
        super().__init__(trigger_name='extract_cliente')

    def run(self, myTimer: func.TimerRequest) -> None:
        """Execute the cliente extraction pipeline."""
        execution_id = str(uuid4())
        start_time = time.time()

        try:
            # Notify observers: trigger started
            self._notify_observers('start', TriggerStartEvent(
                trigger_name=self.trigger_name,
                timestamp=datetime.now(),
                execution_id=execution_id
            ))

            logging.info('tabela cliente.')

            # Credenciais do banco SOURCE (professor)
            sql_server_source = os.getenv("SQL_SERVER_SOURCE")
            sql_database_source = os.getenv("SQL_DATABASE_SOURCE")
            sql_user_source = os.getenv("SQL_USER_SOURCE")
            sql_pass_source = os.getenv("SQL_PASSWORD_SOURCE")

            # Credenciais do banco DESTINATION (aluno)
            sql_server_dest = os.getenv("SQL_SERVER_TARGET")
            sql_database_dest = os.getenv("SQL_DATABASE_TARGET")
            sql_user_dest = os.getenv("SQL_USER_TARGET")
            sql_pass_dest = os.getenv("SQL_PASSWORD_TARGET")

            logging.info(f'Conectando ao banco SOURCE: {sql_server_source}/{sql_database_source}')

            # ========== EXTRAÇÃO ==========
            conn_str_source = (
                "DRIVER={ODBC Driver 18 for SQL Server};"
                f"SERVER={sql_server_source};"
                f"DATABASE={sql_database_source};"
                f"UID={sql_user_source};"
                f"PWD={sql_pass_source};"
                "Encrypt=yes;"
                "TrustServerCertificate=no;"
                "Connection Timeout=30;"
            )

            with pyodbc.connect(conn_str_source) as conn_source:
                cursor_source = conn_source.cursor()
                query = "SELECT * FROM erp.cliente"
                cursor_source.execute(query)
                rows = cursor_source.fetchall()
                columns = [description[0] for description in cursor_source.description]

            if not rows:
                logging.warning('Nenhum registro encontrado na tabela cliente')
                return

            logging.info(f'Extração bem-sucedida: {len(rows)} registros encontrados')

            # ========== CARREGAMENTO ==========
            conn_str_dest = (
                "DRIVER={ODBC Driver 18 for SQL Server};"
                f"SERVER={sql_server_dest};"
                f"DATABASE={sql_database_dest};"
                f"UID={sql_user_dest};"
                f"PWD={sql_pass_dest};"
                "Encrypt=yes;"
                "TrustServerCertificate=no;"
                "Connection Timeout=30;"
            )

            with pyodbc.connect(conn_str_dest) as conn_dest:
                cursor_dest = conn_dest.cursor()

                # Limpar dados anteriores (idempotência)
                cursor_dest.execute("DELETE FROM erp.cliente")
                logging.info('Tabela de destino limpa')

                # Inserir novos dados
                placeholders = ','.join(['?' for _ in columns])
                insert_query = f"INSERT INTO erp.cliente ({','.join(columns)}) VALUES ({placeholders})"

                cursor_dest.executemany(insert_query, rows)
                conn_dest.commit()

            logging.info(f'Carregamento bem-sucedido: {len(rows)} registros inseridos')

            # Notify observers: trigger succeeded
            duration = time.time() - start_time
            self._notify_observers('success', TriggerSuccessEvent(
                trigger_name=self.trigger_name,
                duration_seconds=duration,
                rows_processed=len(rows),
                execution_id=execution_id
            ))

        except (pyodbc.Error, Exception) as e:
            duration = time.time() - start_time
            # Notify observers: trigger failed
            self._notify_observers('failure', TriggerFailureEvent(
                trigger_name=self.trigger_name,
                duration_seconds=duration,
                exception=e,
                execution_id=execution_id
            ))
            logging.error(f"Erro: {str(e)}")
            raise

        finally:
            # Notify observers: trigger complete
            self._notify_observers('complete', TriggerCompleteEvent(
                trigger_name=self.trigger_name,
                execution_id=execution_id
            ))


@bp.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False)
def extract_cliente(myTimer: func.TimerRequest) -> None:
    """Azure Function entry point for cliente extraction."""
    trigger = ExtractClienteTrigger()
    trigger.run(myTimer)