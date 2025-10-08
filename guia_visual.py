# guia_visual.py
from fpdf import FPDF
from datetime import datetime

class GuiaVisual(FPDF):
    def header(self):
        # Cabeçalho colorido
        self.set_font("Arial", "B", 16)
        self.set_text_color(0, 51, 102)  # Azul escuro
        self.cell(0, 10, "📦 Guia de Utilização - Sistema de Postagens", ln=True, align="C")
        self.ln(5)
        self.set_text_color(0, 0, 0)

    def section_title(self, numero, titulo):
        self.set_font("Arial", "B", 14)
        self.set_text_color(0, 102, 0)  # Verde escuro
        self.cell(0, 8, f"{numero} {titulo}", ln=True)
        self.ln(2)
        self.set_text_color(0, 0, 0)
    
    def section_body(self, texto):
        self.set_font("Arial", size=12)
        self.multi_cell(0, 8, texto)
        self.ln(3)
    
    def divider(self):
        self.set_draw_color(0, 102, 204)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

def gerar_guia_visual(nome_arquivo="guia_utilizacao_visual.pdf"):
    pdf = GuiaVisual()
    pdf.add_page()

    # Introdução
    pdf.section_body(
        "Este guia tem como objetivo auxiliar os atendentes no uso correto do Sistema de Postagens. "
        "Siga as instruções abaixo para realizar as operações de forma eficiente e segura."
    )
    pdf.divider()

    # 1️⃣ Login
    pdf.section_title("1️⃣", "Login")
    pdf.section_body(
        "- Acesse o sistema usando seu usuário e senha.\n"
        "- Apenas usuários cadastrados podem acessar.\n"
        "- Caso esqueça a senha, contate o administrador do sistema."
    )
    pdf.divider()

    # 2️⃣ Menu Principal
    pdf.section_title("2️⃣", "Menu Principal")
    pdf.section_body(
        "- 📊 Dashboard: resumo das postagens, valores totais e status de pagamentos.\n"
        "- 📝 Cadastrar Postagem: registre novas postagens.\n"
        "- 📋 Listar Postagens: visualize todas as postagens cadastradas.\n"
        "- 👥 Gerenciar Usuários: disponível apenas para administradores.\n"
        "- 💰 Pagamentos Pendentes: marque postagens como pagas.\n"
        "- 🧾 Fechamento Diário: gere PDF do fechamento diário.\n"
        "- 📑 Relatório Mensal: gere PDF com filtros por mês, tipo e forma de pagamento."
    )
    pdf.divider()

    # 3️⃣ Cadastrar Postagem
    pdf.section_title("3️⃣", "Cadastrar Postagem")
    pdf.section_body(
        "- Preencha todos os campos obrigatórios: Posto, Remetente, Código de Rastreamento, Tipo, Valor, Forma e Status de Pagamento, Funcionário, Datas.\n"
        "- O sistema não permite duplicidade de códigos de rastreio.\n"
        "- Clique em 'Cadastrar' para salvar a postagem."
    )
    pdf.divider()

    # 4️⃣ Editar Postagem
    pdf.section_title("4️⃣", "Editar Postagem")
    pdf.section_body(
        "- Apenas administradores podem editar postagens já cadastradas.\n"
        "- Abra a postagem desejada em 'Listar Postagens' e clique em 'Editar'.\n"
        "- Faça as alterações e clique em 'Salvar Alterações'."
    )
    pdf.divider()

    # 5️⃣ Pagamentos Pendentes
    pdf.section_title("5️⃣", "Pagamentos Pendentes")
    pdf.section_body(
        "- Acesse a aba 'Pagamentos Pendentes' para ver todas as postagens com pagamento não confirmado.\n"
        "- Clique em 'Marcar como Pago' quando o pagamento for efetuado.\n"
        "- A data de pagamento será atualizada automaticamente."
    )
    pdf.divider()

    # 6️⃣ Relatórios
    pdf.section_title("6️⃣", "Fechamento Diário e Relatório Mensal")
    pdf.section_body(
        "- 🧾 Fechamento Diário: gera PDF com todas as postagens do dia.\n"
        "- 📑 Relatório Mensal: gera PDF com postagens filtradas por mês, tipo de postagem, forma de pagamento e posto.\n"
        "- Apenas administradores podem gerar relatórios mensais."
    )
    pdf.divider()

    # Observações finais
    pdf.section_title("📌", "Observações Finais")
    pdf.section_body(
        "- Mantenha seus dados de login confidenciais.\n"
        "- Siga sempre o fluxo correto para evitar inconsistências nos registros.\n"
        "- Em caso de dúvidas, contate o administrador do sistema."
    )

    # Salvar PDF
    pdf.output(nome_arquivo)
    print(f"PDF visual de guia de utilização gerado: {nome_arquivo}")
    return nome_arquivo

if __name__ == "__main__":
    gerar_guia_visual()
