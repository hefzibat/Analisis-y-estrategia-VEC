import streamlit as st
import pandas as pd
from seo_utils import (
    filtrar_contenidos_con_potencial,
    generar_keywords_por_cluster
)

st.set_page_config(page_title="Análisis SEO y estrategia de contenidos", layout="wide")

st.title("🔍 Análisis SEO y estrategia de contenidos")

st.markdown("---")

# Subida de archivos
st.header("📁 Carga de archivos")

col1, col2 = st.columns(2)

with col1:
    archivo_analisis = st.file_uploader("Sube el archivo de análisis SEO (CSV o Excel)", type=["csv", "xls", "xlsx"])

with col2:
    archivo_auditoria = st.file_uploader("Sube el archivo de auditoría (CSV o Excel)", type=["csv", "xls", "xlsx"])

# Leer los archivos
def cargar_archivo(archivo):
    if archivo is None:
        return None
    if archivo.name.endswith(".csv"):
        return pd.read_csv(archivo)
    else:
        return pd.read_excel(archivo)

df_analisis = cargar_archivo(archivo_analisis)
df_auditoria = cargar_archivo(archivo_auditoria)

# Análisis Parte 1
st.markdown("### 1️⃣ Contenidos con potencial para optimizar")

if df_analisis is not None and df_auditoria is not None:
    try:
        df_resultados = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.success("✅ Contenidos con potencial identificados correctamente.")
        st.dataframe(df_resultados)
    except Exception as e:
        st.error(f"❌ Error al procesar los archivos: {e}")
else:
    st.info("🔎 Sube ambos archivos para comenzar el análisis.")

# Análisis Parte 2
st.markdown("### 2️⃣ Palabras clave sugeridas por cluster y etapa del funnel")

if df_analisis is not None and df_auditoria is not None:
    try:
        df_keywords = generar_keywords_por_cluster(df_analisis, df_auditoria)
        st.success("✅ Palabras clave sugeridas generadas correctamente.")
        st.dataframe(df_keywords)
    except Exception as e:
        st.error(f"❌ Error al procesar los archivos: {e}")
