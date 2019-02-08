# -*- coding: utf-8 -*-
from pynubank import Nubank
from money_parser import price_str
import json
import csv
import os
import getpass
import re

filename = "extrato.json"
filenameCSV = "extrato.csv"

if (os.path.isfile(filename) == False):
    username = input("Informe seu CPF:\n")
    password = getpass.getpass("Informe sua SENHA:\n")

    # Utilize o CPF sem pontos ou traços
    nu = Nubank(username, password)

    extrato = nu.get_account_feed();
    extratoJSON = json.dumps(extrato)

    F = open(filename, "w")
    F.write(extratoJSON)

    # print(extratoJSON)

    # Lista de dicionários contendo todas as transações de seu cartão de crédito
    account_statements = nu.get_account_statements()

    # Soma de todas as transações na NuConta
    # Observacão: As transações de saída não possuem o valor negativo, então deve-se olhar a propriedade "__typename".
    # TransferInEvent = Entrada
    # TransferOutEvent = Saída
    # TransferOutReversalEvent = Devolução
    print(sum([t['amount'] for t in account_statements]))

    # Saldo atual
    print(nu.get_account_balance())
else:
    F = open(filename, "r")
    extratoJSON = F.read()
    extrato = json.loads(extratoJSON)

# print(extratoJSON)
with open(filenameCSV, mode='w') as employee_file:
    employee_writer = csv.writer(employee_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    i = -1;
    while (i < len(extrato) - 1):
        i += 1

        # Eventos que geram movimentação da conta
        if extrato[i]['__typename'] not in ["TransferInEvent", "TransferOutEvent", "BillPaymentEvent"]:
            continue

        if "amount" not in extrato[i]:
            amountRegex = re.search(r'(R\$ [0-9\.]+,\d+)', extrato[i]['detail'], flags=0)

            if amountRegex == None:
                continue

            amount = float(price_str(amountRegex.group(1)))
        else:
            amount = extrato[i]['amount']

        multiplier = -1 if extrato[i]['__typename'] in ["TransferOutEvent", "BillPaymentEvent"] else 1
        employee_writer.writerow([
            extrato[i]['id'],
            extrato[i]['postDate'],
            extrato[i]['title'] + " " + extrato[i]['detail'],
            amount * multiplier
        ])

print("Arquivo CSV Gerado")
