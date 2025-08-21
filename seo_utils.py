import streamlit as st
import pandas as pd
from io import BytesIO
from seo_utils import filtrar_contenidos_con_potencial

st.set_page_config(layout="wide")
st.title("Análisis SEO y Estrategia de Contenidos")

# --- SIDEBAR: Carga de archivos ---
st.sidebar.header("Carga de Archivos")
archivo_analisis = st.sidebar.file_uploader("Carga el archivo de Análisis", type=[".xlsx", ".csv"])
archivo_auditoria = st.sidebar.file_uploader("Carga el archivo de Auditoría", type=[".xlsx", ".csv"])

# --- PROCESAMIENTO DE ARCHIVOS ---
if archivo_analisis and archivo_auditoria:
    try:
        # Cargar archivo de análisis
        if archivo_analisis.name.endswith(".csv"):
            df_analisis = pd.read_csv(archivo_analisis)
        else:
            df_analisis = pd.read_excel(archivo_analisis)

        # Mostrar columnas originales del archivo de análisis
        st.write("🔍 Columnas en archivo de análisis:")
        st.write(list(df_analisis.columns))

        # Cargar archivo de auditoría
        if archivo_auditoria.name.endswith(".csv"):
            df_auditoria = pd.read_csv(archivo_auditoria)
        else:
            df_auditoria = pd.read_excel(archivo_auditoria)

        # Mostrar columnas originales del archivo de auditoría
        st.write("🔍 Columnas en archivo de auditoría:")
        st.write(list(df_auditoria.columns))

        # --- ANÁLISIS PARTE 1 ---
        st.subheader("1. Contenidos con potencial")
        df_filtrado = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)

        st.dataframe(df_filtrado[[
            "URL", "PALABRA CLAVE", "CLUSTER", "SUBCLUSTER",
            "VOLUMEN", "TRÁFICO", "DIFICULTAD", "GENERA LEADS", "SCORE"
        ]])

    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.warning("Por favor, carga ambos archivos para comenzar el análisis.")
