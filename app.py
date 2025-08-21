import streamlit as st
import pandas as pd
from seo_utils import (
    filtrar_contenidos_con_potencial,
    generar_palabras_clave_sugeridas,
    generar_sugerencias_titulos_y_canales
)

st.set_page_config(layout="wide")
st.title("🔍 Análisis y estrategia de contenidos VEC")

st.markdown("Sube tus archivos para comenzar el análisis.")

archivo_keywords = st.file_uploader("📄 Carga el archivo de palabras clave (Excel o CSV)", type=["xlsx", "csv"])
archivo_auditoria = st.file_uploader("📄 Carga el archivo de auditoría (Excel o CSV)", type=["xlsx", "csv"])

if archivo_keywords and archivo_auditoria:
    try:
        if archivo_keywords.name.endswith(".xlsx"):
            df_keywords = pd.read_excel(archivo_keywords)
        else:
            df_keywords = pd.read_csv(archivo_keywords)

        if archivo_auditoria.name.endswith(".xlsx"):
            df_auditoria = pd.read_excel(archivo_auditoria)
        else:
            df_auditoria = pd.read_csv(archivo_auditoria)

        st.subheader("1️⃣ Contenidos con potencial para optimizar")
        df_filtrado = filtrar_contenidos_con_potencial(df_keywords, df_auditoria)
        st.dataframe(df_filtrado)

        st.subheader("2️⃣ Palabras clave sugeridas por cluster y etapa del funnel")
        df_palabras_sugeridas = generar_palabras_clave_sugeridas(df_filtrado)
        st.dataframe(df_palabras_sugeridas)

        st.subheader("3️⃣ Sugerencias de títulos y canales")
        df_sugerencias = generar_sugerencias_titulos_y_canales(df_palabras_sugeridas)
        st.dataframe(df_sugerencias)

    except Exception as e:
        st.error(f"❌ Error al procesar los archivos: {e}")
