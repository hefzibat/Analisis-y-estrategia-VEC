import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_keywords_por_cluster

st.set_page_config(page_title="Análisis SEO", layout="wide")
st.title("🔍 Análisis de Contenidos SEO")

st.markdown("### 1️⃣ Contenidos con potencial para optimizar")
archivo_analisis = st.file_uploader("Carga el archivo de análisis SEO (CSV o Excel)", type=["csv", "xlsx"])
archivo_auditoria = st.file_uploader("Carga el archivo de auditoría de contenidos (CSV o Excel)", type=["csv", "xlsx"])

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

        df_resultado = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.dataframe(df_resultado)

    except Exception as e:
        st.error(f"❌ Error al procesar los archivos: {e}")

st.markdown("---")
st.markdown("### 2️⃣ Palabras clave sugeridas por cluster y etapa del funnel")

if archivo_analisis and archivo_auditoria:
    try:
        df_keywords = generar_keywords_por_cluster(df_analisis, df_auditoria)
        st.dataframe(df_keywords)
    except Exception as e:
        st.error(f"❌ Error al procesar los archivos: {e}")
