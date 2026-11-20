"""Acrescenta boletos gerados ao ledger, pelo indice (0-based) da fila.

Uso: python registrar.py <fila.csv> <ledger.csv> 19=GeraSGR_..._.pdf 20=GeraSGR_...pdf
Fila (separador ;, com cabecalho): cliente;cnpj;custcode;fatura;valor;vencimento
"""
import csv, os, sys

fila_path, led = sys.argv[1], sys.argv[2]
fila = list(csv.reader(open(fila_path, encoding='utf-8-sig'), delimiter=';'))[1:]
novo = not os.path.exists(led)
with open(led, 'a', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter=';')
    if novo:
        w.writerow(['arquivo_pdf', 'cliente', 'cnpj', 'custcode', 'fatura', 'valor', 'vencimento'])
    for a in sys.argv[3:]:
        i, pdf = a.split('=', 1)
        r = fila[int(i)]
        w.writerow([pdf] + r)
        print(i, pdf, r[0], r[3])
