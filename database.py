import sqlite3
from werkzeug.security import generate_password_hash

# Conectar ao banco de dados (ou criar se não existir)
conn = sqlite3.connect('banco.db')
cursor = conn.cursor()

# Criar a tabela de usuários
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        usuario TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL
    )
''')

# Inserir usuários de teste (execute apenas uma vez)
usuarios_iniciais = [
    ("João Comercial", "joao@email.com", "joaovendas", generate_password_hash("1234")),
    ("Maria Vendas", "maria@email.com", "mariavendas", generate_password_hash("5678")),
    ("Carlos Representante", "carlos@email.com", "carlosrep", generate_password_hash("abcd"))
]

try:
    cursor.executemany("INSERT INTO usuarios (nome, email, usuario, senha) VALUES (?, ?, ?, ?)", usuarios_iniciais)
    conn.commit()
    print("Usuários cadastrados com sucesso!")
except sqlite3.IntegrityError:
    print("Usuários já cadastrados.")

# Fechar conexão
conn.close()
