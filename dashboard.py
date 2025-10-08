# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import db  # Importa suas funções de banco de dados

# ------------------- Funções auxiliares -------------------
def carregar_postagens():
    """Carrega todas as postagens do banco e retorna como DataFrame"""
    dados = db.listar_postagens()
    if not dados:
        return pd.DataFrame(columns=[
            "id", "posto", "remetente", "codigo", "tipo", "valor",
            "forma_pagamento", "status_pagamento", "funcionario",
            "data_postagem", "data_pagamento"
        ])
    df = pd.DataFrame(dados)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
    df["data_postagem"] = pd.to_datetime(df["data_postagem"], format="%d/%m/%Y", errors="coerce")
    df["data_pagamento"] = pd.to_datetime(df["data_pagamento"], format="%d/%m/%Y", errors="coerce", exact=False)
    return df

def filtrar_periodo(df, filtro):
    """Filtra DataFrame por dia, semana ou mês"""
    hoje = datetime.now()
    if filtro == "Diário":
        df = df[df["data_postagem"].dt.date == hoje.date()]
    elif filtro == "Semanal":
        semana_atual = hoje.isocalendar().week
        df = df[df["data_postagem"].dt.isocalendar().week == semana_atual]
    elif filtro == "Mensal":
        df = df[(df["data_postagem"].dt.month == hoje.month) & (df["data_postagem"].dt.year == hoje.year)]
    return df

def filtrar_postos_tipos(df, posto=None, tipo=None):
    """Filtra DataFrame por posto e tipo de postagem"""
    if posto and posto != "Todos":
        df = df[df["posto"] == posto]
    if tipo and tipo != "Todos":
        df = df[df["tipo"] == tipo]
    return df

# ------------------- Interface do Dashboard -------------------
def mostrar_dashboard():
    # ------------------- Estilo visual -------------------
    st.markdown("""
        <style>
            /* Cores dos Correios */
            .main { background-color: #fdfdfd; }
            .stApp { background-color: #fdfdfd; }
            h1, h2, h3 { color: #005CA9; }
            .stButton>button { background-color: #005CA9; color: white; border-radius: 8px; border: none; }
            .stButton>button:hover { background-color: #004080; }
        </style>
    """, unsafe_allow_html=True)

    st.title("📦 Painel de Controle - Correios")
    st.markdown("Monitoramento de postagens por posto, tipo de serviço e pagamentos")

    # ------------------- Seleção de período e filtros -------------------
    filtro_periodo = st.radio("Período:", ["Diário", "Semanal", "Mensal"], horizontal=True)
    posto_filtro = st.selectbox("Posto:", ["Todos", "Shopping Bolivia", "Hotel Family"])
    tipo_filtro = st.selectbox("Tipo de Postagem:", ["Todos", "PAC", "SEDEX"])

    df = carregar_postagens()
    if df.empty:
        st.warning("Nenhuma postagem registrada ainda.")
        return

    df = filtrar_periodo(df, filtro_periodo)
    df = filtrar_postos_tipos(df, posto_filtro, tipo_filtro)

    # ---------------- Estatísticas principais ----------------
    total_postagens = len(df)
    total_valor = df["valor"].sum()
    total_postos = df["posto"].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("📬 Total de Postagens", total_postagens)
    col2.metric("💰 Valor Total", f"R$ {total_valor:,.2f}")
    col3.metric("🏢 Postos Ativos", total_postos)

    # ---------------- Gráfico por posto ----------------
    st.subheader("📊 Postagens por Posto")
    if not df.empty:
        graf1 = px.bar(
            df.groupby("posto").size().reset_index(name="quantidade"),
            x="posto", y="quantidade", text="quantidade",
            color="posto", color_discrete_sequence=["#005CA9", "#FFCC00"]
        )
        graf1.update_traces(textposition="outside")
        graf1.update_layout(showlegend=False)
        st.plotly_chart(graf1, use_container_width=True)

    # ---------------- Gráfico por tipo ----------------
    st.subheader("📦 Tipos de Postagens")
    if not df.empty:
        graf2 = px.pie(
            df, names="tipo", title="Distribuição por Tipo de Postagem",
            color_discrete_sequence=["#005CA9", "#FFCC00", "#FFD700", "#003366"]
        )
        st.plotly_chart(graf2, use_container_width=True)

    # ---------------- Pagamentos Pendentes ----------------
    st.subheader("💰 Pagamentos Pendentes")
    pendentes = df[df["status_pagamento"] == "Pendente"]
    if pendentes.empty:
        st.info("Nenhum pagamento pendente.")
    else:
        for _, p in pendentes.iterrows():
            with st.expander(f"📦 {p['codigo']} | {p['posto']} | R$ {p['valor']:.2f}"):
                st.write(f"Remetente: {p['remetente']}")
                st.write(f"Funcionário: {p['funcionario']}")
                st.write(f"Data Postagem: {p['data_postagem'].strftime('%d/%m/%Y')}")
                if st.button("✅ Marcar como Pago", key=f"pago_{p['id']}"):
                    data_atual = datetime.now().strftime("%d/%m/%Y")
                    db.atualizar_pagamento(p['id'], "Pago", data_atual)
                    st.success(f"Pagamento da postagem {p['codigo']} marcado como pago em {data_atual}!")
                    st.experimental_rerun()

    # ---------------- Tabela detalhada ----------------
    st.subheader("📋 Detalhes das Postagens")
    st.dataframe(df.sort_values("data_postagem", ascending=False))

    st.markdown("---")
    st.caption("📮 Sistema Foguete Express - Dashboard © 2025")

# Permite teste isolado
if __name__ == "__main__":
    mostrar_dashboard()
