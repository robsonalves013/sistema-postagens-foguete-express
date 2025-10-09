# dashboard.py
import streamlit as st
import pandas as pd
from datetime import datetime
import db

def mostrar_dashboard():
    st.header("📊 Dashboard - Sistema de Postagens Foguete Express")

    # Carregar todas as postagens
    postagens = db.listar_postagens()
    if not postagens:
        st.info("Nenhuma postagem registrada ainda.")
        return

    # Converter para DataFrame para facilitar manipulação
    df = pd.DataFrame(postagens)

    # Converter valores numéricos e datas
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0.0)
    df['data_postagem'] = pd.to_datetime(df['data_postagem'], format='%d/%m/%Y', errors='coerce')

    # ---------------- Métricas Gerais ----------------
    total_postagens = len(df)
    total_valor = df['valor'].sum()
    total_pago = df[df['status_pagamento'] == "Pago"]['valor'].sum()
    total_pendente = df[df['status_pagamento'] == "Pendente"]['valor'].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Total Postagens", total_postagens)
    col2.metric("💰 Valor Total (R$)", f"{total_valor:.2f}")
    col3.metric("✅ Valor Pago (R$)", f"{total_pago:.2f}")
    col4.metric("⏳ Valor Pendente (R$)", f"{total_pendente:.2f}")

    st.markdown("---")

    # ---------------- Gráficos ----------------
    st.subheader("📈 Postagens por Status")
    status_counts = df['status_pagamento'].value_counts()
    st.bar_chart(status_counts)

    st.subheader("🏢 Postagens por Posto")
    posto_counts = df['posto'].value_counts()
    st.bar_chart(posto_counts)

    st.subheader("👷 Postagens por Funcionário")
    if 'funcionario' in df.columns:
        funcionario_counts = df['funcionario'].value_counts()
        st.bar_chart(funcionario_counts)

    # ---------------- Postagens Recentes ----------------
    st.subheader("🕒 Últimas Postagens")
    df_recentes = df.sort_values(by='data_postagem', ascending=False).head(10)
    st.dataframe(df_recentes[['codigo', 'posto', 'remetente', 'tipo', 'valor', 'forma_pagamento', 'status_pagamento', 'funcionario', 'data_postagem', 'data_pagamento']])
