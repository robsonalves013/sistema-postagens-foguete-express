import sqlite3
from datetime import datetime
import bcrypt

def conectar():
    return sqlite3.connect("postagens.db")

def criar_tabelas():
    conn = conectar()
    c = conn.cursor()

    # Usuários
    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        usuario TEXT UNIQUE,
        senha BLOB,
        is_admin INTEGER DEFAULT 0
    )
    """)

    # Postagens
    c.execute("""
    CREATE TABLE IF NOT EXISTS postagens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        c.execute("INSERT INTO usuarios (nome, usuario, senha, is_admin) VALUES (?, ?, ?, ?)",
                  ("Administrador", "admin", senha_hash, 1))
        print("Usuário admin criado com sucesso: admin / 1234")

    conn.commit()
    conn.close()

def adicionar_postagem(dados):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        INSERT INTO postagens (posto, remetente, codigo, tipo, valor, forma_pagamento, status_pagamento, funcionario, data_postagem, data_pagamento)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    c.execute("INSERT INTO usuarios (nome, usuario, senha, is_admin) VALUES (?, ?, ?, ?)",
              (nome, usuario, senha_hash, is_admin))
    conn.commit()
    conn.close()

def autenticar(usuario, senha):
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE usuario=?", (usuario,))
    user = c.fetchone()
    conn.close()
    if user and bcrypt.checkpw(senha.encode('utf-8'), user[3]):
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
            data = datetime.strptime(p[9], "%d/%m/%Y")
        except:
            continue
        if data.month == mes and data.year == ano:
            if (not posto or p[1] == posto) and (not tipo or p[4] == tipo) and (not forma_pagamento or p[6] == forma_pagamento):
                filtradas.append(p)
    conn.close()
    return filtradas

def atualizar_pagamento(postagem_id, status, data_pagamento):
    conn = conectar()
    c = conn.cursor()
    c.execute("UPDATE postagens SET status_pagamento = ?, data_pagamento = ? WHERE id = ?",
              (status, data_pagamento, postagem_id))
    conn.commit()
    conn.close()
