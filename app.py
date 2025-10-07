import streamlit as st
import db
from datetime import datetime

# Inicializa tabelas
db.criar_tabelas()

# Configurações da página
st.set_page_config(
    page_title="Sistema de Postagens - Foguete Express 🚀",
    page_icon="🚀",
    layout="centered"
)

# Cabeçalho
st.title("📬 Sistema de Postagens - Foguete Express 🚀")
st.markdown("### Crie, visualize e gerencie suas postagens com facilidade!")
st.divider()

# Formulário de nova postagem
with st.form("nova_postagem"):
    st.subheader("📝 Nova Postagem")
    titulo = st.text_input("Título da postagem:")
    conteudo = st.text_area("Conteúdo da postagem:")
    enviar = st.form_submit_button("Publicar 🚀")

    if enviar:
        if titulo and conteudo:
            db.adicionar_postagem(titulo, conteudo)
            st.success("✅ Postagem publicada com sucesso!")
            st.rerun()
        else:
            st.warning("⚠️ Preencha todos os campos antes de publicar.")

st.divider()

# Lista de postagens
st.subheader("📰 Postagens Recentes")
postagens = db.listar_postagens()
if postagens:
    for p in postagens:
        st.markdown(f"### {p['titulo']}")
        st.markdown(p['conteudo'])
        st.caption(f"🕒 Publicado em {p['criado_em'].strftime('%d/%m/%Y %H:%M')}")
        st.markdown("---")
else:
    st.info("🚀 Nenhuma postagem encontrada ainda. Crie a primeira acima!")

# Rodapé
st.markdown(
    """
    <div style="text-align:center; margin-top: 40px; font-size: 0.9em; color: gray;">
        Sistema de Postagens - <b>Foguete Express 🚀</b> desenvolvido por <b>RobTech Service</b>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("© 2024 RobTech Service. Todos os direitos reservados.")