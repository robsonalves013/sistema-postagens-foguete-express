# utils.py
import io
from fpdf import FPDF
from datetime import datetime

# ------------------ PDF DE POSTAGENS ------------------
def gerar_pdf(postagens, nome_arquivo="fechamento_diario.pdf"):
    """
    Gera PDF de fechamento diário com as postagens fornecidas.
    Retorna BytesIO pronto para download.
    """
    if not postagens:
        return None

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Fechamento Diário - Sistema de Postagens Foguete Express", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    for p in postagens:
        pdf.multi_cell(0, 8,
            f"Posto: {p['posto']}\n"
            f"Remetente: {p['remetente']}\n"
            f"Código: {p['codigo']}\n"
            f"Tipo: {p['tipo']}\n"
            f"Valor: R$ {p['valor']:.2f}\n"
            f"Forma de Pagamento: {p['forma_pagamento']}\n"
            f"Status: {p['status_pagamento']}\n"
            f"Funcionário: {p['funcionario']}\n"
            f"Data Postagem: {p['data_postagem']}\n"
            f"Data Pagamento: {p['data_pagamento'] or ''}\n"
            "--------------------------------------------"
        )
        pdf.ln(2)

    # Gerar PDF em memória
    pdf_bytes = io.BytesIO()
    pdf.output(pdf_bytes)
    pdf_bytes.seek(0)
    return pdf_bytes

# ------------------ RELATÓRIO MENSAL ------------------
def gerar_relatorio_mensal(postagens, nome_arquivo="relatorio_mensal.pdf"):
    """
    Gera PDF de relatório mensal filtrado.
    Retorna BytesIO pronto para download.
    """
    if not postagens:
        return None

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Relatório Mensal - Sistema de Postagens Foguete Express", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    for p in postagens:
        pdf.multi_cell(0, 8,
            f"Posto: {p['posto']}\n"
            f"Remetente: {p['remetente']}\n"
            f"Código: {p['codigo']}\n"
            f"Tipo: {p['tipo']}\n"
            f"Valor: R$ {p['valor']:.2f}\n"
            f"Forma de Pagamento: {p['forma_pagamento']}\n"
            f"Status: {p['status_pagamento']}\n"
            f"Funcionário: {p['funcionario']}\n"
            f"Data Postagem: {p['data_postagem']}\n"
            f"Data Pagamento: {p['data_pagamento'] or ''}\n"
            "--------------------------------------------"
        )
        pdf.ln(2)

    pdf_bytes = io.BytesIO()
    pdf.output(pdf_bytes)
    pdf_bytes.seek(0)
    return pdf_bytes

# ------------------ GUIA DE ATENDENTES ------------------
def gerar_pdf_guia_atendentes():
    """
    Gera o PDF do Guia de Atendentes em memória.
    Retorna BytesIO pronto para download.
    """
    from guia_utilizacao import gerar_guia_utilizacao
    # A função gerar_guia_utilizacao retorna o caminho do arquivo, mas vamos gerar em BytesIO
    nome_arquivo = "guia_atendentes.pdf"
    gerar_guia_utilizacao(nome_arquivo)
    with open(nome_arquivo, "rb") as f:
        pdf_bytes = io.BytesIO(f.read())
    return pdf_bytes

# ------------------ GUIA DE ADMINISTRADORES ------------------
def gerar_pdf_guia_admin():
    """
    Gera o PDF do Guia de Administradores em memória.
    Retorna BytesIO pronto para download.
    """
    from guia_visual import gerar_guia_visual
    nome_arquivo = "guia_administradores.pdf"
    gerar_guia_visual(nome_arquivo)
    with open(nome_arquivo, "rb") as f:
        pdf_bytes = io.BytesIO(f.read())
    return pdf_bytes
