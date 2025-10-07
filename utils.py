from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

def gerar_pdf(postagens):
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    data_atual = datetime.now().strftime("%d/%m/%Y")
    c.drawString(100, 800, f"Fechamento Diário - {data_atual}")
    y = 750
    if not postagens:
        c.drawString(50, y, "Nenhuma postagem cadastrada.")
    else:
        for p in postagens:
            c.drawString(50, y, f"{p['posto']} | {p['remetente']} | {p['codigo']} | {p['tipo']} | "
                                 f"R$ {p['valor']:.2f} | {p['forma_pagamento']} | {p['status_pagamento']} | "
                                 f"{p['funcionario']}")
            y -= 20
            if y < 50:
                c.showPage()
                y = 800
    c.save()
    buffer.seek(0)
    with open("fechamento.pdf", "wb") as f:
        f.write(buffer.getvalue())

def gerar_relatorio_mensal(postagens):
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    c.drawString(100, 800, f"Relatório Mensal - Gerado em {data_atual}")
    y = 750
    if not postagens:
        c.drawString(50, y, "Nenhuma postagem encontrada para o período.")
    else:
        for p in postagens:
            c.drawString(50, y, f"{p['posto']} | {p['remetente']} | {p['codigo']} | {p['tipo']} | "
                                 f"R$ {p['valor']:.2f} | {p['forma_pagamento']} | {p['status_pagamento']} | "
                                 f"{p['funcionario']} | {p['data_postagem']} | {p['data_pagamento']}")
            y -= 20
            if y < 50:
                c.showPage()
                y = 800
    c.save()
    buffer.seek(0)
    with open("relatorio_mensal.pdf", "wb") as f:
        f.write(buffer.getvalue())
