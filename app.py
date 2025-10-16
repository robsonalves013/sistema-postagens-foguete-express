import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import time

import db
from dashboard import mostrar_dashboard
from utils import gerar_pdf, gerar_relatorio_mensal, gerar_pdf_guia_visual

def get_brasilia_now():
    return datetime.now(ZoneInfo("America/Sao_Paulo"))

TEMPO_INATIVIDADE = 30 * 60

db.criar_tabelas()

st.set_page_config(page_title="Sistema de Postagens - Foguete Express", layout="wide")

if "ultimo_acesso" not in st.session_state:
    st.session_state["ultimo_acesso"] = time.time()

tempo_agora = time.time()
if st.session_state.get("logado") and (tempo_agora - st.session_state["ultimo_acesso"] > TEMPO_INATIVIDADE):
    st.session_state["logado"] = False
    st.session_state["usuario"] = None
    st.warning("⚠️ Sua sessão expirou por inatividade. Por favor, faça login novamente.")
    st.experimental_rerun()

if st.session_state.get("logado"):
    st.session_state["ultimo_acesso"] = tempo_agora

if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

if not st.session_state["logado"]:
    st.title("📦 Sistema de Postagens Foguete Express - Login")
    with st.form("login_form"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar")
        if entrar:
            user = db.autenticar(usuario, senha)
            if user:
                st.session_state["logado"] = True
                st.session_state["usuario"] = user
                st.success("✅ Login realizado com sucesso!")
                st.experimental_rerun()
            else:
                st.error("❌ Usuário ou senha incorretos.")
    st.stop()

usuario = st.session_state["usuario"]
admin = bool(usuario.get("is_admin", 0))
st.sidebar.title(f"👋 Olá, {usuario['nome']}")
opcoes = ["Cadastrar Postagem", "Listar Postagens", "Lista de Remetentes", "Pagamentos Pendentes", "Guia"]
if admin:
    opcoes += ["Dashboard", "Gerenciar Usuários", "Relatório Mensal", "Fechamento Diário"]
opcao = st.sidebar.radio("Navegação", opcoes)

if st.sidebar.button("🚪 Sair"):
    st.session_state["logado"] = False
    st.session_state["usuario"] = None
    st.experimental_set_query_params()
    st.experimental_rerun()

if opcao == "Dashboard":
    mostrar_dashboard()

elif opcao == "Cadastrar Postagem":
    st.header("📝 Cadastrar Nova Postagem")

    # Busca remetentes cadastrados
    remetentes_cadastrados = [r["nome"] for r in db.listar_remetentes()]
    if not remetentes_cadastrados:
        st.warning("⚠️ Cadastre pelo menos um remetente antes de cadastrar postagens.")
        st.stop()

    with st.form("form_postagem"):
        posto = st.selectbox("Posto", ["Shopping Bolivia", "Hotel Family"])
        remetente = st.selectbox("Remetente", remetentes_cadastrados)
        codigo = st.text_input("Código de Rastreamento")
        tipo = st.selectbox("Tipo", ["PAC", "SEDEX"])
        valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01)
        forma_pagamento = st.selectbox("Forma de Pagamento", ["PIX", "Dinheiro", "Cartão"])
        status_pagamento = st.selectbox("Status do Pagamento", ["Pendente", "Pago"])
        funcionario = st.selectbox("Funcionário", ["Yuri", "Jair"])
        observacao = st.text_area("Observação (opcional)")
        data_postagem = get_brasilia_now().strftime("%d/%m/%Y %H:%M:%S")

        if status_pagamento == "Pago":
            data_pagamento = get_brasilia_now().strftime("%d/%m/%Y %H:%M:%S")
        else:
            data_pagamento = ""

        submit = st.form_submit_button("💾 Cadastrar")

        if submit:
            erros = []
            if not posto:
                erros.append("Posto é obrigatório.")
            if not remetente:
                erros.append("Remetente é obrigatório.")
            if not codigo:
                erros.append("Código de rastreamento é obrigatório.")
            if len(codigo) != 13:
                erros.append("Código de rastreamento deve ter exatamente 13 caracteres.")
            if not tipo:
                erros.append("Tipo é obrigatório.")
            if valor <= 0:
                erros.append("Valor deve ser maior que zero.")
            if not forma_pagamento:
                erros.append("Forma de pagamento é obrigatória.")
            if not status_pagamento:
                erros.append("Status de pagamento é obrigatório.")
            if not funcionario:
                erros.append("Funcionário é obrigatório.")

            if erros:
                for erro in erros:
                    st.error(erro)
            elif db.codigo_existe(codigo):
                st.error("Código de rastreamento já cadastrado no sistema.")
            else:
                dados = (posto, remetente, codigo, tipo, valor, forma_pagamento, status_pagamento,
                         funcionario, data_postagem, data_pagamento, observacao)
                try:
                    db.adicionar_postagem(dados)
                    st.success("✅ Postagem cadastrada com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao cadastrar: {e}")

