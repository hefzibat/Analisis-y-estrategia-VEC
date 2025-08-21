import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_keywords_por_cluster

st.set_page_config(page_title="Análisis SEO VEC", layout="wide")

st.title("🔍 Análisis de contenidos y estrategia SEO")

st.markdown("Carga los archivos necesarios para comenzar.")

col1, col2 = st.columns(2)

with col1:
    archivo_analisis = st.file_uploader("📄 Archivo de análisis", type=["csv", "xlsx", "xls"], key="analisis")
with col2:
    archivo_auditoria = st.file_uploader("📋 Archivo de auditoría", type=["csv", "xlsx", "xls"], key="auditoria")

def cargar_archivo(f):
    if f is None:
        return None
    if f.name.endswith(".csv"):
        return pd.read_csv(f)
    else:
        return pd.read_excel(f)

if archivo_analisis and archivo_auditoria:
    try:
        df_analisis = cargar_archivo(archivo_analisis)
        df_auditoria = cargar_archivo(archivo_auditoria)

        st.markdown("### 1️⃣ Contenidos con mayor potencial de optimización")
        df_filtrado = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.dataframe(df_filtrado, use_container_width=True)

        st.markdown("### 2️⃣ Palabras clave sugeridas por cluster y etapa del funnel")
        df_keywords = generar_keywords_por_cluster(df_analisis)
        st.dataframe(df_keywords, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al procesar los archivos: {e}")
