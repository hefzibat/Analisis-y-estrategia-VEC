# app.py
import streamlit as st
import pandas as pd
from seo_utils import (
    cargar_datos,
    obtener_contenidos_para_optimizar,
    visualizar_clusters,
    generar_sugerencias_keywords
)

st.set_page_config(page_title="Estrategia SEO VEC", layout="wide")
st.title("🔍 Estrategia de Contenidos SEO - VEC")

st.sidebar.header("Carga de archivos")
archivo_keywords = st.sidebar.file_uploader("Sube el archivo de palabras clave (Excel)", type=["xlsx"])
archivo_auditoria = st.sidebar.file_uploader("Sube el archivo de auditoría de contenidos (Excel)", type=["xlsx"])

if archivo_keywords and archivo_auditoria:
    df = cargar_datos(archivo_keywords, archivo_auditoria)

    st.header("1. Contenidos con alto potencial de optimización")
    optimizables = obtener_contenidos_para_optimizar(df)
    st.write(optimizables)

    st.header("2. Visualización de clusters")
    visualizar_clusters(df)

    st.header("3. Sugerencias de nuevas keywords y canales")
    sugerencias = generar_sugerencias_keywords(df)
    st.dataframe(sugerencias)
else:
    st.warning("Por favor, sube ambos archivos para comenzar el análisis.")
