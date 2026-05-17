# =========================================
# CENÁRIO 3 — PAGAMENTO SEGURO
# =========================================

def mascarar_cartao(cartao):
    return "**** **** **** " + cartao[-4:]

def processar_pagamento(cartao, cvv):

    cartao_mascarado = mascarar_cartao(cartao)

    # nunca mostrar CVV
    print(f"Processando cartão {cartao_mascarado}")

    return "Pagamento aprovado"


print(processar_pagamento("1234567890123456", "123"))