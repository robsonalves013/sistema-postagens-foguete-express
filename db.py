import os
from psycopg import connect, sql
from psycopg.rows import dict_row
import bcrypt

# ---------- Configurações de Conexão ----------
# Coloque a URL do banco do Render na variável de ambiente DATABASE_URL
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Defina a variável de ambiente DATABASE_URL com a URL do Postgres.")

# ---------- Função de Conexão ----------
def conectar():
    return connect(DATABASE_URL, row_factory=dict_row, autocommit=True)

# ---------- Criar tabelas ----------
def criar_tabelas():
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                usuario TEXT UNIQUE NOT NULL,
                senha BYTEA NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE
            );
            """)
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
                data_postagem TEXT NOT NULL,
                data_pagamento TEXT
            );
            """)

# ---------- Usuários ----------
def criar_usuario(nome, usuario, senha, is_admin=0):
    hashed = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO usuarios (nome, usuario, senha, is_admin) VALUES (%s, %s, %s, %s);",
                (nome, usuario, hashed, bool(is_admin))
            )

def listar_usuarios():
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nome, usuario, is_admin FROM usuarios ORDER BY id;")
            return cur.fetchall()

def autenticar(usuario, senha):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM usuarios WHERE usuario = %s;", (usuario,))
            user = cur.fetchone()
            if user and bcrypt.checkpw(senha.encode("utf-8"), user['senha']):
                return user
            return None

def resetar_senha(usuario, nova_senha):
    hashed = bcrypt.hashpw(nova_senha.encode("utf-8"), bcrypt.gensalt())
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE usuarios SET senha=%s WHERE usuario=%s;", (hashed, usuario))

# ---------- Postagens ----------
def adicionar_postagem(dados):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO postagens 
            (posto, remetente, codigo, tipo, valor, forma_pagamento, status_pagamento, funcionario, data_postagem, data_pagamento)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
            """, dados)

def listar_postagens():
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM postagens ORDER BY id DESC;")
            return cur.fetchall()

def atualizar_pagamento(postagem_id, status_pagamento, data_pagamento):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            UPDATE postagens 
            SET status_pagamento=%s, data_pagamento=%s
            WHERE id=%s;
            """, (status_pagamento, data_pagamento, postagem_id))

def listar_postagens_mensal(mes, ano, filtro_posto=None, filtro_tipo=None, filtro_forma=None):
    query = "SELECT * FROM postagens WHERE EXTRACT(MONTH FROM TO_DATE(data_postagem,'DD/MM/YYYY'))=%s AND EXTRACT(YEAR FROM TO_DATE(data_postagem,'DD/MM/YYYY'))=%s"
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
    query += " ORDER BY id DESC;"

    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()
