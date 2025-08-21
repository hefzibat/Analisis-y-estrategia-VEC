import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_keywords_por_cluster

st.set_page_config(layout="wide")
st.title("🔍 Análisis SEO y Estrategia de Contenidos")

st.sidebar.header("Sube tus archivos")
archivo_analisis = st.sidebar.file_uploader("Archivo de análisis SEO (.csv o .xlsx)", type=["csv", "xlsx"])
archivo_auditoria = st.sidebar.file_uploader("Archivo de auditoría (.csv o .xlsx)", type=["csv", "xlsx"])
archivo_keywords_externas = st.sidebar.file_uploader("Palabras clave externas (opcional)", type=["csv", "xlsx"])

if archivo_analisis and archivo_auditoria:
    try:
        df_analisis = pd.read_csv(archivo_analisis) if archivo_analisis.name.endswith(".csv") else pd.read_excel(archivo_analisis)
        df_auditoria = pd.read_csv(archivo_auditoria) if archivo_auditoria.name.endswith(".csv") else pd.read_excel(archivo_auditoria)
        df_keywords = None
        if archivo_keywords_externas:
            df_keywords = pd.read_csv(archivo_keywords_externas) if archivo_keywords_externas.name.endswith(".csv") else pd.read_excel(archivo_keywords_externas)

        try:
            st.subheader("📊 Parte 1: Contenidos con mayor potencial de optimización")
            resultado1 = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
            st.dataframe(resultado1)
        except Exception as e:
            st.error(f"Error en Parte 1: {e}")

        try:
            st.subheader("🧠 Parte 2: Nuevas palabras clave por cluster")
            resultado2 = generar_keywords_por_cluster(df_analisis, df_auditoria, df_keywords)
            st.dataframe(resultado2)
        except Exception as e:
            st.error(f"Error en Parte 2: {e}")

    except Exception as e:
        st.error(f"Error al procesar los archivos: {e}")
else:
    st.info("Por favor, sube los archivos de análisis y auditoría para comenzar.")
