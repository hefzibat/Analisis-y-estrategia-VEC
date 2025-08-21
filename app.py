import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_nuevas_keywords, generar_sugerencias_contenido

st.set_page_config(page_title="SEO App", layout="wide")

st.title("🔍 Análisis de Contenidos para Optimización SEO")

st.sidebar.header("Carga tus archivos")
archivo_analisis = st.sidebar.file_uploader("📄 Archivo de análisis (Excel)", type=["xlsx"])
archivo_auditoria = st.sidebar.file_uploader("📄 Archivo de auditoría (Excel)", type=["xlsx"])

if archivo_analisis and archivo_auditoria:
    df_analisis = pd.read_excel(archivo_analisis)
    df_auditoria = pd.read_excel(archivo_auditoria)

    try:
        st.header("1️⃣ Contenidos con potencial")
        df_top = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.dataframe(df_top[["URL", "PALABRA CLAVE", "SCORE", "CLUSTER", "SUBCLUSTER"]], use_container_width=True)

        st.header("2️⃣ Nuevas palabras clave")
        df_clustered, nuevas_keywords = generar_nuevas_keywords(df_top)
        st.dataframe(pd.DataFrame(nuevas_keywords), use_container_width=True)

        st.header("3️⃣ Sugerencias de contenido")
        df_sugerencias = generar_sugerencias_contenido(nuevas_keywords, df_clustered)
        st.dataframe(df_sugerencias, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
