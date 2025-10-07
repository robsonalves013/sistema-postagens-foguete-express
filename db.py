import psycopg
from psycopg.rows import dict_row
import os

# Lê a variável de ambiente do Render
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ A variável de ambiente DATABASE_URL não foi encontrada. Configure-a no Render!")

def conectar():
    """Conecta ao PostgreSQL usando a URL completa"""
    # Adiciona sslmode=require se não estiver presente na URL
    if "sslmode=" not in DATABASE_URL:
        dsn = DATABASE_URL + "?sslmode=require"
    else:
        dsn = DATABASE_URL

    return psycopg.connect(dsn, row_factory=dict_row)

def criar_tabelas():
    """Cria a tabela de postagens se não existir"""
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

def adicionar_postagem(titulo, conteudo):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO postagens (titulo, conteudo) VALUES (%s, %s);",
                (titulo, conteudo)
            )
        conn.commit()

def listar_postagens():
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM postagens ORDER BY criado_em DESC;")
            return cur.fetchall()
