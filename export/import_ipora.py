import re
import pandas as pd
import sqlite3

connection = sqlite3.connect('rad_database.db')
cursor = connection.cursor()
pattern = r'^(.*?)\s\((\d+)\)$'

df_areas = pd.read_excel('export/download/ipora/areas.xlsx', engine='openpyxl')
areas_por_siape = {
    str(int(row['MATRICULA'])): row['AREA']
    for _, row in df_areas.iterrows()
}

arquivos = [
    'export/download/ipora/2023-1.xlsx',
    'export/download/ipora/2023-2.xlsx',
    'export/download/ipora/2024-1.xlsx',
    'export/download/ipora/2024-2.xlsx',
    'export/download/ipora/2025-1.xlsx',
    'export/download/ipora/2025-2.xlsx',
]
novos_servidores = []

for path in arquivos:
    print(path)
    df = pd.read_excel(path, engine='openpyxl')
    for index, row in df.iterrows():
        result = re.match(pattern, df.loc[index, 'Professor'])
        siape = result.group(2)
        data = {
            'periodo': df.loc[index, 'Periodo letivo'],
            'nome': result.group(1),
            'siape': siape,
            'situacao': df.loc[index, 'Situação'],
            'total': df.loc[index, 'Total'],
            'aula': float(df.loc[index, 'Aula']),
            'ensino': float(df.loc[index, 'Ensino']),
            'capacitacao': float(df.loc[index, 'Capacitação']),
            'pesquisa': float(df.loc[index, 'Pesquisa']),
            'extensao': float(df.loc[index, 'Extensão']),
            'administracao': float(df.loc[index, 'Administração e Representação']),
            'total_nao_homologado': float(df.loc[index, 'Total não homologado'])
        }
        cursor.execute('SELECT * FROM servidores WHERE siape = ?', (siape,))
        rows = cursor.fetchall()
        if len(rows) == 0:
            area = areas_por_siape.get(siape, '')
            cursor.execute(
                'INSERT INTO servidores (siape, nome, campus, area) VALUES (?, ?, ?, ?)',
                (siape, data['nome'], 'CMPIPR', area)
            )
            connection.commit()
            novos_servidores.append((siape, data['nome'], area))
        query = """INSERT INTO rads (siape, periodo, situacao, total, aula, ensino, capacitacao, pesquisa, extensao, administracao, total_nao_homologado)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        values = (data['siape'], data['periodo'], data['situacao'], data['total'], data['aula'], data['ensino'], data['capacitacao'], data['pesquisa'], data['extensao'], data['administracao'], data['total_nao_homologado'])
        cursor.execute(query, values)
        connection.commit()

cursor.close()
connection.close()

print()
print(f'Servidores novos adicionados: {len(novos_servidores)}')
for siape, nome, area in novos_servidores:
    print(f'  {siape} - {nome} - area: {area}')
