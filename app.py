import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_keywords_por_cluster

st.set_page_config(layout="wide")
st.title("🔍 Análisis SEO y Estrategia de Contenidos")

st.sidebar.header("Sube tus archivos")
archivo_analisis = st.sidebar.file_uploader("Archivo de análisis (CSV o Excel)", type=["csv", "xlsx"])
archivo_auditoria = st.sidebar.file_uploader("Archivo de auditoría (CSV o Excel)", type=["csv", "xlsx"])
archivo_keywords = st.sidebar.file_uploader("Archivo de palabras clave externas (opcional)", type=["csv", "xlsx"])

def leer_archivo(archivo):
    if archivo is not None:
        if archivo.name.endswith('.csv'):
            return pd.read_csv(archivo)
        elif archivo.name.endswith('.xlsx'):
            return pd.read_excel(archivo)
    return None

df_analisis = leer_archivo(archivo_analisis)
df_auditoria = leer_archivo(archivo_auditoria)
df_keywords = leer_archivo(archivo_keywords)

if df_analisis is not None and df_auditoria is not None:
    st.subheader("📌 Parte 1: Contenidos con Potencial")
    try:
        df_potencial = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.dataframe(df_potencial, use_container_width=True)
    except Exception as e:
        st.error(f"Error en Parte 1: {e}")

    st.subheader("🌱 Parte 2: Nuevas Palabras Clave por Cluster")
    try:
        df_keywords_sugeridas = generar_keywords_por_cluster(df_analisis, df_auditoria, df_keywords)
        st.dataframe(df_keywords_sugeridas, use_container_width=True)
    except Exception as e:
        st.error(f"Error en Parte 2: {e}")
else:
    st.info("Por favor, sube los archivos necesarios.")
