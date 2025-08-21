import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial

st.set_page_config(page_title="App de Análisis SEO", layout="wide")
st.title("🔍 App de Análisis SEO para Contenidos")

st.markdown("""
Esta herramienta analiza datos de rendimiento de tus contenidos y auditoría para ayudarte a detectar los que tienen mayor potencial de optimización.
""")

st.sidebar.header("Carga tus archivos")

archivo_analisis = st.sidebar.file_uploader("📄 Archivo de análisis (CSV o Excel)", type=["csv", "xlsx"])
archivo_auditoria = st.sidebar.file_uploader("📄 Archivo de auditoría (CSV o Excel)", type=["csv", "xlsx"])

df_analisis = None
df_auditoria = None

if archivo_analisis:
    if archivo_analisis.name.endswith(".csv"):
        df_analisis = pd.read_csv(archivo_analisis)
    else:
        df_analisis = pd.read_excel(archivo_analisis)

if archivo_auditoria:
    if archivo_auditoria.name.endswith(".csv"):
        df_auditoria = pd.read_csv(archivo_auditoria)
    else:
        df_auditoria = pd.read_excel(archivo_auditoria)

if df_analisis is not None and df_auditoria is not None:
    try:
        st.subheader("🔎 Parte 1: Contenidos con mayor potencial de optimización")
        df_resultado = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.dataframe(df_resultado, use_container_width=True)
    except Exception as e:
        st.error(f"❌ Error: '{e}'")
