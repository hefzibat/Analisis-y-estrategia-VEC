import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial
from io import BytesIO

st.set_page_config(layout="wide")
st.title("Análisis SEO y Estrategia de Contenidos")

# --- SIDEBAR: Carga de Archivos ---
st.sidebar.header("Carga de Archivos")
archivo_analisis = st.sidebar.file_uploader("Carga el archivo de Análisis (keywords)", type=[".xlsx", ".csv"])
archivo_auditoria = st.sidebar.file_uploader("Carga el archivo de Auditoría (clusters)", type=[".xlsx", ".csv"])

# --- PROCESAMIENTO ---
if archivo_analisis and archivo_auditoria:
    try:
        # Leer archivo de análisis
        if archivo_analisis.name.endswith(".csv"):
            df_analisis = pd.read_csv(archivo_analisis)
        else:
            df_analisis = pd.read_excel(archivo_analisis)

        # Leer archivo de auditoría
        if archivo_auditoria.name.endswith(".csv"):
            df_auditoria = pd.read_csv(archivo_auditoria)
        else:
            df_auditoria = pd.read_excel(archivo_auditoria)

        # Diagnóstico de columnas antes del análisis
        st.write("🔍 Columnas en archivo de análisis:")
        st.write(list(df_analisis.columns))
        st.write("🔍 Columnas en archivo de auditoría:")
        st.write(list(df_auditoria.columns))

        # Ejecutar función de análisis
        df_filtrado = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)

        # Renombrar columnas para visualización
        df_vista = df_filtrado.rename(columns={
            "url": "URL",
            "palabra_clave": "Palabra clave",
            "cluster": "Cluster",
            "sub-cluster (si aplica)": "Subcluster",
            "volumen_de_búsqueda": "Volumen",
            "tráfico_estimado": "Tráfico",
            "dificultad": "Dificultad",
            "leads 90 d": "Genera Leads",
            "score": "Score"
        })

        st.subheader("1. Contenidos con Potencial para Optimización")
        st.dataframe(df_vista[[
            "URL", "Palabra clave", "Cluster", "Subcluster",
            "Volumen", "Tráfico", "Dificultad", "Genera Leads", "Score"
        ]])

    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.warning("Por favor, carga ambos archivos para comenzar el análisis.")
