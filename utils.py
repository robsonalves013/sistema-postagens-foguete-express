from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

# ---------- PDF fechamento diário ----------
def gerar_pdf(postagens):
    c = canvas.Canvas("fechamento.pdf", pagesize=A4)
    c.setFont("Helvetica", 12)
    y = 800
    c.drawString(50, y, f"Fechamento Diário - {datetime.now().strftime('%d/%m/%Y')}")
    y -= 30
    for p in postagens:
        texto = f"{p['data_postagem']} | {p['posto']} | {p['remetente']} | {p['codigo']} | {p['tipo']} | R$ {p['valor']:.2f} | {p['status_pagamento']}"
        c.drawString(50, y, texto)
        y -= 20
        if y < 50:
            c.showPage()
            y = 800
    c.save()

# ---------- Relatório mensal ----------
def gerar_relatorio_mensal(postagens):
    c = canvas.Canvas("relatorio_mensal.pdf", pagesize=A4)
    c.setFont("Helvetica", 12)
    y = 800
    c.drawString(50, y, f"Relatório Mensal")
    y -= 30
    for p in postagens:
        texto = f"{p['data_postagem']} | {p['posto']} | {p['remetente']} | {p['codigo']} | {p['tipo']} | R$ {p['valor']:.2f} | {p['status_pagamento']}"
        c.drawString(50, y, texto)
        y -= 20
        if y < 50:
            c.showPage()
            y = 800
    c.save()
