import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial

st.set_page_config(layout="wide")
st.title("Análisis SEO y Estrategia de Contenidos")

# --- SIDEBAR: Carga de Archivos ---
st.sidebar.header("Carga de Archivos")
archivo_analisis = st.sidebar.file_uploader("Carga el archivo de Análisis", type=[".xlsx", ".csv"])
archivo_auditoria = st.sidebar.file_uploader("Carga el archivo de Auditoría", type=[".xlsx", ".csv"])

# --- PROCESAMIENTO ---
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

        # Normalizar columnas: pasar todo a minúsculas y quitar espacios
        df_analisis.columns = df_analisis.columns.str.lower().str.strip()
        df_auditoria.columns = df_auditoria.columns.str.lower().str.strip()

        st.subheader("1. Contenidos con Potencial")
        df_resultado = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)

        st.dataframe(df_resultado)

    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.warning("Por favor, carga ambos archivos para comenzar el análisis.")
