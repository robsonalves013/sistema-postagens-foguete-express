from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

# ---------- Função para gerar PDF de Fechamento Diário ----------
def gerar_pdf(postagens):
    if not postagens:
        return

    nome_arquivo = f"fechamento_{datetime.now().strftime('%d%m%Y_%H%M%S')}.pdf"
    c = canvas.Canvas(nome_arquivo, pagesize=A4)
    largura, altura = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, altura - 50, "Fechamento Diário - Sistema de Postagens - Foguete Express 🚀")
    c.setFont("Helvetica", 12)
    c.drawString(50, altura - 70, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    y = altura - 100
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Posto")
    c.drawString(150, y, "Remetente")
    c.drawString(300, y, "Código")
    c.drawString(400, y, "Tipo")
    c.drawString(450, y, "Valor")
    c.drawString(500, y, "Pagamento")
    c.drawString(570, y, "Status")
    c.drawString(640, y, "Funcionário")
    y -= 20

    c.setFont("Helvetica", 10)
    for p in postagens:
        c.drawString(50, y, str(p['posto']))
        c.drawString(150, y, str(p['remetente']))
        c.drawString(300, y, str(p['codigo']))
        c.drawString(400, y, str(p['tipo']))
        c.drawString(450, y, f"R$ {p['valor']:.2f}")
        c.drawString(500, y, str(p['forma_pagamento']))
        c.drawString(570, y, str(p['status_pagamento']))
        c.drawString(640, y, str(p['funcionario']))
        y -= 20
        if y < 50:
            c.showPage()
            y = altura - 50

    c.save()


# ---------- Função para gerar Relatório Mensal ----------
def gerar_relatorio_mensal(postagens):
    if not postagens:
        return

    nome_arquivo = f"relatorio_mensal_{datetime.now().strftime('%d%m%Y_%H%M%S')}.pdf"
    c = canvas.Canvas(nome_arquivo, pagesize=A4)
    largura, altura = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, altura - 50, "Relatório Mensal - Sistema de Postagens - Foguete Express 🚀")
    c.setFont("Helvetica", 12)
    c.drawString(50, altura - 70, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    y = altura - 100
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Posto")
    c.drawString(150, y, "Remetente")
    c.drawString(300, y, "Código")
    c.drawString(400, y, "Tipo")
    c.drawString(450, y, "Valor")
    c.drawString(500, y, "Pagamento")
    c.drawString(570, y, "Status")
    c.drawString(640, y, "Funcionário")
    y -= 20

    c.setFont("Helvetica", 10)
    for p in postagens:
        c.drawString(50, y, str(p['posto']))
        c.drawString(150, y, str(p['remetente']))
        c.drawString(300, y, str(p['codigo']))
        c.drawString(400, y, str(p['tipo']))
        c.drawString(450, y, f"R$ {p['valor']:.2f}")
        c.drawString(500, y, str(p['forma_pagamento']))
        c.drawString(570, y, str(p['status_pagamento']))
        c.drawString(640, y, str(p['funcionario']))
        y -= 20
        if y < 50:
            c.showPage()
            y = altura - 50

    c.save()
