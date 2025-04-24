import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import sqlite3 as sql
from streamlit_option_menu import option_menu
from scipy.stats import norm, shapiro, kruskal
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import statsmodels.api as sm
import scikit_posthocs as sp

class StatisticCategory:

    def __init__(self, df):
        self.df = df
        self.regulamento = ['2018/1 a 2018/2', '2019/1 a 2022/2', '2023/1 a 2024/1']

    ######################################################################################
    ####### Visualização
    ######################################################################################

    def load(self):
        st.header('Análise Estatística da Pontuação por Categoria por Revisão de Regulamento')
        opcoes = st.selectbox('Selecione o regulamento', (self.regulamento))
        limit = self.definirIQR(opcoes)
        df = self.buscarRegulamento(opcoes)
        df_limit = self.filterLimit(limit, df)
        opcoesCampus = st.selectbox('Selecione o campus', (self.listarCampus(df_limit)))
        self.pizza(df_limit, opcoesCampus)
        self.barras_agrupadas(df_limit, opcoesCampus)
        self.quadroDocente()


    def pizza(self, df, opcoesCampus):
        colunas_atividade = ["aula", "ensino", "capacitacao", "pesquisa", "extensao", "administracao"]
        color_scale = alt.Scale(scheme='tableau10')
        if opcoesCampus != 'TODOS':
            df = df[df['campus'] == opcoesCampus]
        totais = df[colunas_atividade].sum().reset_index()
        totais.columns = ['Atividade', 'Total']
        chart = alt.Chart(totais).mark_arc().encode(
            theta=alt.Theta(field='Total', type='quantitative'),
            color=alt.Color(field='Atividade', type='nominal', scale=color_scale),
            tooltip=[
                alt.Tooltip("Atividade", title="Atividade"),
                alt.Tooltip("Total", title="Total")
            ]
        ).properties(
            width=300,
            height=300,
            title=f'Total de atividades por tipo - Campus: {opcoesCampus}'
        )
        barras = alt.Chart(totais).mark_bar().encode(
            y=alt.Y('Atividade', sort='-x', title=''),
            x=alt.X('Total', title='Total'),
            color=alt.Color('Atividade', scale=color_scale, legend=None),
            tooltip=['Atividade', 'Total']
        ).properties(
            width=300,
            height=300
        )
        text = alt.Chart(totais).mark_text(
            align='left',
            baseline='middle',
            dx=3  # desloca o texto um pouco à direita
        ).encode(
            y=alt.Y('Atividade', sort='-x'),
            x=alt.X('Total'),
            text=alt.Text('Total')
        )
        grafico_combinado = alt.hconcat(chart, barras+text)
        st.altair_chart(grafico_combinado, use_container_width=True)
        st.dataframe(totais)

    def barras_agrupadas(self, df, opcoesCampus):
        atividades = ["aula", "ensino", "capacitacao", "pesquisa", "extensao", "administracao"]
        color_scale = alt.Scale(scheme='tableau10')
        if opcoesCampus != 'TODOS':
            df = df[df['campus'] == opcoesCampus]
        df[atividades] = df[atividades].apply(pd.to_numeric, errors='coerce')
        df_agrupado = df.groupby('periodo')[atividades].sum().reset_index()
        df_melted = df_agrupado.melt(id_vars='periodo', 
                             value_vars=atividades,
                             var_name='Atividade', 
                             value_name='Total')
        df_melted = df_melted[df_melted['Total'].notnull()]
        chart = alt.Chart(df_melted).mark_bar().encode(
            x=alt.X('periodo:N', title='Período', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('Total:Q', title='Total de Atividades'),
            color=alt.Color('Atividade:N', scale=color_scale, legend=alt.Legend(title='Atividade')),
            tooltip=['periodo', 'Atividade', 'Total'],
            xOffset='Atividade:N'  # <- isso agrupa as barras lado a lado por atividade
        ).properties(
            width=600,
            height=400,
            title='Atividades por Período (barras agrupadas)'
        )
        st.altair_chart(chart, use_container_width=True)
        df_pivotado = df_melted.pivot(
            index='Atividade',
            columns='periodo',
            values='Total'
        ).fillna(0).astype(int)
        st.subheader("Resumo de atividades por período")
        st.dataframe(df_pivotado)
        # Calcula a variação percentual da última coluna em relação à primeira
        variacao_percentual = ((df_pivotado.iloc[:, -1] - df_pivotado.iloc[:, 0]) / df_pivotado.iloc[:, 0]) * 100
        # Cria novo DataFrame com os resultados
        df_variacao = pd.DataFrame({
            'Atividade': df_pivotado.index,
            'Variação Percentual (%)': variacao_percentual.round(2)
        }).set_index('Atividade')
        styled_df = df_variacao.style \
        .applymap(self.colorir_valor) \
        .format("{:.2f}")
        st.subheader("Variação Percentual da Primeira para a Última Coluna")
        st.dataframe(styled_df)

    def colorir_valor(self, val):
        if val > 0:
            return 'background-color: #d4edda'  # verde claro
        elif val < 0:
            return 'background-color: #f8d7da'  # vermelho claro
        return ''

    def quadroDocente(self):
        dados = {
            'ano': [2018, 2019, 2020, 2021, 2022, 2023],
            'número de docentes': [774, 812, 792, 814, 820, 805],
            'docente efetivo': [674, 721, 722, 729, 726, 713]
        }
        df_docentes = pd.DataFrame(dados)
        st.subheader("Tabela de Docentes por Ano (Plataforma Nilo Peçanha)")
        st.dataframe(df_docentes)
        # Transformando os dados para o formato adequado para o gráfico
        df_melted = df_docentes.melt(id_vars=['ano'], var_name='Tipo de Docente', value_name='Quantidade')

        # Garantindo que "Tipo de Docente" seja tratado como uma variável categórica
        df_melted['Tipo de Docente'] = df_melted['Tipo de Docente'].astype(str)

        # Gráfico de linha
        chart = alt.Chart(df_melted).mark_line().encode(
            x='ano:O',  # Eixo X com os anos
            y='Quantidade:Q',  # Eixo Y com o número de docentes
            color='Tipo de Docente:N',  # Cor por tipo de docente (número de docentes ou efetivos)
            tooltip=['ano', 'Tipo de Docente', 'Quantidade']  # Tooltip para mostrar valores
        ).properties(
            title='Número de Docentes e Docentes Efetivos por Ano',
            width=600,
            height=400
        )

        # Exibindo o gráfico no Streamlit
        st.subheader("Gráfico de Linha - Número de Docentes e Docente Efetivo")
        st.altair_chart(chart, use_container_width=True)
    
        


    ######################################################################################
    ####### Método
    ######################################################################################
    def definirIQR(self, regulamento):
        df = self.buscarRegulamento(regulamento)
        descricao = df.describe()
        return pd.DataFrame({
            'q1': descricao.loc["25%"], 
                'q3': descricao.loc["75%"], 
            'iqr': (descricao.loc["75%"] - descricao.loc["25%"]),
            'limitinf': (descricao.loc["25%"] - 1.5 * (descricao.loc["75%"] - descricao.loc["25%"])).clip(lower=0),
            'limitsup': descricao.loc["75%"] + 1.5 * (descricao.loc["75%"] - descricao.loc["25%"])
        })

    def buscarRegulamento(self, regulamento):
        inicio, fim = regulamento.split(' a ')
        df = self.df.copy()
        df["periodo_num"] = df["periodo"].apply(self.periodo_para_num)        
        filtro = (df["periodo_num"] >= self.periodo_para_num(inicio)) & (df["periodo_num"] <= self.periodo_para_num(fim))
        return df.loc[filtro, ["campus", "periodo", "total", "aula", "ensino", "capacitacao", "pesquisa", "extensao", "administracao"]]
    
    def periodo_para_num(self, p):
        ano, semestre = map(int, p.split('/'))
        return ano * 10 + semestre
    
    def filterLimit(self, limit, df):
        df_filter = df.copy()
        return df_filter[(df_filter['total'] >= limit.loc['total', 'limitinf']) & (df_filter['total'] <= limit.loc['total', 'limitsup'])]
    
    def listarCampus(self, df):
        valores_ordenados = sorted(df['campus'].dropna().unique().tolist())
        valores_ordenados.insert(0, 'TODOS')
        return valores_ordenados
