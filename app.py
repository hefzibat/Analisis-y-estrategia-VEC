import streamlit as st
import pandas as pd
from seo_utils import (
    filtrar_contenidos_con_potencial,
    generar_keywords_por_cluster
)

st.set_page_config(page_title="Análisis SEO y Estrategia de Contenidos", layout="wide")
st.title("🔍 Análisis SEO + Estrategia de Contenidos")

# Subida de archivos
st.sidebar.header("Subir Archivos")
archivo_analisis = st.sidebar.file_uploader("📊 Archivo de Análisis (CSV o Excel)", type=["csv", "xlsx"])
archivo_auditoria = st.sidebar.file_uploader("📋 Archivo de Auditoría (CSV o Excel)", type=["csv", "xlsx"])

if archivo_analisis and archivo_auditoria:
    try:
        # Leer archivos según el formato
        if archivo_analisis.name.endswith(".csv"):
            df_analisis = pd.read_csv(archivo_analisis)
        else:
            df_analisis = pd.read_excel(archivo_analisis)

        if archivo_auditoria.name.endswith(".csv"):
            df_auditoria = pd.read_csv(archivo_auditoria)
        else:
            df_auditoria = pd.read_excel(archivo_auditoria)

        st.success("✅ Archivos cargados correctamente.")

        # Parte 1: Contenidos con potencial
        st.header("🚀 Contenidos con mayor potencial de optimización")
        df_potenciales = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.dataframe(df_potenciales, use_container_width=True)

        # Parte 2: Nuevas palabras clave por cluster
        st.header("🧠 Sugerencias de nuevas palabras clave por cluster")
        df_keywords = generar_keywords_por_cluster(df_analisis, df_auditoria)
        st.dataframe(df_keywords, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al procesar los archivos: {e}")
else:
    st.warning("📂 Por favor sube ambos archivos para comenzar.")