elif opcao == "Listar Postagens":
    st.header("📋 Lista de Postagens")
    postagens = db.listar_postagens()
    if not postagens:
        st.info("Nenhuma postagem cadastrada.")
    else:
        import pandas as pd

        # Filtro por código de rastreamento
        codigo_filtro = st.text_input("Filtrar por código de rastreamento (opcional)")
        if codigo_filtro:
            postagens = [p for p in postagens if codigo_filtro.lower() in p['codigo'].lower()]
            if not postagens:
                st.warning("Nenhuma postagem encontrada com esse código.")

        df = pd.DataFrame(postagens)
        df['data_postagem'] = pd.to_datetime(df['data_postagem'], dayfirst=True, errors='coerce')
        df["ano"] = df["data_postagem"].dt.year
        df["mes"] = df["data_postagem"].dt.strftime("%m/%Y")

        for ano, grupo_ano in df.groupby("ano"):
            with st.expander(f"📅 Ano: {ano}"):
                meses = sorted(grupo_ano["mes"].unique())
                for mes in meses:
                    expand_mes = st.checkbox(f"📅 Mês: {mes} - {len(grupo_ano[grupo_ano['mes'] == mes])} postagens", key=f"{ano}_{mes}")
                    if expand_mes:
                        grupo_mes = grupo_ano[grupo_ano["mes"] == mes]
                        for _, p in grupo_mes.iterrows():
                            expand_post = st.checkbox(f"📦 {p['codigo']} | {p['posto']} | {p['remetente']}", key=f"post_{p['id']}")
                            if expand_post:
                                st.write(f"**Posto:** {p['posto']}")
                                st.write(f"**Remetente:** {p['remetente']}")
                                st.write(f"**Código:** {p['codigo']}")
                                st.write(f"**Tipo:** {p['tipo']}")
                                st.write(f"**Valor:** R$ {float(p['valor']):.2f}")
                                st.write(f"**Forma Pagamento:** {p['forma_pagamento']}")
                                st.write(f"**Status:** {p['status_pagamento']}")
                                st.write(f"**Funcionário:** {p['funcionario']}")
                                st.write(f"**Data Postagem:** {p['data_postagem'].strftime('%d/%m/%Y %H:%M:%S') if pd.notnull(p['data_postagem']) else ''}")
                                st.write(f"**Data Pagamento:** {p['data_pagamento'] or ''}")
                                st.write(f"**Observação:** {p.get('observacao', '')}")

                                if admin:
                                    st.divider()
                                    st.subheader("✏️ Editar Postagem")
                                    # Corrigido: posto só aceita opções válidas
                                    novo_posto = st.selectbox("Posto", ["Shopping Bolivia", "Hotel Family"],
                                        index=["Shopping Bolivia", "Hotel Family"].index(p['posto']) if p['posto'] in ["Shopping Bolivia", "Hotel Family"] else 0)
                                    novo_remetente = st.text_input("Remetente", p['remetente'])
                                    novo_codigo = st.text_input("Código", p['codigo'])
                                    novo_tipo = st.selectbox("Tipo", ["PAC", "SEDEX"],
                                        index=["PAC", "SEDEX"].index(p['tipo']) if p['tipo'] in ["PAC", "SEDEX"] else 0)
                                    novo_valor = st.number_input("Valor (R$)", value=float(p['valor']))
                                    nova_forma = st.selectbox("Forma Pagamento", ["PIX", "Dinheiro", "Cartão"],
                                        index=["PIX", "Dinheiro", "Cartão"].index(p['forma_pagamento']) if p['forma_pagamento'] in ["PIX", "Dinheiro", "Cartão"] else 0)
                                    novo_status = st.selectbox("Status", ["Pendente", "Pago"],
                                        index=["Pendente", "Pago"].index(p['status_pagamento']) if p['status_pagamento'] in ["Pendente", "Pago"] else 0)
                                    novo_func = st.selectbox("Funcionário", ["Yuri", "Jair"],
                                        index=["Yuri", "Jair"].index(p['funcionario']) if p['funcionario'] in ["Yuri", "Jair"] else 0)
                                    nova_observacao = st.text_area("Observação", p.get('observacao', ''))
                                    if novo_status == "Pago":
                                        nova_data_pag = get_brasilia_now().strftime("%d/%m/%Y %H:%M:%S")
                                    else:
                                        nova_data_pag = ""
                                    salvar = st.form_submit_button("💾 Salvar Alterações")
                                    if salvar:
                                        novos_dados = (
                                            novo_posto, novo_remetente, novo_codigo, novo_tipo, novo_valor,
                                            nova_forma, novo_status, novo_func,
                                            p['data_postagem'], nova_data_pag, nova_observacao
                                        )
                                        try:
                                            db.editar_postagem(p["id"], novos_dados)
                                            st.success("✅ Postagem atualizada com sucesso!")
                                            st.experimental_rerun()
                                        except Exception as e:
                                            st.error(f"Erro ao atualizar: {e}")
                                    if st.button("🗑️ Excluir Postagem", key=f"excluir_{p['id']}"):
                                        try:
                                            db.excluir_postagem(p['id'])
                                            st.success("Postagem excluída.")
                                            st.experimental_rerun()
                                        except Exception as e:
                                            st.error(f"Erro ao excluir: {e}")
                                else:
                                    st.caption("🔒 Somente administradores podem editar/excluir postagens.")



