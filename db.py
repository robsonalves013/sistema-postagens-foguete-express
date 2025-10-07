import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
from datetime import datetime

# Configurações do banco PostgreSQL no Render
DB_PARAMS = {
    "host": "dpg-d3ijmvffte5s7391mug0-a",
    "dbname": "postagens_db",
    "user": "postagens_db_user",
    "password": "ciXfjUZZcKBJi1xVIZhqxykaLeGMN8GR",
    "port": 5432
}

def conectar():
    return psycopg2.connect(**DB_PARAMS, cursor_factory=RealDictCursor)

def criar_tabelas():
    conn = conectar()
    c = conn.cursor()

    # Usuários
    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        nome TEXT,
        usuario TEXT UNIQUE,
        senha BYTEA,
        is_admin INTEGER DEFAULT 0
    )
    """)

    # Postagens
    c.execute("""
    CREATE TABLE IF NOT EXISTS postagens (
        id SERIAL PRIMARY KEY,
        posto TEXT,
        remetente TEXT,
        codigo TEXT,
        tipo TEXT,
        valor REAL,
        forma_pagamento TEXT,
        status_pagamento TEXT,
        funcionario TEXT,
        data_postagem TEXT,
        data_pagamento TEXT
    )
    """)

    # Usuário admin padrão
    c.execute("SELECT * FROM usuarios WHERE usuario='admin'")
    if not c.fetchone():
        senha_hash = bcrypt.hashpw("1234".encode('utf-8'), bcrypt.gensalt())
        c.execute(
            "INSERT INTO usuarios (nome, usuario, senha, is_admin) VALUES (%s, %s, %s, %s)",
            ("Administrador", "admin", senha_hash, 1)
        )
        print("Usuário admin criado com sucesso: admin / 1234")

    conn.commit()
    conn.close()

def adicionar_postagem(dados):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        INSERT INTO postagens (posto, remetente, codigo, tipo, valor, forma_pagamento, status_pagamento, funcionario, data_postagem, data_pagamento)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, dados)
    conn.commit()
    conn.close()

def listar_postagens():
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT * FROM postagens ORDER BY data_postagem DESC")
    dados = c.fetchall()
    conn.close()
    return dados

def listar_usuarios():
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT id, nome, usuario, is_admin FROM usuarios")
    dados = c.fetchall()
    conn.close()
    return dados

def criar_usuario(nome, usuario, senha, is_admin=0):
    conn = conectar()
    c = conn.cursor()
    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
    c.execute("INSERT INTO usuarios (nome, usuario, senha, is_admin) VALUES (%s, %s, %s, %s)",
              (nome, usuario, senha_hash, is_admin))
    conn.commit()
    conn.close()

def resetar_senha(usuario, nova_senha):
    conn = conectar()
    c = conn.cursor()
    senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt())
    c.execute("UPDATE usuarios SET senha=%s WHERE usuario=%s", (senha_hash, usuario))
    conn.commit()
    conn.close()

def autenticar(usuario, senha):
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE usuario=%s", (usuario,))
    user = c.fetchone()
    conn.close()
    if user and bcrypt.checkpw(senha.encode('utf-8'), user['senha']):
        return user
    return None

def listar_postagens_mensal(mes, ano, posto=None, tipo=None, forma_pagamento=None):
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT * FROM postagens")
    todas = c.fetchall()
    filtradas = []
    for p in todas:
        try:
            data = datetime.strptime(p['data_postagem'], "%d/%m/%Y")
        except:
            continue
        if data.month == mes and data.year == ano:
            if (not posto or p['posto'] == posto) and (not tipo or p['tipo'] == tipo) and (not forma_pagamento or p['forma_pagamento'] == forma_pagamento):
                filtradas.append(p)
    conn.close()
    return filtradas

def atualizar_pagamento(postagem_id, status, data_pagamento):
    conn = conectar()
    c = conn.cursor()
    c.execute("UPDATE postagens SET status_pagamento=%s, data_pagamento=%s WHERE id=%s",
              (status, data_pagamento, postagem_id))
    conn.commit()
    conn.close()
