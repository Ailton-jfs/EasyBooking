##Planejamento do projeto de QA

##Tema Escolhido
Tema: Sistema de Agendamento
##Proposta:
Desenvolver um sistema simples de agendamento onde usuários possam marcar, visualizar e cancelar horários para serviços (ex: consultas, atendimentos ou reservas). O sistema permitirá testar funcionalidades básicas como cadastro, validação de dados e controle de horários disponíveis.

##Descrição do Sistema
Descrever de forma objetiva:
O que o sistema faz:
Permite que usuários realizem agendamentos de horários, consultem seus agendamentos e cancelem quando necessário.
Quem utilizará o sistema:
Clientes que desejam agendar horários e administradores que gerenciam os agendamentos. 
Qual problema ele resolve:
Evita conflitos de horários e organiza o controle de atendimentos de forma simples e automatizada. 
Orientação: evitem textos longos. Se não conseguem explicar em poucas linhas, o sistema ainda não está claro.
##Funcionalidades Principais
Listar pelo menos 5 funcionalidades.
Cadastro de usuário
Login de usuário
Criação de agendamento
Consulta de agendamentos
Cancelamento de agendamento
Validação de horários disponíveis
Orientação: pensem em funcionalidades simples, mas que possam ser testadas.
##Definição Inicial de Testes
Criar pelo menos 5 cenários de teste.
Cada cenário deve indicar:
Criar agendamento em horário já ocupado → sistema deve impedir
Criar agendamento com dados incompletos → deve retornar erro
Cancelar agendamento inexistente → deve retornar erro
Login com senha incorreta → deve negar acesso
Inserir data inválida → sistema deve rejeitar
Orientação: um bom teste tenta encontrar erro, não apenas confirmar que funciona.
4.6 Tecnologias e Ferramentas
Informar:
Como pretendem desenvolver o protótipo em Python
O sistema será desenvolvido em Python, com foco em um protótipo simples e funcional.
Quais ferramentas pretendem utilizar
Para os testes, serão utilizadas abordagens mais diretas, como:
pytest para testes automatizados básicos
Testes manuais para validação das funcionalidades
Uso de comandos simples (como print) para verificação do comportamento do sistema


##Organização do Grupo
Definir quem ficará responsável por:
Desenvolvimento (interface):
Guilherme, Murilo e Dennis
Desenvolvimento (lógica do sistema):
Ailton e Antonio
Testes:
Ailton e Antonio
Documentação:
Guilherme e Dennis
Apresentação
Todos os integrantes do grupo
