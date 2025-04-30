import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import sqlite3 as sql
from streamlit_option_menu import option_menu
import base64

st.set_page_config(
    page_title='IF Goiano - Campus Trindade: Públicação dos RADS',
    layout='wide'
)

@st.cache_resource
def conectar_banco():
    return sql.connect('rad_database.db')

@st.cache_data
def carregar_dados():
    connect = conectar_banco()
    df = pd.read_sql_query('SELECT nome, area, periodo, situacao, total, aula, ensino, capacitacao, pesquisa, extensao, administracao, total_nao_homologado FROM rads, servidores where rads.siape = servidores.siape', connect)
    connect.close()
    return df

df = carregar_dados()
periodo = ['2024/2', '2024/1', '2023/2', '2023/1']


################################################################################
# Blocos
################################################################################
def carregar_logo():
    file_path = "img/logo.png"
    with open(file_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{encoded}" width="200"/>
        </div>
        """,
        unsafe_allow_html=True
    )

def titulo():
    st.markdown(
        """
        <h2 style='text-align: center;'>
            Plataforma de Publicação dos Relatórios de Atividades dos servidores do quadro docente do IF Goiano - Campus Trindade
        </h2></br>
        Esta plataforma tem como objetivo disponibilizar os Relatórios de Atividades dos servidores do quadro docente, em conformidade com as determinações previstas no respectivo artigo.</br></br>
        <i>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Art. 26. O Relatório de Atividades deverá ser publicado no site oficial
        do campus, em até 10 dias após a avaliação final.</i></br></br>
        conforme disposto no Regulamento de Atividades Docentes do Instituto Federal de Educação, Ciência e Tecnologia Goiano.
        """,
        unsafe_allow_html=True
    )

def pontuacao_total_eixos(df):
        colunas_atividade = ["aula", "ensino", "capacitacao", "pesquisa", "extensao", "administracao"]
        color_scale = alt.Scale(scheme='tableau10')
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
            height=300
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
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.altair_chart(grafico_combinado, use_container_width=True)

def pontuacao_area_eixos(df):
    areas = sorted(df["area"].unique().tolist())
    st.subheader('Quadro de pontuação separado por área')
    for i in areas:
        st.subheader(f'Área: {i}')
        df_area = df[df['area'] == i]
        pontuacao_total_eixos(df_area)
        st.dataframe(df_area)
        







def selecao_periodo():
    st.subheader('Seleção do período')
    return st.selectbox('Selecione o período', periodo)

def filtrar_periodo(periodo, df):
    df_filtro = df[df['periodo'] == periodo]
    return df_filtro.sort_values(by='nome')

################################################################################
# Dashboard
################################################################################
carregar_logo()
titulo()
df_periodo = filtrar_periodo(selecao_periodo(), df)
st.dataframe(df_periodo)
st.subheader('Pontuação total dos eixos: Aula; Administração/Representação; Ensino; Capacitação; Pesquisa; Extensão')
pontuacao_total_eixos(df_periodo)
pontuacao_area_eixos(df_periodo)



