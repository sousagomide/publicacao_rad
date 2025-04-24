import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import sqlite3 as sql
from streamlit_option_menu import option_menu

from dataset import Dataset
from suporte import Suporte
from limpeza import Cleaning
from statistic_total import StatisticTotal
from statistic_category import StatisticCategory

st.set_page_config(
    page_title='Estatística RAD',
    layout='wide',
    initial_sidebar_state='expanded'
)

@st.cache_resource
def conectar_banco():
    return sql.connect('rad_statistic.db')

@st.cache_data
def carregar_dados():
    connect = conectar_banco()
    df = pd.read_sql_query('SELECT campus, periodo, situacao, total, aula, ensino, capacitacao, pesquisa, extensao, administracao FROM rads, servidores WHERE rads.siape = servidores.siape ORDER BY periodo DESC', connect)
    connect.close()
    return df

df = carregar_dados()

################################################################################
# Menu Principal
################################################################################
with st.sidebar:
    selected = option_menu(
        menu_title='Estatística RAD',
        menu_icon='window-fullscreen',
        options=['Dataset', 'Análise Estatística', 'Suporte'],
        icons=['database', 'clipboard-data', 'info'],
        default_index=0,
        styles={
            'nav-link-selected': {'background-color': 'green'}
        }
    )



if selected == 'Dataset':
    Dataset(df).load()
elif selected == 'Suporte':
    Suporte().load()
elif selected == 'Análise Estatística':
    submenu = option_menu(
        None,
        ['Total', 'Categoria'],
        icons=['graph-up', 'bar-chart-fill'],
        orientation='horizontal',
        styles={
            'nav-link-selected': {'background-color': 'green'}
        }
    )
    df_clear = Cleaning(df).clear()
    if submenu == 'Total':
        StatisticTotal(df_clear).load()        
    elif submenu == 'Categoria':
        StatisticCategory(df_clear).load()