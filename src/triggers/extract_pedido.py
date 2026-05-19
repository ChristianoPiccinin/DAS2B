import logging
import azure.functions as func

app = func.Blueprint()

@bp.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_pedido(myTimer: func.TimerRequest) -> None:
    logging.info('tabela pedidos')