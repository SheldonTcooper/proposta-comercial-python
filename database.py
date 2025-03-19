import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect('banco.db')
cursor = conn.cursor()

# Criar a tabela de usuários se não existir
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        senha TEXT NOT NULL
    )
''')

# Criar a tabela de propostas se não existir
cursor.execute('''
    CREATE TABLE IF NOT EXISTS propostas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        consultor TEXT NOT NULL,
        telefone TEXT NOT NULL,
        email TEXT NOT NULL,
        cliente TEXT NOT NULL,
        telefone_cliente TEXT NOT NULL,
        email_cliente TEXT NOT NULL,
        descricao TEXT NOT NULL,
        valor TEXT NOT NULL,
        taxa TEXT NOT NULL,
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Verifica se os usuários já existem antes de cadastrar
cursor.execute("SELECT COUNT(*) FROM usuarios")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO usuarios (nome, senha) VALUES ('vendedor1', '1234')")
    cursor.execute("INSERT INTO usuarios (nome, senha) VALUES ('vendedor2', '5678')")
    conn.commit()
    print("Usuários cadastrados com sucesso!")
else:
    print("Usuários já cadastrados.")

# Salvar e fechar conexão
conn.commit()
conn.close()
