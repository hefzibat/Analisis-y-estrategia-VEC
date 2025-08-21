import streamlit as st
import pandas as pd
from seo_utils import (
    filtrar_contenidos_con_potencial,
    generar_keywords_por_cluster
)

st.set_page_config(page_title="Análisis y Estrategia SEO - VEC", layout="wide")
st.title("🔍 Análisis y Estrategia SEO - VEC")

st.sidebar.header("Carga de archivos")
archivo_seo = st.sidebar.file_uploader("Sube el archivo SEO (.xlsx o .csv)", type=["xlsx", "csv"])
archivo_auditoria = st.sidebar.file_uploader("Sube el archivo de auditoría (.xlsx o .csv)", type=["xlsx", "csv"])

def leer_archivo(archivo):
    if archivo.name.endswith(".csv"):
        return pd.read_csv(archivo)
    else:
        return pd.read_excel(archivo)

if archivo_seo and archivo_auditoria:
    try:
        df_seo = leer_archivo(archivo_seo)
        df_auditoria = leer_archivo(archivo_auditoria)

        # Parte 1
        st.subheader("✅ Parte 1: Contenidos con potencial")
        resultados_1 = filtrar_contenidos_con_potencial(df_seo, df_auditoria)
        st.dataframe(resultados_1, use_container_width=True)

        # Parte 2
        st.subheader("✨ Parte 2: Palabras clave sugeridas por cluster y etapa del funnel")
        resultados_2 = generar_keywords_por_cluster(df_seo, df_auditoria)
        st.dataframe(resultados_2, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al procesar los archivos: {str(e)}")

else:
    st.info("⬅️ Por favor, sube ambos archivos para comenzar el análisis.")
