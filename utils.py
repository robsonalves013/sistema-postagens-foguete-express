# utils.py
from fpdf import FPDF
from datetime import datetime

# ---------- PDF fechamento diário ----------
def gerar_pdf(postagens):
    if not postagens:
        return None

    data_hoje = datetime.now().strftime("%d-%m-%Y")
    nome_arquivo = f"fechamento_{data_hoje}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Fechamento Diário - {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", size=12)

    # Cabeçalho
    pdf.cell(25, 8, "Data", border=1)
    pdf.cell(35, 8, "Posto", border=1)
    pdf.cell(40, 8, "Remetente", border=1)
    pdf.cell(40, 8, "Código", border=1)
    pdf.cell(25, 8, "Tipo", border=1)
    pdf.cell(20, 8, "Valor", border=1)
    pdf.cell(25, 8, "Status", border=1)
    pdf.ln()

    for p in postagens:
        pdf.cell(25, 8, p['data_postagem'], border=1)
        pdf.cell(35, 8, p['posto'], border=1)
        pdf.cell(40, 8, p['remetente'], border=1)
        pdf.cell(40, 8, p['codigo'], border=1)
        pdf.cell(25, 8, p['tipo'], border=1)
        pdf.cell(20, 8, f"R$ {p['valor']:.2f}", border=1)
        pdf.cell(25, 8, p['status_pagamento'], border=1)
        pdf.ln()

    pdf.output(nome_arquivo)
    return nome_arquivo


# ---------- Relatório mensal ----------
def gerar_relatorio_mensal(postagens):
    if not postagens:
        return None

    data_hoje = datetime.now().strftime("%d-%m-%Y")
    nome_arquivo = f"relatorio_mensal_{data_hoje}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Relatório Mensal - {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", size=12)

    # Cabeçalho
    pdf.cell(25, 8, "Data", border=1)
    pdf.cell(35, 8, "Posto", border=1)
    pdf.cell(40, 8, "Remetente", border=1)
    pdf.cell(40, 8, "Código", border=1)
    pdf.cell(25, 8, "Tipo", border=1)
    pdf.cell(20, 8, "Valor", border=1)
    pdf.cell(25, 8, "Status", border=1)
    pdf.ln()

    for p in postagens:
        pdf.cell(25, 8, p['data_postagem'], border=1)
        pdf.cell(35, 8, p['posto'], border=1)
        pdf.cell(40, 8, p['remetente'], border=1)
        pdf.cell(40, 8, p['codigo'], border=1)
        pdf.cell(25, 8, p['tipo'], border=1)
        pdf.cell(20, 8, f"R$ {p['valor']:.2f}", border=1)
        pdf.cell(25, 8, p['status_pagamento'], border=1)
        pdf.ln()

    pdf.output(nome_arquivo)
    return nome_arquivo
