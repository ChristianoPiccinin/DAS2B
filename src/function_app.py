import logging
import azure.functions as func
app = func.FunctionApp()

# Importa triggers para registrar as functions no app
from triggers.extract_cliente import bp as cliente
from triggers.extract_pedido import bp as pedido
from triggers.extract_entrega import bp as entrega
from triggers.extract_representante import bp as representante

# Registrar as azure functions
app.register_functions(cliente)

app.register_functions(pedido)

app.register_functions(entrega)

app.register_functions(representante)
