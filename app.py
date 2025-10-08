# app.py
import streamlit as st
from datetime import datetime
import db
from utils import gerar_pdf, gerar_relatorio_mensal
from streamlit_autorefresh import st_autorefresh
from dashboard import mostrar_dashboard  # Importa o dashboard modularizado

# Inicializa banco
db.criar_tabelas()
st.set_page_config(page_title="Sistema de Postagens", layout="centered")

# ------------------- Sessão -------------------
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

# ----------------- Tela de Login -----------------
if not st.session_state["logado"]:
    st.title("📦 Sistema de Postagens - Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        user = db.autenticar(usuario, senha)
        if user:
            st.session_state["logado"] = True
            st.session_state["usuario"] = user
            st.success("Login realizado com sucesso!")
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos.")

# ----------------- Tela Principal -----------------
else:
    user = st.session_state["usuario"]
    admin = bool(user['is_admin'])

    st.sidebar.title("Menu")
    opcoes = ["Dashboard", "Cadastrar Postagem", "Listar Postagens", "Pagamentos Pendentes", "Fechamento Diário"]
    if admin:
        opcoes.append("Gerenciar Usuários")
        opcoes.append("Relatório Mensal")

    opcao = st.sidebar.radio("Selecione uma opção", opcoes)
    st.sidebar.markdown("---")
    st.sidebar.write(f"👤 {user['nome']} ({'Admin' if admin else 'Usuário'})")

    if st.sidebar.button("Sair"):
        st.session_state["logado"] = False
        st.session_state["usuario"] = None
        st.success("Logout realizado com sucesso!")
        st.experimental_rerun()

    # ----------------- DASHBOARD -----------------
    if opcao == "Dashboard":
        mostrar_dashboard()  # Chama o dashboard modularizado

    # ----------------- CADASTRAR POSTAGEM -----------------
    elif opcao == "Cadastrar Postagem":
        st.header("📮 Nova Postagem")
        posto = st.selectbox("Posto", ["Shopping Bolivia", "Hotel Family"])
        remetente = st.text_input("Remetente")
        codigo = st.text_input("Código de Rastreamento")
        tipo = st.selectbox("Tipo de Postagem", ["PAC", "SEDEX"])
        valor = st.number_input("Valor (R$)", min_value=0.0, step=0.5)
        forma_pagamento = st.selectbox("Forma de Pagamento", ["Dinheiro", "PIX"])
        status_pagamento = st.selectbox("Status", ["Pago", "Pendente"])
        funcionario = st.selectbox("Funcionário", ["Jair", "Yuri"])
        data_postagem = datetime.now().strftime("%d/%m/%Y")
        data_pagamento = st.date_input("Data de Pagamento (opcional)").strftime("%d/%m/%Y")

        if st.button("Salvar"):
            dados = (posto, remetente, codigo, tipo, valor, forma_pagamento, status_pagamento, funcionario, data_postagem, data_pagamento)
            db.adicionar_postagem(dados)
            st.success("Postagem cadastrada com sucesso!")
            st.experimental_rerun()

    # ----------------- LISTAR POSTAGENS -----------------
    elif opcao == "Listar Postagens":
        st.header("📋 Lista de Postagens")
        st_autorefresh(interval=5000, key="refresher")
        postagens = db.listar_postagens()
        if postagens:
            for p in postagens:
                with st.expander(f"📦 {p['codigo']} | {p['posto']} | {p['remetente']}"):
                    st.write(f"Posto: {p['posto']}")
                    st.write(f"Remetente: {p['remetente']}")
                    st.write(f"Código: {p['codigo']}")
                    st.write(f"Tipo: {p['tipo']}")
                    st.write(f"Valor: R$ {p['valor']:.2f}")
                    st.write(f"Forma de Pagamento: {p['forma_pagamento']}")
                    st.write(f"Status: {p['status_pagamento']}")
                    st.write(f"Funcionário: {p['funcionario']}")
                    st.write(f"Data Postagem: {p['data_postagem']}")
                    st.write(f"Data Pagamento: {p['data_pagamento']}")
        else:
            st.info("Nenhuma postagem cadastrada.")

    # ----------------- PAGAMENTOS PENDENTES -----------------
    elif opcao == "Pagamentos Pendentes":
        st.header("💰 Pagamentos Pendentes")
        pendentes = db.listar_postagens_pendentes()
        if not pendentes:
            st.info("Nenhum pagamento pendente encontrado.")
        else:
            for p in pendentes:
                with st.expander(f"📦 {p['codigo']} | {p['posto']} | R$ {p['valor']:.2f}"):
                    st.write(f"Remetente: {p['remetente']}")
                    st.write(f"Funcionário: {p['funcionario']}")
                    st.write(f"Data Postagem: {p['data_postagem']}")
                    if st.button("✅ Marcar como Pago", key=f"pago_{p['id']}"):
                        data_atual = datetime.now().strftime("%d/%m/%Y")
                        db.atualizar_pagamento(p['id'], "Pago", data_atual)
                        st.success(f"Pagamento da postagem {p['codigo']} marcado como pago em {data_atual}!")
                        st.experimental_rerun()

    # ----------------- FECHAMENTO DIÁRIO -----------------
    elif opcao == "Fechamento Diário":
        st.header("🧾 Fechamento Diário")
        postagens = db.listar_postagens()
        if st.button("Gerar PDF"):
            gerar_pdf(postagens)
            with open("fechamento.pdf", "rb") as f:
                st.download_button("Baixar PDF", f, file_name="fechamento.pdf")
        st.info("O relatório incluirá todas as postagens do dia.")

    # ----------------- GERENCIAR USUÁRIOS -----------------
    elif opcao == "Gerenciar Usuários" and admin:
        st.header("👥 Gerenciar Usuários")
        # Cadastro, edição e exclusão mantidos como no seu código
        # ...

    # ----------------- RELATÓRIO MENSAL -----------------
    elif opcao == "Relatório Mensal" and admin:
        st.header("📊 Relatório Mensal")
        # Mantido como no seu código
        # ...

    st.markdown("---")
    st.caption("Sistema de Postagens - Foguete Express 🚀 desenvolvido por RobTech Service")
