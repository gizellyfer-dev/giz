"""Renomeia os PDFs GeraSGR_*.pdf baixados usando o ledger.

Uso: python renomear.py <ledger.csv> [pasta_downloads]
Ledger (separador ;): arquivo_pdf;cliente;cnpj;custcode;fatura;valor;vencimento
"""
import csv, os, re, sys

led = sys.argv[1]
dl = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.environ['USERPROFILE'], 'Downloads')

for r in csv.DictReader(open(led, encoding='utf-8-sig'), delimiter=';'):
    src = os.path.join(dl, r['arquivo_pdf'])
    a, m, d = r['vencimento'].split('-')
    nome = f"{r['cliente']} - CustCode {r['custcode']} - Fatura {r['fatura']} - venc {d}-{m}-{a} - R$ {r['valor']}.pdf"
    nome = re.sub(r'[\\/:*?"<>|]', '-', nome).replace('  ', ' ')
    dst = os.path.join(dl, nome)
    if os.path.exists(dst):
        continue  # ja renomeado
    if not os.path.exists(src):
        print('NAO ACHEI', r['arquivo_pdf'], '|', r['cliente'], r['fatura'])
        continue
    try:
        os.rename(src, dst)
        print('OK', nome)
    except PermissionError:
        print('EM USO', r['arquivo_pdf'])
