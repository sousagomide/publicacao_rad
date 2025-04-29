import sqlite3

connection = sqlite3.connect('rad_database.db')

cursor = connection.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS servidores (
        siape TEXT PRIMARY KEY,
        nome TEXT,
        campus TEXT,
        area TEXT DEFAULT ''
    )               
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS rads (
        id INTEGER PRIMARY KEY,
        periodo TEXT,
        situacao TEXT,
        total DECIMAL(5, 3),
        aula DECIMAL(5, 3),
        ensino DECIMAL(5, 3),
        capacitacao DECIMAL(5, 3),
        pesquisa DECIMAL(5, 3),
        extensao DECIMAL(5, 3),
        administracao DECIMAL(5, 3),
        total_nao_homologado DECIMAL(5, 3),
        siape TEXT NOT NULL,
        FOREIGN KEY(siape) REFERENCES servidores(siape) ON UPDATE CASCADE ON DELETE CASCADE
    )
''')
