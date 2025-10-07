import os
import psycopg
from psycopg.rows import dict_row
from datetime import datetime
import bcrypt

# ------------------- CONFIGURAÇÃO DO BANCO -------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ A variável de ambiente DATABASE_URL não está definida no Render!")

# Conecta ao banco de dados
def conectar():
    """
    Conecta ao PostgreSQL usando a URL completa do Render.
    Retorna conexão com row_factory dict_row.
    """
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

# ------------------- TABELAS -------------------

def criar_tabelas():
    """Cria tabelas principais do sistema caso não existam"""
    with conectar() as conn:
        with conn.cursor() as cur:
            # Tabela de usuários
            cur.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    nome TEXT NOT NULL,
                    usuario TEXT UNIQUE NOT NULL,
                    senha BYTEA NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE
                );
            """)
            # Tabela de postagens
            cur.execute("""
                CREATE TABLE IF NOT EXISTS postagens (
                    id SERIAL PRIMARY KEY,
                    posto TEXT NOT NULL,
                    remetente TEXT NOT NULL,
                    codigo TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    valor NUMERIC NOT NULL,
                    forma_pagamento TEXT NOT NULL,
                    status_pagamento TEXT NOT NULL,
                    funcionario TEXT NOT NULL,
                    data_postagem DATE NOT NULL,
                    data_pagamento DATE
                );
            """)
        conn.commit()

# ------------------- USUÁRIOS -------------------

def criar_usuario(nome, usuario, senha, is_admin=0):
    hashed = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO usuarios (nome, usuario, senha, is_admin)
                VALUES (%s, %s, %s, %s)
            """, (nome, usuario, hashed, bool(is_admin)))
        conn.commit()

def autenticar(usuario, senha):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM usuarios WHERE usuario=%s", (usuario,))
            user = cur.fetchone()
            if user and bcrypt.checkpw(senha.encode("utf-8"), user["senha"]):
                return user
    return None

def listar_usuarios():
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM usuarios ORDER BY nome ASC")
            return cur.fetchall()

def resetar_senha(usuario, nova_senha):
    hashed = bcrypt.hashpw(nova_senha.encode("utf-8"), bcrypt.gensalt())
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE usuarios SET senha=%s WHERE usuario=%s", (hashed, usuario))
        conn.commit()

# ------------------- POSTAGENS -------------------

def adicionar_postagem(dados):
    """
    dados = (
        posto, remetente, codigo, tipo, valor,
        forma_pagamento, status_pagamento, funcionario,
        data_postagem, data_pagamento
    )
    """
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO postagens (
                    posto, remetente, codigo, tipo, valor,
                    forma_pagamento, status_pagamento, funcionario,
                    data_postagem, data_pagamento
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, dados)
        conn.commit()

def listar_postagens():
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM postagens ORDER BY data_postagem DESC, id DESC")
            return cur.fetchall()

def atualizar_pagamento(postagem_id, status_pagamento, data_pagamento):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE postagens
                SET status_pagamento=%s, data_pagamento=%s
                WHERE id=%s
            """, (status_pagamento, data_pagamento, postagem_id))
        conn.commit()

def listar_postagens_mensal(mes, ano, posto=None, tipo=None, forma=None):
    query = "SELECT * FROM postagens WHERE EXTRACT(MONTH FROM data_postagem)=%s AND EXTRACT(YEAR FROM data_postagem)=%s"
    params = [mes, ano]

    if posto:
        query += " AND posto=%s"
        params.append(posto)
    if tipo:
        query += " AND tipo=%s"
        params.append(tipo)
    if forma:
        query += " AND forma_pagamento=%s"
        params.append(forma)

    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()
