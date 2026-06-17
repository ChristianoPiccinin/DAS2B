import logging
import azure.functions as func
import os 
import pyodbc

bp = func.Blueprint()


@bp.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_cliente(myTimer: func.TimerRequest) -> None:
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
    
    # NÃO LOG credenciais!
    logging.info(f'Conectando ao banco SOURCE: {sql_server_source}/{sql_database_source}')
    
    try:
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
        
    except pyodbc.Error as e:
        logging.error(f"Erro SQL: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Erro inesperado: {str(e)}")
        raise