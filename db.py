# db.py
import psycopg
from psycopg.rows import dict_row
import bcrypt
import os
from datetime import datetime

# ------------------- Configurações do Banco -------------------
# Substitua pelo DATABASE_URL do Render
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://usuario:senha@host:porta/banco")

# ------------------- Conexão -------------------
def conectar():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row, sslmode="require")

# ------------------- Criação de tabelas -------------------
def criar_tabelas():
    with conectar() as conn:
        with conn.cursor() as cur:
            # Usuários
            cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                usuario TEXT UNIQUE NOT NULL,
                senha BYTEA NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE
            )
            """)
            # Postagens
            cur.execute("""
            CREATE TABLE IF NOT EXISTS postagens (
                id SERIAL PRIMARY KEY,
                posto TEXT,
                remetente TEXT,
                codigo TEXT,
                tipo TEXT,
                valor NUMERIC,
                forma_pagamento TEXT,
                status_pagamento TEXT,
                funcionario TEXT,
                data_postagem TEXT,
                data_pagamento TEXT
            )
            """)
        conn.commit()

# ------------------- Usuários -------------------
def criar_usuario(nome, usuario, senha, is_admin=False):
    senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO usuarios (nome, usuario, senha, is_admin)
            VALUES (%s, %s, %s, %s)
            """, (nome, usuario, senha_hash, is_admin))
        conn.commit()

def autenticar(usuario, senha):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM usuarios WHERE usuario=%s", (usuario,))
            user = cur.fetchone()
            if user and bcrypt.checkpw(senha.encode("utf-8"), user['senha']):
                return user
    return None

def listar_usuarios():
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM usuarios ORDER BY id")
            return cur.fetchall()

def resetar_senha(usuario, nova_senha):
    nova_hash = bcrypt.hashpw(nova_senha.encode("utf-8"), bcrypt.gensalt())
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE usuarios SET senha=%s WHERE usuario=%s", (nova_hash, usuario))
        conn.commit()

# ------------------- Postagens -------------------
def adicionar_postagem(dados):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO postagens
            (posto, remetente, codigo, tipo, valor, forma_pagamento, status_pagamento, funcionario, data_postagem, data_pagamento)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, dados)
        conn.commit()

def listar_postagens():
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM postagens ORDER BY id DESC")
            return cur.fetchall()

def atualizar_pagamento(postagem_id, status, data_pagamento):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            UPDATE postagens
            SET status_pagamento=%s, data_pagamento=%s
            WHERE id=%s
            """, (status, data_pagamento, postagem_id))
        conn.commit()

def listar_postagens_mensal(mes, ano, filtro_posto=None, filtro_tipo=None, filtro_forma=None):
    with conectar() as conn:
        with conn.cursor() as cur:
            query = "SELECT * FROM postagens WHERE EXTRACT(MONTH FROM TO_DATE(data_postagem, 'DD/MM/YYYY')) = %s AND EXTRACT(YEAR FROM TO_DATE(data_postagem, 'DD/MM/YYYY')) = %s"
            params = [mes, ano]
            if filtro_posto:
                query += " AND posto=%s"
                params.append(filtro_posto)
            if filtro_tipo:
                query += " AND tipo=%s"
                params.append(filtro_tipo)
            if filtro_forma:
                query += " AND forma_pagamento=%s"
                params.append(filtro_forma)
            query += " ORDER BY id DESC"
            cur.execute(query, params)
            return cur.fetchall()
