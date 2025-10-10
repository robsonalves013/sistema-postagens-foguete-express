import pandas as pd
from fpdf import FPDF
from io import BytesIO
from datetime import datetime
from guia_visual import gerar_pdf_guia_atendente

def gerar_pdf(postagens):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Fechamento Diário - Foguete Express", ln=True, align="C")
    pdf.ln(10)

    if isinstance(postagens, list):
        postagens = pd.DataFrame(postagens)
    postagens["data_postagem"] = pd.to_datetime(postagens["data_postagem"], errors="coerce")

    # Filtra os status Pago e Pendente
    postagens = postagens[postagens["status_pagamento"].isin(["Pago", "Pendente"])]

    valor_total = postagens["valor"].sum()
    total_postagens = len(postagens)
    formas_pagamento_agg = postagens.groupby("forma_pagamento").size()
    tipos_agg = postagens.groupby("tipo").size()

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Total Geral de Postagens: {total_postagens}", ln=True)
    pdf.cell(0, 10, f"Valor Total Geral: R$ {valor_total:.2f}", ln=True)
    pdf.ln(5)

    pdf.cell(0, 10, "Quantidade por Forma de Pagamento:", ln=True)
    pdf.set_font("Arial", size=11)
    for forma, qtd in formas_pagamento_agg.items():
        pdf.cell(0, 10, f"- {forma}: {qtd}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Quantidade por Tipo de Postagem:", ln=True)
    pdf.set_font("Arial", size=11)
    for tipo, qtd in tipos_agg.items():
        pdf.cell(0, 10, f"- {tipo}: {qtd}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Detalhamento por Posto:", ln=True)
    pdf.ln(5)

    for posto, grupo in postagens.groupby("posto"):
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 10, f"Posto: {posto} (Total: {len(grupo)}, Valor: R$ {grupo['valor'].sum():.2f})", ln=True)
        pdf.set_font("Arial", size=11)
        formas_posto = grupo.groupby("forma_pagamento").size()
        for forma, qtd in formas_posto.items():
            pdf.cell(0, 8, f"   Forma: {forma} - Quantidade: {qtd}", ln=True)
        tipos_posto = grupo.groupby("tipo").size()
        for tipo, qtd in tipos_posto.items():
            pdf.cell(0, 8, f"   Tipo: {tipo} - Quantidade: {qtd}", ln=True)
        pdf.ln(3)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Observações:", ln=True)
    pdf.set_font("Arial", size=10)
    for _, row in postagens.iterrows():
        if row.get("observacao"):
            pdf.multi_cell(0, 5, f"- {row['codigo']}: {row['observacao']}")
    pdf.ln(5)

    pdf_bytes = BytesIO(pdf.output(dest="S").encode("latin1"))
    nome_pdf = f"fechamento_diario_{datetime.now().strftime('%d%m%Y')}.pdf"
    return pdf_bytes, nome_pdf

def gerar_relatorio_mensal(postagens):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Relatório Mensal - Foguete Express", ln=True, align="C")
    pdf.ln(10)

    if isinstance(postagens, list):
        postagens = pd.DataFrame(postagens)

    postagens["data_postagem"] = pd.to_datetime(postagens["data_postagem"], errors="coerce")

    # Filtra os status Pago e Pendente
    postagens = postagens[postagens["status_pagamento"].isin(["Pago", "Pendente"])]

    valor_total = postagens["valor"].sum()
    total_postagens = len(postagens)
    formas_pagamento_agg = postagens.groupby("forma_pagamento").size()
    tipos_agg = postagens.groupby("tipo").size()

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Total Geral de Postagens: {total_postagens}", ln=True)
    pdf.cell(0, 10, f"Valor Total Geral: R$ {valor_total:.2f}", ln=True)
    pdf.ln(5)

    pdf.cell(0, 10, "Quantidade por Forma de Pagamento:", ln=True)
    pdf.set_font("Arial", size=11)
    for forma, qtd in formas_pagamento_agg.items():
        pdf.cell(0, 10, f"- {forma}: {qtd}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Quantidade por Tipo de Postagem:", ln=True)
    pdf.set_font("Arial", size=11)
    for tipo, qtd in tipos_agg.items():
        pdf.cell(0, 10, f"- {tipo}: {qtd}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Detalhamento por Posto:", ln=True)
    pdf.ln(5)

    for posto, grupo in postagens.groupby("posto"):
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 10, f"Posto: {posto} (Total: {len(grupo)}, Valor: R$ {grupo['valor'].sum():.2f})", ln=True)
        pdf.set_font("Arial", size=11)
        formas_posto = grupo.groupby("forma_pagamento").size()
        for forma, qtd in formas_posto.items():
            pdf.cell(0, 8, f"   Forma: {forma} - Quantidade: {qtd}", ln=True)
        tipos_posto = grupo.groupby("tipo").size()
        for tipo, qtd in tipos_posto.items():
            pdf.cell(0, 8, f"   Tipo: {tipo} - Quantidade: {qtd}", ln=True)
        pdf.ln(3)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Observações:", ln=True)
    pdf.set_font("Arial", size=10)
    for _, row in postagens.iterrows():
        if row.get("observacao"):
            pdf.multi_cell(0, 5, f"- {row['codigo']}: {row['observacao']}")
    pdf.ln(5)

    pdf_bytes = BytesIO(pdf.output(dest="S").encode("latin1"))
    nome_pdf = f"relatorio_mensal_{datetime.now().strftime('%m%Y')}.pdf"
    return pdf_bytes, nome_pdf

def gerar_pdf_guia_visual():
    nome_pdf = "guia_utilizacao.pdf"
    gerar_pdf_guia_atendente(nome_pdf)
    with open(nome_pdf, "rb") as f:
        pdf_data = f.read()
    return pdf_data, nome_pdf
