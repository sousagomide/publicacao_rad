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


class StatisticTotal:

    def __init__(self, df):
        self.df = df
        self.regulamento = ['2014/2 a 2016/2', '2017/1 a 2018/2', '2019/1 a 2022/2', '2023/1 a 2024/1']
    
    def load(self):
        st.header('Análise Estatística da Pontuação Total por Revisão de Regulamento')
        opcoes = st.selectbox(
            'Selecione o regulamento',
            (self.regulamento)
        )
        limit = self.definirIQR(opcoes)
        df = self.buscarRegulamento(opcoes)
        self.printLimit(limit)
        df_limit = self.filterLimit(limit, df)
        st.subheader('Boxplot')
        self.bloxplot(df_limit, opcoes)
        st.subheader('Histograma')
        self.histograma(df_limit)
        st.subheader('Density plot')
        self.densityPlot(df_limit)
        st.subheader('Mediana dos totais por período')
        self.barrasMediana(self.calcularMedianaPorPeriodo(df_limit))
        st.subheader('Comparação entre os regulamentos')
        self.anova()


    ######################################################################################
    ####### Tela
    ######################################################################################

    def printLimit(self, limit):
        df_limit = limit.round(2).transpose()
        df_limit.columns = ['Valores']
        df_limit.index = [
            'Primeiro Quartil', 
            'Terceiro Quartil', 
            'Intervalo Interquartil',
            'Limite Inferior',
            'Limite Superior']
        st.dataframe(df_limit)

    def bloxplot(self, df, regulamento):
        df_box = df.copy()
        df_box['periodo_range'] = regulamento
        df_box['jitter'] = np.random.uniform(-0.2, 0.2, size=len(df_box))
        box = alt.Chart(df_box).mark_boxplot(extent='min-max', size=100).encode(
            x=alt.X('periodo_range:N', axis=alt.Axis(orient='bottom')),
            y=alt.Y('total:Q')
        )
        points = alt.Chart(df_box).mark_circle(size=10, opacity=0.5, color='black').encode(
            x=alt.X('jitter:Q', axis=alt.Axis(labels=False, ticks=False), title=None),
            y='total:Q'
        )
        chart = (points + box).properties(width=600, height=400)
        st.altair_chart(chart, use_container_width=True)

    def histograma(self, df):
        bin_step = 50
        df_curve = self.calcular_curva(df, bin_step)
        hist = alt.Chart(df).mark_bar(opacity=0.7, color='lightblue').encode(
            alt.X('total:Q', bin=alt.Bin(step=bin_step), title='Valor'),
            alt.Y('count():Q', title='Frequência')
        ).interactive()
        curve = alt.Chart(df_curve).mark_line(color='red', strokeWidth=2).encode(
            x='x:Q',
            y='y:Q'
        )
        chart = (hist + curve).properties(width=600, height=400)
        st.altair_chart(chart, use_container_width=True)

    def densityPlot(self, df):
        density_plot = alt.Chart(df).transform_density(
            'total',
            as_=['total', 'density'],
            extent=[df['total'].min(), df['total'].max()],
            steps=200
        ).mark_area(color='steelblue', opacity=0.5).encode(
            x='total:Q',
            y='density:Q'
        ).properties(
            width=600,
            height=400
        )
        st.altair_chart(density_plot, use_container_width=True)


    def barrasMediana(self, df):
        bar_chart = alt.Chart(df).mark_bar(color='steelblue').encode(
            x=alt.X('periodo:N', title='Período'),
            y=alt.Y('mediana_total:Q', title='Mediana do Total'),
            tooltip=['periodo', 'mediana_total']
        ).properties(
            width=600,
            height=400
        )
        text = alt.Chart(df).mark_text(
            align='center',
            baseline='bottom',
            dy=-2,
            fontSize=13
        ).encode(
            x='periodo:N',
            y='mediana_total:Q',
            text='mediana_total:Q'
        )
        chart = (bar_chart + text).properties(
            width=600,
            height=400
        )
        st.altair_chart(chart, use_container_width=True)

    ######################################################################################
    ####### Método
    ######################################################################################

    def anova(self):
        df = self.criarCategoriaPeriodo()
        test_normalidade = []
        for nome, grupo in df.groupby('categoria'):
            stat, p = shapiro(grupo['total'])
            test_normalidade.append(f'{nome} → p = {p:.4f} → {"Normal" if p > 0.05 else "Não normal"}')
        st.write(test_normalidade)
        grupos = [g['total'].values for _, g in df.groupby('categoria')]
        # Aplicar o teste de Kruskal-Wallis
        h_stat, p_valor = kruskal(*grupos)
        st.write(f"Kruskal-Wallis H = {h_stat:.2f}, p = {p_valor:.4f}")
        dunn_result = sp.posthoc_dunn(df, val_col='total', group_col='categoria', p_adjust='bonferroni')
        dunn_result_formatted = dunn_result.applymap(lambda x: f"{x:.2e}")
        st.write("Resultado do Dunn Test:")
        st.dataframe(dunn_result_formatted)


    def criarCategoriaPeriodo(self):
        df_total = []
        for i in self.regulamento:
            df = self.buscarRegulamento(i)
            limit = self.definirIQR(i)
            df_limit = self.filterLimit(limit, df)
            df_limit['categoria'] = i
            df_total.append(df_limit)
        return pd.concat(df_total, ignore_index=True)
    
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
        return df.loc[filtro, ["campus", "periodo", "total"]]
    
    def periodo_para_num(self, p):
        ano, semestre = map(int, p.split('/'))
        return ano * 10 + semestre
    
    def filterLimit(self, limit, df):
        df_filter = df.copy()
        return df_filter[(df_filter['total'] >= limit.loc['total', 'limitinf']) & (df_filter['total'] <= limit.loc['total', 'limitsup'])]

    def calcularMedianaPorPeriodo(self, df):
        df_mediana = df.copy()
        df_mediana = df_mediana.groupby('periodo')['total'].median().reset_index()
        df_mediana.rename(columns={'total': 'mediana_total'}, inplace=True)
        return df_mediana
    
    def calcular_curva(self, df, bin_step):
        start = (df['total'].min() // bin_step) * bin_step
        end = ((df['total'].max() // bin_step) + 1) * bin_step
        x_vals = np.linspace(start, end, 100)
        mean = df['total'].mean()
        std = df['total'].std()
        y_vals = norm.pdf(x_vals, mean, std)
        y_scaled = y_vals * len(df) * bin_step
        df_curve = pd.DataFrame({'x': x_vals, 'y': y_scaled})
        return df_curve
            

    
    