elif opcao == "Lista de Remetentes":
    st.header("📬 Lista de Remetentes")
    with st.form("form_remetente"):
        novo_remetente = st.text_input("Nome do remetente")
        cadastrar = st.form_submit_button("Cadastrar")
        if cadastrar and novo_remetente:
            db.cadastrar_remetente(novo_remetente.strip())
            st.success("Remetente cadastrado com sucesso!")
    remetentes = db.listar_remetentes()
    if not remetentes:
        st.info("Nenhum remetente cadastrado.")
    else:
        df_remet = pd.DataFrame(remetentes)
        st.dataframe(df_remet, use_container_width=True)
        for r in remetentes:
            if st.button(f"🗑️ Excluir {r['nome']}", key=f"exc_rem_{r['id']}"):
                db.excluir_remetente(r['id'])
                st.experimental_rerun()

elif opcao == "Pagamentos Pendentes":
    st.header("💰 Pagamentos Pendentes")
    pendentes = db.listar_postagens_pendentes()
    if not pendentes:
        st.info("Nenhum pagamento pendente.")
    else:
        import pandas as pd
        df = pd.DataFrame(pendentes)
        df["data_postagem"] = pd.to_datetime(df["data_postagem"], dayfirst=True, errors="coerce")
        df["ano"] = df["data_postagem"].dt.year
        df["mes"] = df["data_postagem"].dt.strftime("%m/%Y")

        for ano, grupo_ano in df.groupby("ano"):
            with st.expander(f"📅 Ano: {ano}"):
                meses = sorted(grupo_ano["mes"].unique())
                for mes in meses:
                    expand_mes = st.checkbox(f"📅 Mês: {mes} - {len(grupo_ano[grupo_ano['mes'] == mes])} postagens", key=f"pend_mes_{ano}_{mes}")
                    if expand_mes:
                        grupo_mes = grupo_ano[grupo_ano["mes"] == mes]
                        for _, p in grupo_mes.iterrows():
                            expand_post = st.checkbox(f"📦 {p['codigo']} | {p['posto']} | R$ {p['valor']:.2f} | {p['data_postagem'].strftime('%d/%m/%Y') if pd.notnull(p['data_postagem']) else ''}", key=f"pend_post_{p['id']}")
                            if expand_post:
                                st.write(f"Remetente: {p['remetente']}")
                                st.write(f"Funcionário: {p['funcionario']}")
                                st.write(f"Data Postagem: {p['data_postagem'].strftime('%d/%m/%Y %H:%M:%S') if pd.notnull(p['data_postagem']) else ''}")
                                st.write(f"Observação: {p.get('observacao', '')}")
                                if st.button("✅ Marcar como Pago", key=f"pago_{p['id']}"):
                                    data_atual = get_brasilia_now().strftime("%d/%m/%Y %H:%M:%S")
                                    db.atualizar_pagamento(p['id'], "Pago", data_atual)
                                    st.success("Pagamento marcado como Pago.")
                                    st.experimental_rerun()


