# Projeto VendaMais Distribuidora -- Plataforma de Inteligência Operacional



## 📌 Descrição
Neste projeto nosso objetivo é montar o conceito de uma arquitetura para a empresa **VendaMais** - uma distribuidora de porte médio que processa cerca de 3.500 pedidos/mês com 18 representantes e opera um ERP proprietário desde 2019. É importante ressaltar que no momento esse trabalho não entregará um sistema desenvolvido. 

Focaremos apenas na base / arquitetura da plataforma de inteligência operacional. Como dito acima, a empresa atualmente opera em ERP (_Enterprise Resource Planning_) e nosso **objetivo é reduzir o atraso de dados em até 24 horas**. Conectando o ERP da empresa ao Azure e ao Power BI.

## 🚩 Problema que resolve
- Relatórios manuais que antes demoravam até dois dias úteis.  
- Indicadores financeiros e incumprimento na atualização de planilhas.  
- Diretoria tomando decisões com dados desatualizados.  

A solução entrega de uma arquitetura base para **visibilidade consolidada e automatizada** de todos os setores da operação.


## 👥 Integrantes da equipe

- Igor Henrique Lorenço - https://github.com/ilorenco 
- João Vitor Ferreira Buhring de Oliveira - https://github.com/JoBuhg 
- Lorena Chaves Barbizan - https://github.com/LorenaR4ven 
- Thiago Schulz da Rosa - https://github.com/ThiagoSchulzRs 

## Estrutura do Projeto

-- Docs <br>
| ↳ ADRs <br>
| -- ↳ ADR_001.md <br>
| -- ↳ ADR_002.md <br>
| ↳ Diagramas <br>
| -- ↳ Diagrama_c4_nivel_1.jpg <br>
| -- ↳ Diagrama_c4_nivel_2.jpg <br>
-- README.md <br>

## Instruções de navegação da documentação

O trabalho esta estruturado visando a facilidade de visualização, seguindo a ordem de Docs(documentos) ➝ ADRs ➝ Diagramas ➝ README.

### 🧭 Fluxo recomendado de leitura

1. Leia o **README.md** para entender o contexto geral  
2. Veja o **Diagrama C4 Nível 1** para visão macro  
3. Aprofunde no nível 2 do diagrama  
4. Consulte os `ADRs` para entender decisões específicas  

#### README.md
Contém:
- Descrição do projeto
- Objetivo e problemas resolvidos do projeto
- Informações dos integrantes
- Instruções básicas de uso

Na pasta "docs" você irá encontrar todo o projeto.

#### ADRs (Architecture Decision Records)
Contêm os registros das decisões arquiteturais 001 e 002 - Entenda o motivo dessas duas escolhas.
    | ➞ ADR_001.md: Decisão arquitetural de **Azure Functions (Python)**
    | ➞ ADR_002.md: Decisão arquitetural de **Armazenamento (Blob Storage)**

#### Diagramas
Contém representações visuais da arquitetura do sistema seguindo o modelo C4 - nos niveis 1 e 2. Utilize para entender a estrutura da arquitetura.
    | ➞ Diagrama_c4_nivel_1.jpg: Visão geral do sistema (contexto)
    | ➞ Diagrama_c4_nivel_2.jpg: Visão dos containers 

## 🧪 Running Tests

Unit tests for the ETL extraction triggers validate three scenarios per trigger: successful extraction, empty source table, and SQL error handling.

### Prerequisites

Ensure your virtual environment is activated and dependencies are installed (see "Local Development" in CLAUDE.md):

```bash
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac
pip install -r src/requirements.txt
```

### Run Tests with unittest (built-in)

```bash
python -m unittest discover -s src -p "test_*.py" -v
```

### Run Tests with pytest (optional)

If pytest is installed:

```bash
python -m pytest src/test_triggers.py -v
```

### Test Coverage

The test suite covers all extraction triggers with three test scenarios per trigger:
- **Success scenario**: Validates that data extraction, DELETE operation, and INSERT all execute correctly
- **Empty table scenario**: Validates warning is logged when source table has no data
- **SQL error scenario**: Validates error is logged and exception is re-raised on database error



