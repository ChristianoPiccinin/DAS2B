import logging
import azure.functions as func

app = func.FunctionApp()

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def timer_trigger_aula02(myTimer: func.TimerRequest) -> None:
    logging.info('aula 2.')





@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def timer_trigger_aula03(myTimer: func.TimerRequest) -> None:
    logging.info('aula 3.')