import streamlit as st
import pandas as pd
import numpy as np
import os

@st.cache_data
def cargar_datos():
    archivos = st.file_uploader("Sube el archivo consolidado con clusters, tráfico, posición, etc.", type=["csv", "xlsx"], accept_multiple_files=False)
    if archivos is not None:
        nombre = archivos.name
        if nombre.endswith(".csv"):
            df = pd.read_csv(archivos)
        else:
            df = pd.read_excel(archivos, engine="openpyxl")
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        return df
    return None

def seleccionar_contenidos_para_optimizar(df):
    columnas_requeridas = ['url', 'palabra_clave', 'posición', 'volumen', 'dificultad', 'tráfico', 'cluster', 'subcluster']
    df.columns = [c.lower() for c in df.columns]
    df = df[[c for c in columnas_requeridas if c in df.columns]]
    df = df.dropna(subset=['posición', 'volumen', 'tráfico'])
    df['posición'] = pd.to_numeric(df['posición'], errors='coerce')
    df['score'] = (100 - df['posición']) * df['volumen'] * df['tráfico']
    df = df.sort_values(by='score', ascending=False).head(40)
    return df

def mostrar_clusters(df):
    if 'cluster' in df.columns and 'subcluster' in df.columns:
        st.write("Distribución por Clusters y Subclusters")
        conteo = df.groupby(['cluster', 'subcluster']).size().reset_index(name='conteo')
        st.dataframe(conteo)
    else:
        st.warning("No se encontraron las columnas 'cluster' y 'subcluster'.")

def generar_estrategia_contenido(df):
    if 'palabra_clave' not in df.columns:
        st.warning("Falta la columna 'palabra_clave'.")
        return
    st.write("Ideas de contenido basadas en las keywords actuales:")
    ideas = df['palabra_clave'].dropna().unique().tolist()[:10]
    canales = ['Blog', 'Email marketing', 'Webinars', 'Video corto', 'Podcast']
    estrategia = [(kw, np.random.choice(canales)) for kw in ideas]
    df_estrategia = pd.DataFrame(estrategia, columns=["Keyword sugerida", "Canal sugerido"])
    st.dataframe(df_estrategia)