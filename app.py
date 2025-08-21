import streamlit as st
import pandas as pd
from io import BytesIO
from seo_utils import (
    filtrar_contenidos_con_potencial,
)

st.set_page_config(layout="wide")
st.title("Análisis SEO y Estrategia de Contenidos")

st.sidebar.header("Carga de Archivos")
archivo_analisis = st.sidebar.file_uploader("Carga el archivo de Análisis", type=[".xlsx", ".csv"])
archivo_auditoria = st.sidebar.file_uploader("Carga el archivo de Auditoría", type=[".xlsx", ".csv"])

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

        # Validación de columnas requeridas en df_analisis
        columnas_esperadas = [
            'url', 'palabra_clave', 'posición_promedio', 'volumen_de_búsqueda',
            'dificultad', 'tráfico_estimado', 'tipo_de_contenido'
        ]
        for col in columnas_esperadas:
            if col not in df_analisis.columns:
                raise ValueError(f"Falta la columna requerida en df_analisis: {col}")

        st.subheader("1. Contenidos con potencial")
        df_filtrado = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.dataframe(df_filtrado[[
            'url', 'palabra_clave', 'posición_promedio', 'volumen_de_búsqueda',
            'dificultad', 'tráfico_estimado', 'tipo_de_contenido', 'cluster', 'subcluster', 'score'
        ]])

    except Exception as e:
        st.error(f"❌ Error: {e}")
