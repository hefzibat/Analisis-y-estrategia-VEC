import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_keywords_por_cluster

st.set_page_config(page_title="Análisis SEO VEC", layout="wide")
st.title("🔍 Análisis de contenidos y estrategia SEO")

st.sidebar.header("Carga tus archivos")
archivo_keywords = st.sidebar.file_uploader("📄 Archivo de keywords (CSV o Excel)", type=["csv", "xlsx"])
archivo_auditoria = st.sidebar.file_uploader("📊 Archivo de auditoría (CSV o Excel)", type=["csv", "xlsx"])

def cargar_datos(archivo):
    if archivo is not None:
        nombre = archivo.name.lower()
        if nombre.endswith('.csv'):
            return pd.read_csv(archivo)
        elif nombre.endswith('.xlsx'):
            return pd.read_excel(archivo)
    return None

df_keywords = cargar_datos(archivo_keywords)
df_auditoria = cargar_datos(archivo_auditoria)

if df_keywords is not None and df_auditoria is not None:
    st.markdown("### 1️⃣ Contenidos con potencial para optimizar")
    try:
        df_filtrado = filtrar_contenidos_con_potencial(df_keywords, df_auditoria)
        st.success(f"{len(df_filtrado)} contenidos encontrados con alto potencial")
        st.dataframe(df_filtrado, use_container_width=True)
    except Exception as e:
        st.error(f"❌ Error al procesar los archivos: {e}")

    st.markdown("---")
    st.markdown("### 2️⃣ Palabras clave sugeridas por cluster y etapa del funnel")
    try:
        df_sugerencias = generar_keywords_por_cluster(df_keywords, df_auditoria)
        st.success(f"{len(df_sugerencias)} palabras clave sugeridas generadas")
        st.dataframe(df_sugerencias, use_container_width=True)
    except Exception as e:
        st.error(f"❌ Error al procesar los archivos: {e}")
else:
    st.warning("👈 Carga ambos archivos para iniciar el análisis.")
