# db.py
import psycopg
from psycopg.rows import dict_row
import bcrypt
import os
from datetime import datetime

# ------------------- Configurações do Banco -------------------
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://usuario:senha@host:porta/banco")

# ------------------- Conexão -------------------
def conectar():
    """Conecta ao banco PostgreSQL e retorna a conexão."""
    return psycopg.connect(DATABASE_URL, row_factory=dict_row, sslmode="require")

# ------------------- Criação de Tabelas -------------------
def criar_tabelas():
    """Cria tabelas de usuários e postagens, caso não existam."""
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
    """Cria um novo usuário com senha criptografada."""
    senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO usuarios (nome, usuario, senha, is_admin)
                VALUES (%s, %s, %s, %s)
            """, (nome, usuario, senha_hash, is_admin))
        conn.commit()

def autenticar(usuario, senha):
    """Autentica um usuário verificando a senha criptografada."""
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM usuarios WHERE usuario=%s", (usuario,))
            user = cur.fetchone()
            if user and bcrypt.checkpw(senha.encode("utf-8"), bytes(user["senha"])):
                return user
    return None

def listar_usuarios():
    """Retorna todos os usuários cadastrados (sem mostrar senhas)."""
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nome, usuario, is_admin FROM usuarios ORDER BY id")
            return cur.fetchall()

def atualizar_usuario(user_id, nome, senha=None, is_admin=False):
    """Atualiza nome, senha (opcional) e privilégio de um usuário."""
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

def excluir_usuario(user_id):
    """Remove permanentemente um usuário pelo ID."""
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM usuarios WHERE id=%s", (user_id,))
        conn.commit()

def resetar_senha(usuario, nova_senha):
    """Redefine a senha de um usuário específico."""
    nova_hash = bcrypt.hashpw(nova_senha.encode("utf-8"), bcrypt.gensalt())
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE usuarios SET senha=%s WHERE usuario=%s", (nova_hash, usuario))
        conn.commit()

# ------------------- Postagens -------------------
def adicionar_postagem(dados):
    posto, remetente, codigo, tipo, valor, forma_pagamento, status_pagamento, funcionario, data_postagem, data_pagamento = dados

    if codigo_existe(codigo):
        raise ValueError("Código de rastreio já cadastrado.")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO postagens (posto, remetente, codigo, tipo, valor, forma_pagamento, status_pagamento, funcionario, data_postagem, data_pagamento)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (posto, remetente, codigo, tipo, valor, forma_pagamento, status_pagamento, funcionario, data_postagem, data_pagamento))
    conn.commit()
    conn.close()
    
def codigo_existe(codigo):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM postagens WHERE codigo = ?", (codigo,))
    existe = cursor.fetchone() is not None
    conn.close()
    return existe
    
def editar_postagem(id_postagem, novos_dados):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE postagens
        SET posto = ?, remetente = ?, codigo = ?, tipo = ?, valor = ?, 
            forma_pagamento = ?, status_pagamento = ?, funcionario = ?, 
            data_postagem = ?, data_pagamento = ?
        WHERE id = ?
    """, (*novos_dados, id_postagem))
    conn.commit()
    conn.close()


def listar_postagens():
    """Lista todas as postagens registradas (mais recentes primeiro)."""
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM postagens ORDER BY id DESC")
            return cur.fetchall()

def listar_postagens_pendentes():
    """Retorna todas as postagens com pagamento pendente."""
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM postagens
                WHERE status_pagamento = 'Pendente'
                ORDER BY id DESC
            """)
            return cur.fetchall()

def atualizar_pagamento(postagem_id, status, data_pagamento):
    """Atualiza o status e a data de pagamento de uma postagem."""
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE postagens
                SET status_pagamento=%s, data_pagamento=%s
                WHERE id=%s
            """, (status, data_pagamento, postagem_id))
        conn.commit()

def listar_postagens_mensal(mes, ano, filtro_posto=None, filtro_tipo=None, filtro_forma=None):
    """Filtra postagens por mês, ano e filtros opcionais (posto, tipo, forma)."""
    with conectar() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT * FROM postagens
                WHERE EXTRACT(MONTH FROM TO_DATE(data_postagem, 'DD/MM/YYYY')) = %s
                  AND EXTRACT(YEAR FROM TO_DATE(data_postagem, 'DD/MM/YYYY')) = %s
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
        



