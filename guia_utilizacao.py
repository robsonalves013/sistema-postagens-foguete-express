# guia_utilizacao.py
from fpdf import FPDF
from datetime import datetime

def gerar_guia_utilizacao(nome_arquivo="guia_utilizacao.pdf"):
    pdf = FPDF()
    pdf.add_page()
    
    # --- Cabeçalho ---
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Guia de Utilização - Sistema de Postagens - Foguete Express", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("Arial", size=12)
    
    # --- Introdução ---
    pdf.multi_cell(0, 8,
        "Este guia tem como objetivo auxiliar os atendentes no uso correto do Sistema de Postagens. "
        "Siga as instruções abaixo para realizar as operações de forma eficiente e segura."
    )
    pdf.ln(5)
    
    # --- Login ---
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, "1️⃣ Login", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8,
        "- Acesse o sistema usando seu usuário e senha.\n"
        "- Apenas usuários cadastrados podem acessar.\n"
        "- Caso esqueça a senha, contate o administrador do sistema."
    )
    pdf.ln(5)
    
    # --- Menu Principal ---
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, "2️⃣ Menu Principal", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8,
        "- Dashboard: visualização do resumo das postagens, valores totais e status de pagamentos.\n"
        "- Cadastrar Postagem: registre novas postagens com todos os dados necessários.\n"
        "- Listar Postagens: visualize todas as postagens cadastradas.\n"
        "- Gerenciar Usuários: disponível apenas para administradores.\n"
        "- Pagamentos Pendentes: marque postagens como pagas quando o pagamento for realizado.\n"
        "- Fechamento Diário: gere o PDF do fechamento das postagens do dia.\n"
        "- Relatório Mensal: gere relatórios em PDF filtrando por mês, tipo e forma de pagamento."
    )
    pdf.ln(5)
    
    # --- Cadastrar Postagem ---
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, "3️⃣ Cadastrar Postagem", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8,
        "- Preencha todos os campos obrigatórios: Posto, Remetente, Código de Rastreamento, Tipo, Valor, Forma e Status de Pagamento, Funcionário, Datas.\n"
        "- O sistema não permite duplicidade de códigos de rastreio.\n"
        "- Clique em 'Cadastrar' para salvar a postagem."
    )
    pdf.ln(5)
    
    # --- Editar Postagem ---
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, "4️⃣ Editar Postagem", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8,
        "- Apenas administradores podem editar postagens já cadastradas.\n"
        "- Acesse 'Listar Postagens', abra a postagem desejada e clique em 'Editar'.\n"
        "- Faça as alterações e clique em 'Salvar Alterações'."
    )
    pdf.ln(5)
    
    # --- Pagamentos Pendentes ---
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, "5️⃣ Pagamentos Pendentes", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8,
        "- Acesse a aba 'Pagamentos Pendentes' para ver todas as postagens com pagamento não confirmado.\n"
        "- Clique em 'Marcar como Pago' quando o pagamento for efetuado.\n"
        "- A data de pagamento será atualizada automaticamente."
    )
    pdf.ln(5)
    
    # --- Fechamento Diário e Relatório Mensal ---
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, "6️⃣ Relatórios", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8,
        "- Fechamento Diário: gera PDF com todas as postagens do dia atual.\n"
        "- Relatório Mensal: gera PDF com postagens filtradas por mês, tipo de postagem, forma de pagamento e posto.\n"
        "- Somente administradores podem gerar relatórios mensais."
    )
    pdf.ln(5)
    
    # --- Finalização ---
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "📌 Observações Finais", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8,
        "- Mantenha seus dados de login confidenciais.\n"
        "- Em caso de dúvidas, contate o administrador do sistema.\n"
        "- Siga sempre o fluxo correto para evitar inconsistências nos registros."
    )
    pdf.ln(5)
    
    # --- Salvar PDF ---
    pdf.output(nome_arquivo)
    print(f"PDF de guia de utilização gerado: {nome_arquivo}")
    return nome_arquivo

# --- Gerar PDF ---
if __name__ == "__main__":
    gerar_guia_utilizacao()
