# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import db  # Importa suas funções de banco de dados

# ------------------- Estilo visual -------------------
st.markdown("""
    <style>
        /* Background da página */
        .main {
            background-color: #f0f4f8;
        }
        .stApp {
            background-color: #f0f4f8;
        }

        /* Cabeçalhos */
        h1, h2, h3 {
            color: #005CA9;
        }

        /* Radio buttons e selects */
        .css-1d391kg, .css-18ni7ap {
            background-color: #FFCC00 !important;
            color: black !important;
        }

        /* Botões */
        .stButton>button {
            background-color: #005CA9;
            color: white;
            border-radius: 8px;
            border: none;
        }
        .stButton>button:hover {
            background-color: #004080;
        }

        /* Tabela */
        .stDataFrame table {
            border: 1px solid #ddd;
        }
        .stDataFrame th {
            background-color: #005CA9;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------- Funções auxiliares -------------------
def carregar_postagens():
    dados = db.listar_postagens()
    if not dados:
        return pd.DataFrame(columns=[
            "id", "posto", "remetente", "codigo", "tipo", "valor",
            "forma_pagamento", "status_pagamento", "funcionario",
            "data_postagem", "data_pagamento"
        ])
    df = pd.DataFrame(dados)
    df["data_postagem"] = pd.to_datetime(df["data_postagem"], format="%d/%m/%Y", errors="coerce")
    return df

def filtrar_periodo(df, filtro):
    """Filtra DataFrame por dia, semana ou mês"""
    hoje = datetime.now()
    if filtro == "Diário":
        return df[df["data_postagem"].dt.date == hoje.date()]
    elif filtro == "Semanal":
        semana_atual = hoje.isocalendar().week
        return df[df["data_postagem"].dt.isocalendar().week == semana_atual]
    elif filtro == "Mensal":
        return df[
            (df["data_postagem"].dt.month == hoje.month) &
            (df["data_postagem"].dt.year == hoje.year)
        ]
    return df

# ------------------- Interface principal -------------------
def mostrar_dashboard():
    st.title("📦 Painel de Controle - Correios")
    st.markdown("Monitoramento de postagens por posto e tipo de serviço")

    # Filtro de período
    filtro_periodo = st.radio(
        "Selecione o período:",
        ["Diário", "Semanal", "Mensal"],
        horizontal=True
    )

    df = carregar_postagens()
    if df.empty:
        st.warning("Nenhuma postagem registrada ainda.")
        return

    df_filtrado = filtrar_periodo(df, filtro_periodo)

    # ---------------- Estatísticas principais ----------------
    total_postagens = len(df_filtrado)
    total_valor = df_filtrado["valor"].sum()
    total_postos = df_filtrado["posto"].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("📬 Total de Postagens", total_postagens)
    col2.metric("💰 Valor Total", f"R$ {total_valor:,.2f}")
    col3.metric("🏢 Postos Ativos", total_postos)

    # ---------------- Gráfico por posto ----------------
    st.subheader("📊 Postagens por Posto")
    if not df_filtrado.empty:
        graf1 = px.bar(
            df_filtrado.groupby("posto").size().reset_index(name="quantidade"),
            x="posto",
            y="quantidade",
            text="quantidade",
            color="posto",
            color_discrete_sequence=["#005CA9", "#FFCC00", "#FFD700", "#003366"]
        )
        graf1.update_traces(textposition="outside")
        graf1.update_layout(showlegend=False)
        st.plotly_chart(graf1, use_container_width=True)

    # ---------------- Gráfico por tipo ----------------
    st.subheader("📦 Tipos de Postagens")
    if not df_filtrado.empty:
        graf2 = px.pie(
            df_filtrado,
            names="tipo",
            title="Distribuição por Tipo de Postagem",
            color_discrete_sequence=["#005CA9", "#FFCC00", "#FFD700", "#003366"]
        )
        st.plotly_chart(graf2, use_container_width=True)

    # ---------------- Tabela detalhada ----------------
    st.subheader("📋 Detalhes das Postagens")
    st.dataframe(df_filtrado.sort_values("data_postagem", ascending=False))

    st.markdown("---")
    st.caption("📮 Sistema Foguete Express - Dashboard © 2025")
