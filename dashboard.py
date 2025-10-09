import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from zoneinfo import ZoneInfo
import db

def mostrar_dashboard():
    st.title("📊 Dashboard - Foguete Express")

    postagens = db.listar_postagens()
    if not postagens:
        st.info("Nenhuma postagem cadastrada ainda.")
        return

    df = pd.DataFrame(postagens)

    # Certifica que a coluna 'observacao' existe no DataFrame
    if "observacao" not in df.columns:
        df["observacao"] = ""

    df['id'] = df['id'].astype('int64')

    df["data_postagem"] = pd.to_datetime(
        df["data_postagem"].str.strip(), dayfirst=True, errors="coerce"
    )
    df = df.dropna(subset=["data_postagem"])
    df["data_postagem"] = df["data_postagem"].dt.tz_localize(None)

    filtro = st.selectbox("Período", ["Diário", "Semanal", "Mensal"])
    hoje = datetime.now(ZoneInfo("America/Sao_Paulo")).replace(tzinfo=None)

    if filtro == "Diário":
        dff = df[df["data_postagem"].dt.date == hoje.date()]
    elif filtro == "Semanal":
        dff = df[df["data_postagem"] >= hoje - pd.Timedelta(days=7)]
    else:
        dff = df[df["data_postagem"] >= hoje - pd.Timedelta(days=30)]

    # Certifica que a coluna 'observacao' existe no DataFrame filtrado
    if "observacao" not in dff.columns:
        dff["observacao"] = ""

    st.metric("📬 Total postagens", len(dff))
    st.metric("⌛ Pendentes", len(dff[dff["status_pagamento"] == "Pendente"]))
    st.metric("💰 Valor total", f"R$ {dff['valor'].sum():,.2f}")

    if not dff.empty:
        grouped = dff.groupby("posto").size().reset_index(name="quantidade")
        fig = px.bar(grouped, x="posto", y="quantidade", text="quantidade", color="posto",
                     color_discrete_sequence=["#005CA9", "#FFCC00"])
        fig.update_layout(showlegend=False)
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.pie(dff, names="tipo", title="Distribuição por tipo",
                      color_discrete_sequence=["#005CA9", "#FFCC00", "#003366", "#FFD700"])
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Detalhamento")
    st.dataframe(dff.sort_values("data_postagem", ascending=False)[
        ["id", "posto", "remetente", "codigo", "tipo", "valor", "forma_pagamento", "status_pagamento", "funcionario", "data_postagem", "observacao"]
    ], use_container_width=True)
