from fpdf import FPDF
from io import BytesIO
from datetime import datetime

# =========================================================
# 📘 Função para gerar o Fechamento Diário (PDF)
# =========================================================
def gerar_pdf(postagens):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "📦 Foguete Express - Fechamento Diário", ln=True, align="C")
    pdf.ln(5)

    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Gerado em: {data_atual}", ln=True)
    pdf.ln(10)

    # Cabeçalhos
    pdf.set_font("Arial", "B", 11)
    pdf.cell(30, 10, "Data", 1)
    pdf.cell(30, 10, "Posto", 1)
    pdf.cell(40, 10, "Tipo", 1)
    pdf.cell(30, 10, "Valor", 1)
    pdf.cell(60, 10, "Status", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 10)
    total = 0

    for _, row in postagens.iterrows():
        pdf.cell(30, 10, str(row["data_postagem"]), 1)
        pdf.cell(30, 10, str(row["posto"]), 1)
        pdf.cell(40, 10, str(row["tipo_postagem"]), 1)
        pdf.cell(30, 10, f"R$ {row['valor']:.2f}", 1)
        pdf.cell(60, 10, str(row["status_pagamento"]), 1)
        pdf.ln()
        total += row["valor"]

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"💰 Total: R$ {total:.2f}", ln=True, align="R")

    # 🔧 Corrigido — gera em memória, não em disco
    pdf_output = pdf.output(dest='S').encode('latin1')
    pdf_bytes = BytesIO(pdf_output)
    pdf_bytes.seek(0)
    return pdf_bytes


# =========================================================
# 📆 Função para gerar o Relatório Mensal (PDF)
# =========================================================
def gerar_relatorio_mensal(postagens):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "📑 Foguete Express - Relatório Mensal", ln=True, align="C")
    pdf.ln(5)

    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Gerado em: {data_geracao}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(30, 10, "Data", 1)
    pdf.cell(30, 10, "Posto", 1)
    pdf.cell(40, 10, "Tipo", 1)
    pdf.cell(30, 10, "Valor", 1)
    pdf.cell(60, 10, "Status", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 10)
    total = 0

    for _, row in postagens.iterrows():
        pdf.cell(30, 10, str(row["data_postagem"]), 1)
        pdf.cell(30, 10, str(row["posto"]), 1)
        pdf.cell(40, 10, str(row["tipo_postagem"]), 1)
        pdf.cell(30, 10, f"R$ {row['valor']:.2f}", 1)
        pdf.cell(60, 10, str(row["status_pagamento"]), 1)
        pdf.ln()
        total += row["valor"]

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"💰 Total do Período: R$ {total:.2f}", ln=True, align="R")

    # ✅ Corrigido — retorna BytesIO pronto para download
    pdf_output = pdf.output(dest='S').encode('latin1')
    pdf_bytes = BytesIO(pdf_output)
    pdf_bytes.seek(0)
    return pdf_bytes


# =========================================================
# 📘 Guia de Utilização (com emojis e layout visual)
# =========================================================
class GuiaVisual(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, "📦 Guia de Utilização - Sistema Foguete Express", ln=True, align="C")
        self.ln(5)
        self.set_text_color(0, 0, 0)

    def section_title(self, numero, titulo):
        self.set_font("Arial", "B", 13)
        self.set_text_color(0, 102, 0)
        self.cell(0, 8, f"{numero} {titulo}", ln=True)
        self.ln(2)
        self.set_text_color(0, 0, 0)

    def section_body(self, texto):
        self.set_font("Arial", size=11)
        self.multi_cell(0, 8, texto)
        self.ln(3)

    def divider(self):
        self.set_draw_color(0, 102, 204)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)


# =========================================================
# 🎓 Função para gerar o Guia Visual (PDF)
# =========================================================
def gerar_pdf_guia_visual():
    pdf = GuiaVisual()
    pdf.add_page()

    pdf.section_body(
        "Este guia auxilia os atendentes no uso correto do Sistema de Postagens. "
        "Siga as instruções abaixo para realizar as operações de forma eficiente e segura."
    )
    pdf.divider()

    pdf.section_title("1️⃣", "Login")
    pdf.section_body(
        "- Acesse o sistema com seu usuário e senha.\n"
        "- Caso esqueça a senha, contate o administrador."
    )
    pdf.divider()

    pdf.section_title("2️⃣", "Menu Principal")
    pdf.section_body(
        "- 📊 Dashboard: visão geral de postagens e valores.\n"
        "- 📝 Cadastrar Postagem: registra novas postagens.\n"
        "- 📋 Listar Postagens: visualiza postagens cadastradas.\n"
        "- 👥 Gerenciar Usuários: apenas administradores.\n"
        "- 💰 Pagamentos Pendentes: marca postagens pagas.\n"
        "- 🧾 Fechamento Diário: gera PDF com postagens do dia.\n"
        "- 📑 Relatório Mensal: gera PDF filtrado por mês, tipo e forma de pagamento."
    )
    pdf.divider()

    pdf.section_title("3️⃣", "Cadastrar Postagem")
    pdf.section_body(
        "- Preencha todos os campos obrigatórios.\n"
        "- Se o status for 'Pendente', a data de pagamento fica em branco.\n"
        "- Clique em 'Cadastrar' para salvar."
    )
    pdf.divider()

    pdf.section_title("4️⃣", "Editar Postagem")
    pdf.section_body(
        "- Apenas administradores podem editar.\n"
        "- Vá em 'Listar Postagens' e clique em 'Editar'."
    )
    pdf.divider()

    pdf.section_title("5️⃣", "Relatórios e Fechamento")
    pdf.section_body(
        "- 🧾 Fechamento Diário: gera resumo do dia.\n"
        "- 📑 Relatório Mensal: gera PDF filtrado.\n"
        "- O PDF é baixado automaticamente."
    )
    pdf.divider()

    pdf.section_title("📌", "Observações Finais")
    pdf.section_body(
        "- Guarde suas credenciais com segurança.\n"
        "- Dúvidas? Contate o administrador.\n"
        "- WhatsApp: (11) 96396-1937\n"
        "- E-mail: robtechservice@outlook.com"
    )

    # ✅ Corrigido — retorno em memória (BytesIO)
    pdf_output = pdf.output(dest='S').encode('latin1')
    pdf_bytes = BytesIO(pdf_output)
    pdf_bytes.seek(0)
    return pdf_bytes
