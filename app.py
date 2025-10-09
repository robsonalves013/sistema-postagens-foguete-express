import streamlit as st
import pandas as pd
from datetime import datetime

import db
from dashboard import mostrar_dashboard
from guia_visual import gerar_pdf_guia_atendente
from utils import (
    gerar_pdf,
    gerar_relatorio_mensal,
)


# ---------------- INICIALIZAÇÃO ----------------
db.criar_tabelas()
st.set_page_config(page_title="Sistema de Postagens", layout="wide")

# ---------------- SESSÃO ----------------
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

# ---------------- LOGIN ----------------
if not st.session_state["logado"]:
    st.title("📦 Sistema de Postagens Foguete Express - Login")
    with st.form("login_form"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        login_btn = st.form_submit_button("Entrar")

        if login_btn:
            user = db.autenticar(usuario, senha)
            if user:
                st.session_state["logado"] = True
                st.session_state["usuario"] = user
                st.success("✅ Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("❌ Usuário ou senha incorretos.")
    st.stop()

# ---------------- MENU LATERAL ----------------
usuario = st.session_state["usuario"]
admin = bool(usuario.get("is_admin", 0))

st.sidebar.title(f"👋 Olá, {usuario['nome']}")
opcoes = [
    "Dashboard",
    "Cadastrar Postagem",
    "Listar Postagens",
    "Pagamentos Pendentes",
    "Fechamento Diário",
    "Guia"
]
if admin:
    opcoes.extend(["Gerenciar Usuários", "Relatório Mensal"])

opcao = st.sidebar.radio("Navegação", opcoes)

if st.sidebar.button("🚪 Sair"):
    st.session_state["logado"] = False
    st.session_state["usuario"] = None
    st.rerun()

# ---------------- DASHBOARD ----------------
if opcao == "Dashboard":
    mostrar_dashboard()

# ---------------- CADASTRAR POSTAGEM ----------------
elif opcao == "Cadastrar Postagem":
    st.header("📝 Cadastrar Nova Postagem")

    with st.form("form_postagem"):
        posto = st.selectbox("Posto", ["Shopping Bolivia", "Hotel Family"])
        remetente = st.text_input("Remetente")
        codigo = st.text_input("Código de Rastreamento")

        tipo = st.selectbox("Tipo", ["PAC", "SEDEX"])
        valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01)

        forma_pagamento = st.selectbox("Forma de Pagamento", ["PIX", "Dinheiro", "Cartão"])
        status_pagamento = st.selectbox("Status do Pagamento", ["Pendente", "Pago"])
        funcionario = st.selectbox("Funcionário", ["Yuri", "Jair"])

        data_postagem = st.date_input("Data da Postagem", datetime.today())

        # Data de pagamento apenas se pago
        if status_pagamento == "Pago":
            data_pagamento = st.date_input("Data do Pagamento", datetime.today())
        else:
            data_pagamento = None

        cadastrar_btn = st.form_submit_button("💾 Cadastrar")

        if cadastrar_btn:
            if db.codigo_existe(codigo):
                st.error("❌ Código de rastreio já cadastrado.")
            else:
                dados = (
                    posto,
                    remetente,
                    codigo,
                    tipo,
                    valor,
                    forma_pagamento,
                    status_pagamento,
                    funcionario,
                    data_postagem.strftime("%d/%m/%Y"),
                    data_pagamento.strftime("%d/%m/%Y") if data_pagamento else ""
                )
                db.inserir_postagem(dados)
                st.success("✅ Postagem cadastrada com sucesso!")

# ---------------- LISTAR POSTAGENS ----------------
elif opcao == "Listar Postagens":
    st.header("📋 Lista de Postagens")
    postagens = db.listar_postagens()

    if not postagens:
        st.info("Nenhuma postagem cadastrada.")
    else:
        for p in postagens:
            with st.expander(f"📦 {p['codigo']} | {p['posto']} | {p['remetente']}"):
                st.write(f"**Posto:** {p['posto']}")
                st.write(f"**Remetente:** {p['remetente']}")
                st.write(f"**Código:** {p['codigo']}")
                st.write(f"**Tipo:** {p['tipo']}")
                st.write(f"**Valor:** R$ {p['valor']:.2f}")
                st.write(f"**Forma Pagamento:** {p['forma_pagamento']}")
                st.write(f"**Status:** {p['status_pagamento']}")
                st.write(f"**Funcionário:** {p['funcionario']}")
                st.write(f"**Data Postagem:** {p['data_postagem']}")
                st.write(f"**Data Pagamento:** {p['data_pagamento'] or ''}")

                if admin:
                    st.divider()
                    with st.form(f"editar_{p['id']}"):
                        novo_posto = st.text_input("Posto", p['posto'])
                        novo_remetente = st.text_input("Remetente", p['remetente'])
                        novo_codigo = st.text_input("Código", p['codigo'])
                        novo_tipo = st.selectbox("Tipo", ["PAC", "SEDEX"], index=0 if p['tipo'] == "PAC" else 1)
                        novo_valor = st.number_input("Valor (R$)", value=p['valor'])
                        nova_forma = st.selectbox("Forma Pagamento", ["PIX", "Dinheiro", "Cartão"], index=0)
                        novo_status = st.selectbox("Status", ["Pendente", "Pago"], index=0 if p['status_pagamento'] == "Pendente" else 1)
                        novo_funcionario = st.selectbox("Funcionário", ["Yuri", "Jair"], index=0 if p['funcionario'] == "Yuri" else 1)
                        nova_data_postagem = st.date_input("Data Postagem", pd.to_datetime(p['data_postagem'], dayfirst=True).date())

                        if novo_status == "Pago":
                            nova_data_pagamento = st.date_input(
                                "Data Pagamento",
                                pd.to_datetime(p['data_pagamento'], dayfirst=True).date() if p['data_pagamento'] else datetime.today()
                            )
                        else:
                            nova_data_pagamento = None

                        if st.form_submit_button("💾 Salvar Alterações"):
                            novos_dados = (
                                novo_posto,
                                novo_remetente,
                                novo_codigo,
                                novo_tipo,
                                novo_valor,
                                nova_forma,
                                novo_status,
                                novo_funcionario,
                                nova_data_postagem.strftime("%d/%m/%Y"),
                                nova_data_pagamento.strftime("%d/%m/%Y") if nova_data_pagamento else ""
                            )
                            db.editar_postagem(p["id"], novos_dados)
                            st.success("✅ Postagem atualizada com sucesso!")

                    if st.button("🗑️ Excluir Postagem", key=f"excluir_{p['id']}"):
                        db.excluir_postagem(p['id'])
                        st.success(f"Postagem {p['codigo']} excluída com sucesso!")
                        st.rerun()
                else:
                    st.caption("🔒 Somente administradores podem editar/excluir postagens.")

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
                    st.rerun()

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

# ---------------- GUIA ----------------
if opcao == "Guia":
    st.header("📘 Guia de Utilização do Sistema")
    st.markdown("Clique no botão abaixo para gerar e baixar o guia:")

    if st.button("📄 Gerar Guia de Utilização"):
        pdf_file = gerar_pdf_guia_visual()
        st.download_button(
            label="⬇️ Baixar Guia de Utilização",
            data=pdf_file,
            file_name="guia_utilizacao.pdf",
            mime="application/pdf"
        )

# ---------------------- GERENCIAR USUÁRIOS ----------------------
elif opcao == "Gerenciar Usuários":
    st.header("👥 Gerenciar Usuários")

    usuarios = db.listar_usuarios()

    # Exibe a lista de usuários existentes
    if usuarios.empty:
        st.info("Nenhum usuário cadastrado ainda.")
    else:
        st.subheader("Usuários cadastrados:")
        st.dataframe(usuarios[["id", "nome", "usuario", "nivel"]])

    st.divider()

    st.subheader("Cadastrar Novo Usuário")

    with st.form("cadastro_usuario"):
        nome = st.text_input("Nome completo:")
        usuario = st.text_input("Nome de usuário (login):")
        senha = st.text_input("Senha:", type="password")
        nivel = st.selectbox("Nível de acesso:", ["atendente", "admin"])

        submitted = st.form_submit_button("💾 Cadastrar Usuário")

        if submitted:
            if nome and usuario and senha:
                sucesso = db.cadastrar_usuario(nome, usuario, senha, nivel)
                if sucesso:
                    st.success(f"Usuário '{usuario}' cadastrado com sucesso!")
                else:
                    st.error("Erro: nome de usuário já existe.")
            else:
                st.warning("Preencha todos os campos antes de cadastrar.")

    st.divider()

    st.subheader("Excluir Usuário")
    usuarios_lista = db.listar_usuarios()

    if not usuarios_lista.empty:
        usuario_excluir = st.selectbox(
            "Selecione o usuário para excluir:",
            usuarios_lista["usuario"].tolist()
        )

        if st.button("🗑️ Excluir Usuário"):
            if db.excluir_usuario_por_nome(usuario_excluir):
                st.success(f"Usuário '{usuario_excluir}' excluído com sucesso!")
            else:
                st.error("Erro ao excluir usuário.")
    else:
        st.info("Nenhum usuário disponível para exclusão.")


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
    forma = st.selectbox("Forma de pagamento (opcional)", ["Todos", "Dinheiro", "PIX", "Cartão"])

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
