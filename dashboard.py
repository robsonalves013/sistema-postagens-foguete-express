# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import db

def mostrar_dashboard():
    st.title("📊 Dashboard - Foguete Express")

    postagens = db.listar_postagens()
    if not postagens:
        st.info("Nenhuma postagem cadastrada ainda.")
        return

    df = pd.DataFrame(postagens)
    # Converter data_postagem para datetime, pode estar em vários formatos -> tenta vários
    df["data_postagem"] = pd.to_datetime(df["data_postagem"], format="%d/%m/%Y %H:%M:%S", errors="coerce")
    # Se houver strings sem hora, tenta formato curto
    df["data_postagem"] = df["data_postagem"].fillna(pd.to_datetime(df["data_postagem"].astype(str), errors="coerce"))

    filtro = st.radio("Período:", ["Diário", "Semanal", "Mensal"], horizontal=True)
    hoje = datetime.now()
    if filtro == "Diário":
        dff = df[df["data_postagem"].dt.date == hoje.date()]
    elif filtro == "Semanal":
        semana = hoje.isocalendar().week
        dff = df[df["data_postagem"].dt.isocalendar().week == semana]
    else:
        dff = df[(df["data_postagem"].dt.month == hoje.month) & (df["data_postagem"].dt.year == hoje.year)]

    st.metric("📬 Total postagens", len(dff))
    st.metric("⌛ Pendentes", len(dff[dff["status_pagamento"] == "Pendente"]))
    st.metric("💰 Valor total", f"R$ {dff['valor'].sum():,.2f}")

    # Gráfico por posto
    if not dff.empty:
        grouped = dff.groupby("posto").size().reset_index(name="quantidade")
        fig = px.bar(grouped, x="posto", y="quantidade", text="quantidade", color="posto",
                     color_discrete_sequence=["#005CA9", "#FFCC00"])
        fig.update_layout(showlegend=False)
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

        # Pizza por tipo
        fig2 = px.pie(dff, names="tipo", title="Distribuição por tipo",
                      color_discrete_sequence=["#005CA9", "#FFCC00", "#003366", "#FFD700"])
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Detalhamento")
        st.dataframe(dff.sort_values("data_postagem", ascending=False), use_container_width=True)
