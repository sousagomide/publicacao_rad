import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import sqlite3 as sql
from streamlit_option_menu import option_menu

class Cleaning:

    def __init__(self, df):
        self.df = df

    def clear(self):
        rows = self.df['total'] > 1200
        # Remove os totais maiores que 1200
        df_limpo = self.df[~rows]
        # Deixa apenas a situacao = 'Homologado'
        df_limpo = df_limpo[df_limpo['situacao'] == 'Homologado']
        return df_limpo