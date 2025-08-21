import streamlit as st
import pandas as pd
import os
from seo_utils import generar_keywords_por_cluster, fusionar_keywords

st.set_page_config(layout="wide")

st.title("🔍 Análisis SEO y Generación de Keywords por Clúster")

st.header("📁 Parte 1: Carga de archivos internos")

file_keywords = st.file_uploader("Carga el archivo de análisis interno (CSV o Excel)", type=["csv", "xlsx"], key="keywords")
file_auditoria = st.file_uploader("Carga el archivo de auditoría interna (CSV o Excel)", type=["csv", "xlsx"], key="auditoria")

df_keywords = None
df_auditoria = None

if file_keywords:
    try:
        df_keywords = pd.read_csv(file_keywords) if file_keywords.name.endswith(".csv") else pd.read_excel(file_keywords)
        st.success("Archivo de análisis cargado correctamente.")
    except Exception as e:
        st.error(f"Error al leer el archivo de análisis: {e}")

if file_auditoria:
    try:
        df_auditoria = pd.read_csv(file_auditoria) if file_auditoria.name.endswith(".csv") else pd.read_excel(file_auditoria)
        st.success("Archivo de auditoría cargado correctamente.")
    except Exception as e:
        st.error(f"Error al leer el archivo de auditoría: {e}")

st.header("📁 Parte 2: Carga de keywords externas (opcional)")

file_externas = st.file_uploader("Carga el archivo externo (CSV o Excel) con keywords", type=["csv", "xlsx"], key="externas")

df_externas = None

if file_externas:
    try:
        df_externas = pd.read_csv(file_externas) if file_externas.name.endswith(".csv") else pd.read_excel(file_externas)
        if df_externas.shape[1] == 0:
            st.warning("El archivo está vacío.")
        elif df_externas.shape[1] == 1:
            st.success("Archivo externo cargado correctamente.")
        else:
            st.info("Archivo externo cargado con múltiples columnas. Se usará la primera para las keywords.")
    except Exception as e:
        st.error(f"Error al leer el archivo externo: {e}")

st.header("🚀 Generar Keywords por Clúster")

if df_keywords is not None and df_auditoria is not None:
    if df_externas is not None:
        df_fusionado = fusionar_keywords(df_keywords[['url', 'palabra_clave']], df_externas)
        df_final = pd.merge(df_fusionado, df_auditoria[['URL', 'Cluster', 'Sub-cluster (si aplica)']], left_on='url', right_on='URL', how='left')
        df_final.dropna(subset=['Cluster'], inplace=True)
        resultados = generar_keywords_por_cluster(df_final, df_auditoria)
    else:
        resultados = generar_keywords_por_cluster(df_keywords, df_auditoria)

    if resultados is not None and not resultados.empty:
        st.success("✅ Keywords sugeridas generadas.")
        st.dataframe(resultados)
    else:
        st.warning("No se generaron keywords sugeridas.")
