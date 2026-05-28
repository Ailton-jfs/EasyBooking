# EasyBooking
Projeto de sistema de agendamento com foco em testes de Quality Assurance (QA).

## Integrantes
- Ailton
- Antonio
- Dennis
- Murilo
- Guilherme

## Descrição
Este projeto tem como objetivo desenvolver um sistema simples de agendamento, permitindo criar, visualizar e cancelar horários. O foco principal é aplicar conceitos de Quality Assurance (QA), criando uma base para testes automatizados e validações funcionais.

## Recursos principais
- Cadastro e login de usuários com validação de senha forte.
- Agendamento com horários pré-definidos e opção de horário customizado (`HH:MM`).
- Sugestão do próximo horário livre na mesma data e busca do próximo dia com slots livres (janela padrão: 30 dias).
- Histórico limitado no dashboard (últimos 5 agendamentos) para reduzir uso de banco de dados.
- Backend em Flask com persistência SQLite e testes em `pytest`.

## Estrutura importante
- Código principal: `server.py` (em `projeto-QA/EasyBooking/server.py`)
- Lógica de agendamentos: `app/agendamentos.py`
- Templates: `templates/`
- Arquivos de teste: `tests/`
- Dependências: `requirements.txt`

## Instalação
1. Crie um ambiente virtual (recomendado):

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Unix/macOS:
source .venv/bin/activate
```

2. Instale dependências:

```bash
pip install -r projeto-QA/EasyBooking/requirements.txt
```

## Executando localmente

```bash
cd projeto-QA/EasyBooking
python server.py
# Acesse http://127.0.0.1:5000
```

## Testes

Rode a suíte de testes com `pytest`:

```bash
cd projeto-QA/EasyBooking
pytest -q
```
