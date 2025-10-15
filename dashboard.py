import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import db
import calendar

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
        # Calcula o último domingo
        dias_atras = (hoje.weekday() + 1) % 7  # Domingo = 0
        inicio_semana = hoje - timedelta(days=dias_atras)
        inicio_semana = inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0)
        fim_semana = inicio_semana + timedelta(days=7)
        dff = df[(df["data_postagem"] >= inicio_semana) & (df["data_postagem"] < fim_semana)]
    else:
        primeiro_dia_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        primeiro_dia_mes_seguinte = (primeiro_dia_mes + pd.DateOffset(months=1)).to_pydatetime()
        dff = df[(df["data_postagem"] >= primeiro_dia_mes) & (df["data_postagem"] < primeiro_dia_mes_seguinte)]

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
    st.markdown(f"Total de postagens no período: **{len(dff)}**")
    st.markdown(f"Valor total no período: **R$ {dff['valor'].sum():,.2f}**")
    st.markdown(f"Postagens com Pagamento Pendente: **{len(dff[dff['status_pagamento'] == 'Pendente'])}**")
    st.markdown(f"Valor pendente: **R$ {dff[dff['status_pagamento'] == 'Pendente']['valor'].sum():,.2f}**")
    st.markdown(f"Postagens pagas: **{len(dff[dff['status_pagamento'] == 'Pago'])}**")
    st.markdown(f"Valor pago: **R$ {dff[dff['status_pagamento'] == 'Pago']['valor'].sum():,.2f}**")
    st.markdown("---")
    st.subheader("Postagens com Pagamento Pendente")
    pendentes = dff[dff["status_pagamento"] == "Pendente"].to_dict(orient="records")
    if not pendentes:
        st.info("Nenhuma  Postagem com Pagamento Pendente.")
    else:
        for p in pendentes:
            with st.expander(f"📦 {p['codigo']} | {p['posto']} | R$ {p['valor']:.2f} | {p['data_postagem']}"):
                st.write(f"Remetente: {p['remetente']}")
                st.write(f"Funcionário: {p['funcionario']}")
                st.write(f"Data Postagem: {p['data_postagem']}")
                st.write(f"Tipo: {p['tipo']}")
                st.write(f"Forma de Pagamento: {p['forma_pagamento']}")
                st.write(f"Observação: {p['observacao']}")
                if st.button(f"Marcar como Pago - ID {p['id']}", key=f"pagar_{p['id']}"):
                    db.atualizar_status_pagamento(p['id'], "Pago")
                    st.success("Status atualizado para Pago. Recarregue a página para ver as mudanças.")
                if st.button(f"Deletar Postagem - ID {p['id']}", key=f"deletar_{p['id']}"):
                    db.deletar_postagem(p['id'])
                    st.success("Postagem deletada. Recarregue a página para ver as mudanças.")
                    