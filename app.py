import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_keywords_por_cluster

st.set_page_config(layout="wide")
st.title("🔍 Análisis SEO y Estrategia de Contenidos")

st.header("📂 Parte 1: Contenidos con Potencial de Optimización")
archivo_analisis = st.file_uploader("Sube el archivo de análisis (CSV o Excel)", type=["csv", "xlsx"])
archivo_auditoria = st.file_uploader("Sube el archivo de auditoría (CSV o Excel)", type=["csv", "xlsx"])

if archivo_analisis and archivo_auditoria:
    try:
        if archivo_analisis.name.endswith('.csv'):
            df_analisis = pd.read_csv(archivo_analisis)
        else:
            df_analisis = pd.read_excel(archivo_analisis)

        if archivo_auditoria.name.endswith('.csv'):
            df_auditoria = pd.read_csv(archivo_auditoria)
        else:
            df_auditoria = pd.read_excel(archivo_auditoria)

        resultado_parte1 = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.success("✅ Contenidos con potencial identificados:")
        st.dataframe(resultado_parte1)
    except Exception as e:
        st.error(f"Error en Parte 1: {e}")

st.header("🧠 Parte 2: Sugerencia de Keywords por Cluster")
archivo_keywords = st.file_uploader("Sube archivo con keywords y clusters", type=["csv", "xlsx"], key="parte2")

if archivo_keywords:
    try:
        if archivo_keywords.name.endswith('.csv'):
            df_keywords = pd.read_csv(archivo_keywords)
        else:
            df_keywords = pd.read_excel(archivo_keywords)

        resultado_parte2 = generar_keywords_por_cluster(df_keywords)
        st.success("✅ Keywords sugeridas por cluster:")
        st.dataframe(resultado_parte2)
    except Exception as e:
        st.error(f"Error en Parte 2: {e}")
