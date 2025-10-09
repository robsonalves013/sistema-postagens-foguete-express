import pandas as pd
from fpdf import FPDF
from io import BytesIO
import streamlit as st
from datetime import datetime
from guia_visual import gerar_pdf_guia_atendente

# -------------------- PDF Fechamento Diário --------------------
def gerar_pdf(postagens):
    """Gera PDF do fechamento diário"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Fechamento Diário - Foguete Express", ln=True, align="C")
    pdf.ln(10)

    # Converter lista em DataFrame se necessário
    if isinstance(postagens, list):
        postagens = pd.DataFrame(postagens)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(40, 10, "Data")
    pdf.cell(60, 10, "Código")
    pdf.cell(40, 10, "Valor (R$)")
    pdf.cell(40, 10, "Status", ln=True)

    pdf.set_font("Arial", size=11)
    total = 0

    for _, row in postagens.iterrows():
        data_postagem = (row["data_postagem"].strftime("%d/%m/%Y %H:%M")
                         if isinstance(row["data_postagem"], datetime) else str(row["data_postagem"]))
        pdf.cell(40, 10, data_postagem)
        pdf.cell(60, 10, str(row["codigo"]))  # corrigido para 'codigo'
        pdf.cell(40, 10, f"{row['valor']:.2f}")
        pdf.cell(40, 10, row["status_pagamento"], ln=True)
        total += float(row["valor"])

    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Total do Dia: R$ {total:.2f}", ln=True, align="R")

    # Retorna PDF em bytes para download
    pdf_bytes = BytesIO(pdf.output(dest="S").encode("latin1"))
    nome_pdf = f"fechamento_diario_{datetime.now().strftime('%d%m%Y')}.pdf"
    return pdf_bytes, nome_pdf

# -------------------- PDF Relatório Mensal --------------------
def gerar_relatorio_mensal(postagens):
    """Gera PDF do relatório mensal"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Relatório Mensal - Foguete Express", ln=True, align="C")
    pdf.ln(10)

    if isinstance(postagens, list):
        postagens = pd.DataFrame(postagens)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(35, 10, "Data")
    pdf.cell(50, 10, "Código")
    pdf.cell(45, 10, "Forma Pag.")
    pdf.cell(40, 10, "Valor (R$)", ln=True)

    pdf.set_font("Arial", size=11)
    total = 0

    for _, row in postagens.iterrows():
        data_postagem = (row["data_postagem"].strftime("%d/%m/%Y %H:%M")
                         if isinstance(row["data_postagem"], datetime) else str(row["data_postagem"]))
        pdf.cell(35, 10, data_postagem)
        pdf.cell(50, 10, str(row["codigo"]))  # corrigido para 'codigo'
        pdf.cell(45, 10, str(row["forma_pagamento"]))
        pdf.cell(40, 10, f"{row['valor']:.2f}", ln=True)
        total += float(row["valor"])

    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Total do Mês: R$ {total:.2f}", ln=True, align="R")

    # Retorna PDF em bytes para download
    pdf_bytes = BytesIO(pdf.output(dest="S").encode("latin1"))
    nome_pdf = f"relatorio_mensal_{datetime.now().strftime('%m%Y')}.pdf"
    return pdf_bytes, nome_pdf

# -------------------- Guia de Utilização --------------------
def gerar_pdf_guia_visual():
    """Gera e oferece para download o Guia de Utilização"""
    nome_pdf = "guia_utilizacao.pdf"
    gerar_pdf_guia_atendente(nome_pdf)
    with open(nome_pdf, "rb") as f:
        pdf_data = f.read()
    return pdf_data, nome_pdf
