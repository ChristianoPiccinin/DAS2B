import logging
import azure.functions as func

app = func.FunctionApp()

#importar para function principal
from triggers.extract_cliente import bp as cliente
from triggers.extract_pedido import bp as pedido

#registar 
app.register_functions(cliente)
app.register_functions(pedido)
















# @app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
#               use_monitor=False) 
# def extract_pedido_item(myTimer: func.TimerRequest) -> None:
#     logging.info('tabela pedido item.')



# @app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
#               use_monitor=False) 
# def extract_produto(myTimer: func.TimerRequest) -> None:
#     logging.info('tabela produto.')


# @app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
#               use_monitor=False) 
# def extract_regiao(myTimer: func.TimerRequest) -> None:
#     logging.info('tabela regiao')

# @app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
#               use_monitor=False) 
# def extract_representante(myTimer: func.TimerRequest) -> None:
#     logging.info('tabela representante.')