elif opcao == "Fechamento Diário":
    st.header("🧾 Fechamento Diário")
    postagens = db.listar_postagens()
    if not postagens:
        st.info("Nenhuma postagem para gerar PDF.")
    else:
        bytes_pdf, nome_pdf = gerar_pdf(postagens)
        st.download_button("📥 Baixar Fechamento Diário (PDF)", data=bytes_pdf, file_name=nome_pdf, mime="application/pdf")

elif opcao == "Guia":
    st.header("📘 Guia de Utilização do Sistema")
    bytes_pdf, nome_pdf = gerar_pdf_guia_visual()
    st.download_button("📥 Baixar Guia de Utilização", data=bytes_pdf, file_name=nome_pdf, mime="application/pdf")

elif opcao == "Gerenciar Usuários" and admin:
    st.header("👥 Gerenciar Usuários")
    st.subheader("Cadastrar Novo Usuário")
    with st.form("cadastro_usuario"):
        nome = st.text_input("Nome Completo")
        usuario_n = st.text_input("Usuário (login)")
        senha = st.text_input("Senha", type="password")
        is_admin = st.checkbox("Administrador")
        criar = st.form_submit_button("Criar Usuário")
        if criar:
            try:
                db.criar_usuario(nome, usuario_n, senha, int(is_admin))
                st.success("Usuário criado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao criar usuário: {e}")
    st.divider()
    st.subheader("Usuários cadastrados:")
    usuarios = db.listar_usuarios()
    if not usuarios:
        st.info("Nenhum usuário cadastrado.")
    else:
        df_users = pd.DataFrame(usuarios)
        st.dataframe(df_users[["id", "nome", "usuario", "is_admin"]], use_container_width=True)
        for u in usuarios:
            with st.expander(f"{u['nome']} ({u['usuario']})"):
                novo_nome = st.text_input("Nome", u['nome'], key=f"nome_{u['id']}")
                novo_admin = st.checkbox("Administrador", value=bool(u['is_admin']), key=f"admin_{u['id']}")
                nova_senha = st.text_input("Nova senha (opcional)", type="password", key=f"senha_{u['id']}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Salvar Alterações", key=f"salvar_{u['id']}"):
                        try:
                            db.atualizar_usuario(u['id'], novo_nome, nova_senha if nova_senha else None, int(novo_admin))
                            st.success("Usuário atualizado.")
                        except Exception as e:
                            st.error(f"Erro ao atualizar: {e}")
                with col2:
                    if st.button("🗑️ Excluir Usuário", key=f"del_{u['id']}"):
                        try:
                            db.excluir_usuario_por_nome(u['usuario'])
                            st.warning("Usuário excluído.")
                        except Exception as e:
                            st.error(f"Erro ao excluir usuário: {e}")

elif opcao == "Relatório Mensal" and admin:
    st.header("📊 Relatório Mensal")
    col1, col2 = st.columns(2)
    with col1:
        mes = st.number_input("Mês", min_value=1, max_value=12, value=get_brasilia_now().month)
    with col2:
        ano = st.number_input("Ano", min_value=2000, max_value=2100, value=get_brasilia_now().year)
    posto = st.selectbox("Posto (opcional)", ["Todos", "Shopping Bolivia", "Hotel Family"])
    tipo = st.selectbox("Tipo de postagem (opcional)", ["Todos", "PAC", "SEDEX"])
    forma = st.selectbox("Forma de pagamento (opcional)", ["Todos", "Dinheiro", "PIX"])
    filtro_posto = None if posto == "Todos" else posto
    filtro_tipo = None if tipo == "Todos" else tipo
    filtro_forma = None if forma == "Todos" else forma
    if st.button("Gerar Relatório"):
        postagens = db.listar_postagens_mensal(mes, ano, filtro_posto, filtro_tipo, filtro_forma)
        if not postagens:
            st.info("❗ Não há postagens para gerar o relatório mensal.")
        else:
            bytes_pdf, nome_pdf = gerar_relatorio_mensal(postagens)
            st.download_button("📥 Baixar Relatório Mensal (PDF)", data=bytes_pdf, file_name=nome_pdf, mime="application/pdf")

st.markdown("---")
st.caption("Sistema de Postagens - Foguete Express 🚀 desenvolvido por RobTech Service")
