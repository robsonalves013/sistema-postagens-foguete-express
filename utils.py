# utils.py
from fpdf import FPDF
from datetime import datetime

# ---------- PDF fechamento diário ----------
def gerar_pdf(postagens):
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

    pdf.output("fechamento.pdf")


# ---------- Relatório mensal ----------
def gerar_relatorio_mensal(postagens):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Relatório Mensal", ln=True, align='C')
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

    pdf.output("relatorio_mensal.pdf")
