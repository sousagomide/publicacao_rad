import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import sqlite3 as sql
from streamlit_option_menu import option_menu

class Dataset:

    def __init__(self, df):
        self.df = df
        self.periodLabel = ['2014/2', '2015/1', '2015/2', '2016/1', '2016/2', '2017/1', '2017/2', '2018/1', '2018/2', '2019/1', '2019/2', '2020/1', '2020/2', '2021/1', '2021/2', '2022/1', '2022/2', '2023/1', '2023/2', '2024/1']

    def load(self):
        df = self.cleaning()
        st.title('DataSet')
        st.header('Dados dos Relatórios de Atividades 2014/2 a 2024/1')
        st.dataframe(df)
        st.header('Bloxplot')
        self.bloxplot(df)
        st.header('Estatística Descritiva')
        st.dataframe(self.statisticDescribe(df))
        with st.expander('Método para remover os valores outliers...'):
            st.write('1. Calcular')
            st.write('Q1 = primeiro quartil (25%)')
            st.write('Q3 = terceiro quartil (75%)')
            st.write('IQR = Q3 - Q1')
            st.write('2. Definir os limites')
            st.write('Limite inferior = Q1 - 1.5 × IQR')
            st.write('Limite superior = Q3 + 1.5 × IQR')

    def cleaning(self):
        rows = self.df['total'] > 1200
        # Remove os totais maiores que 1200
        df_limpo = self.df[~rows]
        # Deixa apenas a situacao = 'Homologado'
        df_limpo = df_limpo[df_limpo['situacao'] == 'Homologado']
        return df_limpo
    
    def filter(self, df, periodo):
        output = df.copy()
        if periodo == 'TODOS':
            output['periodo'] = '2014-2024'
        else:
            output = output[output['periodo']==periodo]
        return output
    
    def statisticDescribe(self, df):
        output = {}
        for i in self.periodLabel:
            dfPartial = df[df['periodo']==i]
            output[i] = dfPartial['total'].describe().to_numpy()
        df_final = pd.DataFrame(output)
        df_final.index = ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']
        return df_final

    def bloxplot(self, df):
        opcoes = st.selectbox(
            'Selecione o período',
            (['TODOS'] + self.periodLabel)
        )
        df_filter = self.filter(df, opcoes)
        df_filter['jitter'] = np.random.uniform(-0.2, 0.2, size=len(df_filter))
        box = alt.Chart(df_filter).mark_boxplot(extent='min-max', size=100).encode(
            x=alt.X('periodo:N', axis=alt.Axis(orient='bottom')),
            y=alt.Y('total:Q')
        )
        points = alt.Chart(df_filter).mark_circle(size=10, opacity=0.5, color='black').encode(
            x=alt.X('jitter:Q', axis=alt.Axis(labels=False, ticks=False), title=None),
            y='total:Q'
        )
        chart = (points + box).properties(width=600, height=400)
        st.altair_chart(chart, use_container_width=True)
        
            
