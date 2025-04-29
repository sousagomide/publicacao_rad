import os
import re
import pandas as pd
import sqlite3

connection = sqlite3.connect('rad_database.db')
contents = os.listdir('download')
# contents = ['rad_2014_2.xlsx']
cursor = connection.cursor()
pattern = r'^(.*?)\s\((\d+)\)$'
for item in contents:
    path = f'download/{item}'
    print(path)
    df = pd.read_excel(path, engine='openpyxl')
    # print(df.head())
    for index, row in df.iterrows():
        result = re.match(pattern, df.loc[index, 'Professor'])
        data = {
            'campus': df.loc[index, 'Campus'],
            'periodo': df.loc[index, 'Periodo letivo'],
            'nome': result.group(1),
            'siape': result.group(2),
            'situacao': df.loc[index, 'Situação'],
            'total': df.loc[index, 'Total'],
            'aula': int(df.loc[index, 'Aula']),
            'ensino': int(df.loc[index, 'Ensino']),
            'capacitacao': int(df.loc[index, 'Capacitação']),
            'pesquisa': int(df.loc[index, 'Pesquisa']),
            'extensao': int(df.loc[index, 'Extensão']),
            'administracao': int(df.loc[index, 'Administração e Representação']),
            'total_nao_homologado': int(df.loc[index, 'Total não homologado'])
        }
        cursor.execute(f'SELECT * FROM servidores WHERE siape = "{data['siape']}"')
        rows = cursor.fetchall()
        if len(rows) == 0:
            cursor.execute(f'INSERT INTO servidores (siape, nome, campus) VALUES ("{data['siape']}", "{data['nome']}", "{data['campus']}")')
            connection.commit()
        query = """INSERT INTO rads (siape, periodo, situacao, total, aula, ensino, capacitacao, pesquisa, extensao, administracao, total_nao_homologado) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        values = (data['siape'], data['periodo'], data['situacao'], data['total'], data['aula'], data['ensino'], data['capacitacao'], data['pesquisa'], data['extensao'], data['administracao'], data['total_nao_homologado'])
        cursor.execute(query, values)
        connection.commit()
cursor.close()
connection.close()