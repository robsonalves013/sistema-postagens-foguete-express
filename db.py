import psycopg
from psycopg.rows import dict_row
import bcrypt

# Configuração do banco de dados (Render)
DB_PARAMS = {
    "host": "SEU_HOST_DO_RENDER",
    "dbname": "SEU_DB",
    "user": "SEU_USUARIO",
    "password": "SUA_SENHA"
}

def conectar():
    """Conexão com PostgreSQL usando psycopg 3"""
    return psycopg.connect(**DB_PARAMS, row_factory=dict_row)

def criar_tabelas():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        nome TEXT,
        usuario TEXT UNIQUE,
        senha TEXT,
        is_admin BOOLEAN
    );
    """)
    cur.execute("""
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
    );
    """)
    conn.commit()
    cur.close()
    conn.close()

# ---------------- Usuários ----------------
def criar_usuario(nome, usuario, senha, is_admin):
    conn = conectar()
    cur = conn.cursor()
    hashed = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
    cur.execute("INSERT INTO usuarios (nome, usuario, senha, is_admin) VALUES (%s, %s, %s, %s)",
                (nome, usuario, hashed, bool(is_admin)))
    conn.commit()
    cur.close()
    conn.close()

def autenticar(usuario, senha):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios WHERE usuario=%s", (usuario,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user and bcrypt.checkpw(senha.encode('utf-8'), user['senha']):
        return user
    return None

def listar_usuarios():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users

def resetar_senha(usuario, nova_senha):
    conn = conectar()
    cur = conn.cursor()
    hashed = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt())
    cur.execute("UPDATE usuarios SET senha=%s WHERE usuario=%s", (hashed, usuario))
    conn.commit()
    cur.close()
    conn.close()

# ---------------- Postagens ----------------
def adicionar_postagem(dados):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO postagens 
        (posto, remetente, codigo, tipo, valor, forma_pagamento, status_pagamento, funcionario, data_postagem, data_pagamento)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, dados)
    conn.commit()
    cur.close()
    conn.close()

def listar_postagens():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM postagens ORDER BY id DESC")
    postagens = cur.fetchall()
    cur.close()
    conn.close()
    return postagens

def atualizar_pagamento(post_id, status, data_pagamento):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE postagens SET status_pagamento=%s, data_pagamento=%s WHERE id=%s",
                (status, data_pagamento, post_id))
    conn.commit()
    cur.close()
    conn.close()

def listar_postagens_mensal(mes, ano, filtro_posto=None, filtro_tipo=None, filtro_forma=None):
    conn = conectar()
    cur = conn.cursor()
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

    cur.execute(query, params)
    postagens = cur.fetchall()
    cur.close()
    conn.close()
    return postagens
