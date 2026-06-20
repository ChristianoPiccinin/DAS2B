import logging
import azure.functions as func
from base import (
    register_global_observer,
)
from base.observers import (
    LoggingObserver,
    MetricsObserver,
    ErrorObserver,
)

app = func.FunctionApp()

# Register global observers at startup
register_global_observer(LoggingObserver())
register_global_observer(MetricsObserver())
register_global_observer(ErrorObserver())

# Importa triggers para registrar as functions no app
from triggers.extract_categoria_produto import bp as categoria_produto
from triggers.extract_cliente import bp as cliente
from triggers.extract_entrega import bp as entrega
from triggers.extract_estoque_movimentacao import bp as estoque_movimentacao
from triggers.extract_estoque_saldo import bp as estoque_saldo
from triggers.extract_fornecedor import bp as fornecedor
from triggers.extract_pedido import bp as pedido
from triggers.extract_pedido_item import bp as pedido_item
from triggers.extract_produto import bp as produto
from triggers.extract_regiao import bp as regiao
from triggers.extract_representante import bp as representante
from triggers.extract_titulo_receber import bp as titulo_receber
from triggers.extract_transportadora import bp as transportadora

# Registrar as azure functions
app.register_functions(categoria_produto)
app.register_functions(cliente)
app.register_functions(entrega)
app.register_functions(estoque_movimentacao)
app.register_functions(estoque_saldo)
app.register_functions(fornecedor)
app.register_functions(pedido)
app.register_functions(pedido_item)
app.register_functions(produto)
app.register_functions(regiao)
app.register_functions(representante)
app.register_functions(titulo_receber)
app.register_functions(transportadora)
