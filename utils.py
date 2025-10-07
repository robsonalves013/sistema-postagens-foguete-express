from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def gerar_pdf(postagens, nome_arquivo="fechamento.pdf"):
    from datetime import datetime
    c = canvas.Canvas(nome_arquivo, pagesize=A4)
    largura, altura = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(180, altura - 50, "Fechamento Diário - Sistema de Postagens")

    c.setFont("Helvetica", 10)
    y = altura - 100
    for p in postagens:
        texto = f"{p[1]} | {p[2]} | {p[3]} | R$ {p[5]:.2f} | {p[6]} | {p[7]} | {p[8]} | {p[9]}"
        c.drawString(30, y, texto)
        y -= 15
        if y < 60:
            c.showPage()
            y = altura - 50

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(180, 30, "Sistema desenvolvido por RobTechService © 2025")
    c.save()

def gerar_relatorio_mensal(postagens, nome_arquivo="relatorio_mensal.pdf"):
    from datetime import datetime
    c = canvas.Canvas(nome_arquivo, pagesize=A4)
    largura, altura = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(160, altura - 50, "Relatório Mensal - Sistema de Postagens")

    c.setFont("Helvetica", 10)
    y = altura - 100
    for p in postagens:
        texto = f"{p[1]} | {p[2]} | {p[3]} | {p[4]} | R$ {p[5]:.2f} | {p[6]} | {p[7]} | {p[8]} | {p[9]}"
        c.drawString(30, y, texto)
        y -= 15
        if y < 60:
            c.showPage()
            y = altura - 50

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(180, 30, "Sistema desenvolvido por RobTechService © 2025")
    c.save()
