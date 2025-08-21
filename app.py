# app.py
import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_keywords_por_cluster

st.set_page_config(layout="wide")
st.title("🔍 Análisis SEO y Estrategia de Contenidos")

# Carga de archivos
st.sidebar.header("Sube tus archivos")
archivo_analisis = st.sidebar.file_uploader("Archivo de análisis SEO (.csv o .xlsx)", type=["csv", "xlsx"])
archivo_auditoria = st.sidebar.file_uploader("Archivo de auditoría (.csv o .xlsx)", type=["csv", "xlsx"])
archivo_keywords_externas = st.sidebar.file_uploader("Palabras clave externas (opcional)", type=["csv", "xlsx"])

if archivo_analisis and archivo_auditoria:
    try:
        if archivo_analisis.name.endswith(".csv"):
            df_analisis = pd.read_csv(archivo_analisis)
        else:
            df_analisis = pd.read_excel(archivo_analisis)

        if archivo_auditoria.name.endswith(".csv"):
            df_auditoria = pd.read_csv(archivo_auditoria)
        else:
            df_auditoria = pd.read_excel(archivo_auditoria)

        if archivo_keywords_externas:
            if archivo_keywords_externas.name.endswith(".csv"):
                df_keywords_externas = pd.read_csv(archivo_keywords_externas)
            else:
                df_keywords_externas = pd.read_excel(archivo_keywords_externas)
        else:
            df_keywords_externas = None

        # Parte 1
        try:
            st.subheader("📊 Parte 1: Contenidos con mayor potencial de optimización")
            df_resultado = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
            st.dataframe(df_resultado)
        except Exception as e1:
            st.error(f"Error en Parte 1: {e1}")

        # Parte 2
        try:
            st.subheader("🧠 Parte 2: Nuevas palabras clave por cluster")
            df_keywords = generar_keywords_por_cluster(df_analisis, df_auditoria, df_keywords_externas)
            st.dataframe(df_keywords)
        except Exception as e2:
            st.error(f"Error en Parte 2: {e2}")

    except Exception as e:
        st.error(f"Error cargando los archivos: {e}")
else:
    st.info("Por favor, sube los archivos de análisis y auditoría para comenzar.")
