import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_keywords_por_cluster

st.set_page_config(page_title="Análisis SEO", layout="wide")
st.title("🔍 Herramienta de Análisis SEO por Clusters")

st.markdown("""
Sube dos archivos:
1. El archivo de **palabras clave y métricas SEO** (CSV o Excel).
2. El archivo de **auditoría de contenidos** con clusters y sub-clusters (CSV o Excel).
""")

# Carga de archivos
archivo_keywords = st.file_uploader("📄 Archivo de palabras clave y métricas", type=["csv", "xlsx"])
archivo_auditoria = st.file_uploader("📄 Archivo de auditoría de contenidos", type=["csv", "xlsx"])

# Lectura flexible de archivos
def leer_archivo(archivo):
    if archivo.name.endswith(".csv"):
        return pd.read_csv(archivo)
    else:
        return pd.read_excel(archivo)

if archivo_keywords and archivo_auditoria:
    try:
        df_keywords = leer_archivo(archivo_keywords)
        df_auditoria = leer_archivo(archivo_auditoria)

        st.success("✅ Archivos cargados correctamente.")

        # Parte 1: Contenidos con potencial
        st.header("1️⃣ Contenidos con potencial para optimizar")

        try:
            df_potencial = filtrar_contenidos_con_potencial(df_keywords, df_auditoria)
            st.dataframe(df_potencial, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error al procesar los archivos: {e}")

        # Parte 2: Keywords sugeridas
        st.header("2️⃣ Palabras clave sugeridas por cluster")

        try:
            df_keywords_sugeridas = generar_keywords_por_cluster(df_keywords, df_auditoria)
            st.dataframe(df_keywords_sugeridas, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error al generar keywords sugeridas: {e}")

    except Exception as e:
        st.error(f"❌ Error general al leer los archivos: {e}")
