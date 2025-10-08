# app.py
import streamlit as st
from datetime import datetime
import db
from utils import gerar_pdf, gerar_relatorio_mensal
from streamlit_autorefresh import st_autorefresh
from dashboard import mostrar_dashboard  # Dashboard modularizado

# ---------------- Inicializa banco ----------------
db.criar_tabelas()
st.set_page_config(page_title="Sistema de Postagens", layout="centered")

# ---------------- Sessão ----------------
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

# ---------------- Tela de Login ----------------
if not st.session_state["logado"]:
    st.title("📦 Sistema de Postagens - Login")
    
    with st.form("login_form"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")
        
        if submitted:
            user = db.autenticar(usuario, senha)
            if user:
                st.session_state["logado"] = True
                st.session_state["usuario"] = user
                st.success("Login realizado com sucesso!")
                  # Força atualização da página
            else:
                st.error("Usuário ou senha incorretos.")

# ---------------- Tela Principal ----------------
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
          # Força atualizar para tela de login

    # ---------------- DASHBOARD ----------------
    if opcao == "Dashboard":
        mostrar_dashboard()

    # ---------------- CADASTRAR POSTAGEM ----------------
    elif opcao == "Cadastrar Postagem":
        st.header("📮 Nova Postagem")
        with st.form("cadastro_postagem"):
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
                dados = (posto, remetente, codigo, tipo, valor, forma_pagamento,
                        status_pagamento, funcionario, data_postagem, data_pagamento)
                try:
                    db.adicionar_postagem(dados)
                    st.success("✅ Postagem cadastrada com sucesso!")
                except ValueError as e:
                    st.error(f"❌ {e}")
                except Exception as e:
                    st.error(f"Erro ao cadastrar postagem: {e}")

                

    # ---------------- LISTAR POSTAGENS ----------------
    elif opcao == "Listar Postagens":
    st.header("📋 Lista de Postagens")
    postagens = db.listar_postagens()
    if not postagens:
        st.info("Nenhuma postagem cadastrada.")
    else:
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

                # Apenas administradores podem editar
                if admin:
                    st.divider()
                    st.subheader("✏️ Editar Postagem")
                    with st.form(f"editar_postagem_{p['id']}"):
                        novo_posto = st.text_input("Posto", p['posto'])
                        novo_remetente = st.text_input("Remetente", p['remetente'])
                        novo_codigo = st.text_input("Código", p['codigo'])
                        novo_tipo = st.selectbox("Tipo", ["Carta", "Encomenda", "Sedex"], index=["Carta", "Encomenda", "Sedex"].index(p['tipo']))
                        novo_valor = st.number_input("Valor (R$)", value=p['valor'], min_value=0.0)
                        nova_forma = st.selectbox("Forma de Pagamento", ["Pix", "Dinheiro", "Cartão"], index=["Pix", "Dinheiro", "Cartão"].index(p['forma_pagamento']))
                        novo_status = st.selectbox("Status Pagamento", ["Pendente", "Pago"], index=["Pendente", "Pago"].index(p['status_pagamento']))
                        novo_funcionario = st.text_input("Funcionário", p['funcionario'])
                        nova_data_postagem = st.date_input("Data Postagem", value=pd.to_datetime(p['data_postagem']).date())
                        nova_data_pagamento = st.date_input("Data Pagamento", value=pd.to_datetime(p['data_pagamento']).date())

                        if st.form_submit_button("💾 Salvar Alterações"):
                            novos_dados = (
                                novo_posto, novo_remetente, novo_codigo, novo_tipo, novo_valor,
                                nova_forma, novo_status, novo_funcionario,
                                str(nova_data_postagem), str(nova_data_pagamento)
                            )
                            try:
                                db.editar_postagem(p['id'], novos_dados)
                                st.success("✅ Postagem atualizada com sucesso!")
                            except Exception as e:
                                st.error(f"Erro ao editar: {e}")
                else:
                    st.caption("🔒 Somente administradores podem editar postagens.")

    # ---------------- PAGAMENTOS PENDENTES ----------------
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
                        

    # ---------------- FECHAMENTO DIÁRIO ----------------
    elif opcao == "Fechamento Diário":
        st.header("🧾 Fechamento Diário")
        postagens = db.listar_postagens()
        if st.button("Gerar PDF"):
            nome_pdf = gerar_pdf(postagens)
            if nome_pdf:
                with open(nome_pdf, "rb") as f:
                    st.download_button("Baixar PDF", f, file_name=nome_pdf)
            else:
                st.info("Nenhuma postagem para gerar PDF.")

    # ---------------- GERENCIAR USUÁRIOS ----------------
    elif opcao == "Gerenciar Usuários" and admin:
        st.header("👥 Gerenciar Usuários")

        # --- Cadastrar Novo Usuário ---
        st.subheader("Cadastrar Novo Usuário")
        with st.form("cadastro_usuario"):
            nome = st.text_input("Nome Completo", key="novo_nome")
            novo_usuario = st.text_input("Usuário (login)", key="novo_usuario")
            nova_senha = st.text_input("Senha", type="password", key="nova_senha")
            is_admin = st.checkbox("Administrador", key="novo_admin")
            if st.form_submit_button("Criar Usuário"):
                try:
                    db.criar_usuario(nome, novo_usuario, nova_senha, int(is_admin))
                    st.success("Usuário criado com sucesso!")
                    
                except Exception as e:
                    st.error(f"Erro ao criar usuário: {e}")

        st.markdown("---")
        # --- Editar / Excluir Usuários ---
        st.subheader("Editar / Excluir Usuários")
        usuarios = db.listar_usuarios()
        for u in usuarios:
            with st.expander(f"👤 {u['nome']} ({u['usuario']})"):
                novo_nome = st.text_input("Nome", u['nome'], key=f"nome_{u['id']}")
                novo_admin = st.checkbox("Administrador", value=bool(u['is_admin']), key=f"admin_{u['id']}")
                nova_senha = st.text_input("Nova senha (opcional)", type="password", key=f"senha_{u['id']}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Salvar Alterações", key=f"salvar_{u['id']}"):
                        db.atualizar_usuario(u['id'], novo_nome, nova_senha if nova_senha else None, int(novo_admin))
                        st.success("Usuário atualizado com sucesso!")
                        
                with col2:
                    if st.button("🗑️ Excluir Usuário", key=f"del_{u['id']}"):
                        db.excluir_usuario(u['id'])
                        st.warning("Usuário excluído com sucesso!")
                        

    # ---------------- RELATÓRIO MENSAL ----------------
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
                nome_pdf = gerar_relatorio_mensal(postagens)
                if nome_pdf:
                    with open(nome_pdf, "rb") as f:
                        st.download_button("Baixar PDF", f, file_name=nome_pdf)
            else:
                st.info("Nenhuma postagem encontrada para os filtros selecionados.")

    st.markdown("---")
    st.caption("Sistema de Postagens - Foguete Express 🚀 desenvolvido por RobTech Service")
