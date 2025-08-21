import streamlit as st
import pandas as pd
from seo_utils import (
    filtrar_contenidos_con_potencial,
    generar_keywords_por_cluster
)

st.set_page_config(layout="wide")
st.title("🧠 Análisis de Contenidos y Estrategia SEO")

st.markdown("### 1️⃣ Subir archivos")
archivo_keywords = st.file_uploader("Sube el archivo de resultados de keywords", type=["csv", "xlsx"])
archivo_auditoria = st.file_uploader("Sube el archivo de auditoría de contenidos", type=["csv", "xlsx"])

def leer_archivo(archivo):
    if archivo.name.endswith(".csv"):
        return pd.read_csv(archivo)
    elif archivo.name.endswith(".xlsx"):
        return pd.read_excel(archivo)
    else:
        raise ValueError("Formato de archivo no soportado")

if archivo_keywords and archivo_auditoria:
    try:
        df_keywords = leer_archivo(archivo_keywords)
        df_auditoria = leer_archivo(archivo_auditoria)

        st.markdown("### ✅ Archivos cargados correctamente")

        st.markdown("### 1️⃣ Contenidos con potencial para optimizar")
        try:
            df_top = filtrar_contenidos_con_potencial(df_keywords, df_auditoria)
            st.dataframe(df_top[["palabra_clave", "url", "score", "Cluster", "Sub-cluster (si aplica)", "Etapa del funnel"]])
        except Exception as e:
            st.error(f"❌ Error al procesar los archivos: {e}")

        st.markdown("### 2️⃣ Palabras clave sugeridas por cluster y etapa del funnel")
        try:
            df_keywords_sugeridas = generar_keywords_por_cluster(df_top, df_auditoria)
            st.dataframe(df_keywords_sugeridas)
        except Exception as e:
            st.error(f"❌ Error al procesar los archivos: {e}")

    except Exception as e:
        st.error(f"❌ Error al cargar los archivos: {e}")
