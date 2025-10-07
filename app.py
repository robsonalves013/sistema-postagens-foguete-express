import streamlit as st
from datetime import datetime
import db
from utils import gerar_pdf, gerar_relatorio_mensal

# Inicializa banco
db.criar_tabelas()
st.set_page_config(page_title="Sistema de Postagens", layout="centered")

# ------------------- Sessão -------------------
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
if "recarregar" not in st.session_state:
    st.session_state["recarregar"] = False  # controla atualização da tela

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
            st.session_state["recarregar"] = not st.session_state["recarregar"]
            st.success("Login realizado com sucesso!")
        else:
            st.error("Usuário ou senha incorretos.")

# ----------------- Tela Principal -----------------
else:
    user = st.session_state["usuario"]
    admin = bool(user[4])

    st.sidebar.title("Menu")
    opcoes = ["Cadastrar Postagem", "Listar Postagens", "Fechamento Diário"]
    if admin:
        opcoes.append("Gerenciar Usuários")
        opcoes.append("Relatório Mensal")

    opcao = st.sidebar.radio("Selecione uma opção", opcoes)
    st.sidebar.markdown("---")
    st.sidebar.write(f"👤 {user[1]} ({'Admin' if admin else 'Usuário'})")
    
    # Logout automático
    if st.sidebar.button("Sair"):
        st.session_state["logado"] = False
        st.session_state["usuario"] = None
        st.session_state["recarregar"] = not st.session_state["recarregar"]
        st.success("Logout realizado com sucesso!")

    # -------- CADASTRAR POSTAGEM --------
    if opcao == "Cadastrar Postagem":
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

    # -------- LISTAR POSTAGENS COM EDIÇÃO RÁPIDA --------
    elif opcao == "Listar Postagens":
        st.header("📋 Lista de Postagens")
        postagens = db.listar_postagens()

        if postagens:
            for p in postagens:
                with st.expander(f"📦 {p[3]} | {p[1]} | {p[2]}"):
                    st.write(f"Posto: {p[1]}")
                    st.write(f"Remetente: {p[2]}")
                    st.write(f"Código: {p[3]}")
                    st.write(f"Tipo: {p[4]}")
                    st.write(f"Valor: R$ {p[5]:.2f}")
                    st.write(f"Forma de Pagamento: {p[6]}")
                    st.write(f"Status: {p[7]}")
                    st.write(f"Funcionário: {p[8]}")
                    st.write(f"Data Postagem: {p[9]}")
                    st.write(f"Data Pagamento: {p[10]}")

                    # Atualização de pagamento
                    if p[7] == "Pendente":
                        st.markdown("**Atualizar Pagamento**")
                        novo_status = st.selectbox("Status", ["Pendente", "Pago"], key=f"status_{p[0]}")
                        nova_data = st.date_input("Data Pagamento", value=datetime.now(), key=f"data_{p[0]}")
                        if st.button("Salvar Alterações", key=f"btn_{p[0]}"):
                            db.atualizar_pagamento(p[0], novo_status, nova_data.strftime("%d/%m/%Y"))
                            st.success("Pagamento atualizado com sucesso!")

        else:
            st.info("Nenhuma postagem cadastrada.")

    # -------- FECHAMENTO DIÁRIO --------
    elif opcao == "Fechamento Diário":
        st.header("🧾 Fechamento Diário")
        postagens = db.listar_postagens()
        if st.button("Gerar PDF"):
            gerar_pdf(postagens)
            with open("fechamento.pdf", "rb") as f:
                st.download_button("Baixar PDF", f, file_name="fechamento.pdf")
        st.info("O relatório incluirá todas as postagens do dia.")

    # -------- GERENCIAR USUÁRIOS --------
    elif opcao == "Gerenciar Usuários" and admin:
        st.header("👥 Gerenciar Usuários")
        st.subheader("Cadastrar Novo Usuário")
        nome = st.text_input("Nome Completo")
        novo_usuario = st.text_input("Usuário (login)")
        nova_senha = st.text_input("Senha", type="password")
        is_admin = st.checkbox("Administrador")

        if st.button("Criar Usuário"):
            try:
                db.criar_usuario(nome, novo_usuario, nova_senha, int(is_admin))
                st.success("Usuário criado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao criar usuário: {e}")

        st.markdown("---")
        st.subheader("Usuários Cadastrados")
        usuarios = db.listar_usuarios()
        for u in usuarios:
            tipo = "Admin" if u[3] else "Usuário"
            st.write(f"👤 {u[1]} ({u[2]}) - {tipo}")

    # -------- RELATÓRIO MENSAL --------
    elif opcao == "Relatório Mensal" and admin:
        st.header("📊 Relatório Mensal")
        col1, col2 = st.columns(2)
        with col1:
            mes = st.number_input("Mês", min_value=1, max_value=12, value=datetime.now().month)
        with col2:
            ano = st.number_input("Ano", min_value=2000, max_value=2100, value=datetime.now().year)

        posto = st.selectbox("Posto (opcional)", ["Todos", "Shopping Bolivia", "Hotel Family"])
        tipo = st.selectbox("Tipo de postagem (opcional)", ["Todos", "PAC", "SEDEX"])
        forma = st.selectbox("Forma de pagamento (opcional)", ["Todos", "Dinheiro", "PIX"])

        filtro_posto = None if posto == "Todos" else posto
        filtro_tipo = None if tipo == "Todos" else tipo
        filtro_forma = None if forma == "Todos" else forma

        if st.button("Gerar Relatório"):
            postagens = db.listar_postagens_mensal(mes, ano, filtro_posto, filtro_tipo, filtro_forma)
            if postagens:
                gerar_relatorio_mensal(postagens)
                with open("relatorio_mensal.pdf", "rb") as f:
                    st.download_button("Baixar PDF", f, file_name="relatorio_mensal.pdf")
            else:
                st.warning("Nenhuma postagem encontrada para o filtro selecionado.")

    st.markdown("---")
    st.caption("Sistema desenvolvido por RobTechService © 2025")
    st.caption("Versão 1.0.0")