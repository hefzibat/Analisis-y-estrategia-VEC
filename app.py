import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_nuevas_keywords, generar_sugerencias_contenido

st.set_page_config(layout="wide")
st.title("🔍 Análisis y Estrategia de Contenidos - VEC")

st.markdown("""
Esta app permite identificar contenidos con mayor potencial de optimización, generar nuevas keywords por clúster y subclúster,
y crear una estrategia de contenidos alineada con la etapa del funnel.
""")

st.sidebar.header("📁 Subir Archivos")
archivo_analisis = st.sidebar.file_uploader("Archivo de Análisis de Keywords (CSV o XLSX)", type=["csv", "xlsx"])
archivo_auditoria = st.sidebar.file_uploader("Archivo de Auditoría de Contenidos (CSV o XLSX)", type=["csv", "xlsx"])

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

        st.success("Archivos cargados correctamente ✅")

        st.markdown("---")
        st.header("1️⃣ Contenidos con Potencial")
        df_filtrados = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.dataframe(df_filtrados)

        st.markdown("---")
        st.header("2️⃣ Nuevas Keywords Estratégicas")
        nuevas_keywords = generar_nuevas_keywords(df_filtrados)
        st.dataframe(nuevas_keywords)

        st.markdown("---")
        st.header("3️⃣ Sugerencias de Títulos y Canales")
        sugerencias = generar_sugerencias_contenido(nuevas_keywords)
        st.dataframe(sugerencias)

    except Exception as e:
        st.error(f"Ocurrió un error al procesar los archivos: {e}")
else:
    st.info("Por favor, sube ambos archivos para comenzar el análisis.")
