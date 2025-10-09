import os
import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL")

def conectar():
    """Conecta ao banco PostgreSQL e retorna a conexão."""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def criar_tabelas():
    """Cria as tabelas de usuarios e postagens, caso não existam."""
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    nome TEXT NOT NULL,
                    usuario TEXT UNIQUE NOT NULL,
                    senha BYTEA NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS postagens (
                    id SERIAL PRIMARY KEY,
                    posto TEXT,
                    remetente TEXT,
                    codigo TEXT UNIQUE,
                    tipo TEXT,
                    valor NUMERIC,
                    forma_pagamento TEXT,
                    status_pagamento TEXT,
                    funcionario TEXT,
                    data_postagem TEXT,
                    data_pagamento TEXT,
                    observacao TEXT
                )
            """)
        conn.commit()

def adicionar_postagem(dados):
    posto, remetente, codigo, tipo, valor, forma_pagamento, status_pagamento, funcionario, data_postagem, data_pagamento, observacao = dados
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO postagens
                (posto, remetente, codigo, tipo, valor, forma_pagamento, status_pagamento,
                funcionario, data_postagem, data_pagamento, observacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (posto, remetente, codigo, tipo, valor, forma_pagamento, status_pagamento,
                  funcionario, data_postagem, data_pagamento, observacao))
        conn.commit()

def editar_postagem(id_postagem, novos_dados):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE postagens
                SET posto=%s, remetente=%s, codigo=%s, tipo=%s, valor=%s,
                    forma_pagamento=%s, status_pagamento=%s, funcionario=%s,
                    data_postagem=%s, data_pagamento=%s, observacao=%s
                WHERE id=%s
            """, (*novos_dados, id_postagem))
        conn.commit()

def listar_postagens():
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM postagens ORDER BY id DESC")
            return cur.fetchall()

def listar_postagens_pendentes():
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM postagens WHERE status_pagamento='Pendente' ORDER BY id DESC")
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

def autenticar(usuario, senha):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM usuarios WHERE usuario=%s", (usuario,))
            user = cur.fetchone()
            if user and bcrypt.checkpw(senha.encode("utf-8"), bytes(user["senha"])):
                return user
    return None

def listar_usuarios():
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nome, usuario, is_admin FROM usuarios ORDER BY id")
            return cur.fetchall()

def atualizar_usuario(user_id, nome, senha=None, is_admin=False):
    with conectar() as conn:
        with conn.cursor() as cur:
            if senha:
                senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())
                cur.execute("""
                    UPDATE usuarios
                    SET nome=%s, senha=%s, is_admin=%s
                    WHERE id=%s
                """, (nome, senha_hash, is_admin, user_id))
            else:
                cur.execute("""
                    UPDATE usuarios
                    SET nome=%s, is_admin=%s
                    WHERE id=%s
                """, (nome, is_admin, user_id))
        conn.commit()

def excluir_usuario_por_nome(usuario):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM usuarios WHERE usuario=%s", (usuario,))
        conn.commit()

def resetar_senha(usuario, nova_senha):
    nova_hash = bcrypt.hashpw(nova_senha.encode("utf-8"), bcrypt.gensalt())
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE usuarios SET senha=%s WHERE usuario=%s", (nova_hash, usuario))
        conn.commit()

# ------------------- Postagens -------------------

def codigo_existe(codigo):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM postagens WHERE codigo = %s", (codigo,))
            return cur.fetchone() is not None

def adicionar_postagem(dados):
    posto, remetente, codigo, tipo, valor, forma_pagamento, status_pagamento, funcionario, data_postagem, data_pagamento = dados
    if codigo_existe(codigo):
        raise ValueError("Código de rastreio já cadastrado.")
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO postagens
                (posto, remetente, codigo, tipo, valor, forma_pagamento, status_pagamento, funcionario, data_postagem, data_pagamento)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (posto, remetente, codigo, tipo, valor, forma_pagamento, status_pagamento, funcionario, data_postagem, data_pagamento))
        conn.commit()

def editar_postagem(id_postagem, novos_dados):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE postagens
                SET posto=%s, remetente=%s, codigo=%s, tipo=%s, valor=%s,
                    forma_pagamento=%s, status_pagamento=%s, funcionario=%s,
                    data_postagem=%s, data_pagamento=%s
                WHERE id=%s
            """, (*novos_dados, id_postagem))
        conn.commit()

def excluir_postagem(postagem_id):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM postagens WHERE id=%s", (postagem_id,))
        conn.commit()

def listar_postagens():
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM postagens ORDER BY id DESC")
            return cur.fetchall()

def listar_postagens_pendentes():
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM postagens
                WHERE status_pagamento = 'Pendente'
                ORDER BY id DESC
            """)
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
            query = """
                SELECT *
                FROM postagens
                WHERE EXTRACT(MONTH FROM TO_DATE(data_postagem, 'DD/MM/YYYY HH24:MI:SS')) = %s
                  AND EXTRACT(YEAR FROM TO_DATE(data_postagem, 'DD/MM/YYYY HH24:MI:SS')) = %s
            """
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
