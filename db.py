import psycopg
from psycopg.rows import dict_row
import os

# ✅ Lê a URL do banco do ambiente (Render → DATABASE_URL)
DATABASE_URL = os.getenv("DATABASE_URL")

# 🔒 Configuração da conexão (Render exige SSL)
def conectar():
    return psycopg.connect(DATABASE_URL, sslmode="require", row_factory=dict_row)

# 🧱 Cria a tabela de postagens, se não existir
def criar_tabelas():
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS postagens (
                    id SERIAL PRIMARY KEY,
                    titulo TEXT NOT NULL,
                    conteudo TEXT NOT NULL,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()

# ➕ Adiciona uma nova postagem
def adicionar_postagem(titulo, conteudo):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO postagens (titulo, conteudo) VALUES (%s, %s);",
                (titulo, conteudo)
            )
            conn.commit()

# 📜 Retorna todas as postagens (mais recentes primeiro)
def listar_postagens():
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM postagens ORDER BY criado_em DESC;")
            return cur.fetchall()
