import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_nuevas_keywords, sugerir_contenidos

st.title("Análisis y Estrategia SEO VEC")

uploaded_analisis = st.file_uploader("Sube archivo de análisis", type=["csv", "xlsx"])
uploaded_auditoria = st.file_uploader("Sube archivo de auditoría", type=["csv", "xlsx"])

if uploaded_analisis and uploaded_auditoria:
    try:
        df_analisis = pd.read_excel(uploaded_analisis) if uploaded_analisis.name.endswith(".xlsx") else pd.read_csv(uploaded_analisis)
        df_auditoria = pd.read_excel(uploaded_auditoria) if uploaded_auditoria.name.endswith(".xlsx") else pd.read_csv(uploaded_auditoria)

        st.header("1️⃣ Contenidos con Potencial")
        df_filtrados = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.dataframe(df_filtrados)

        st.header("2️⃣ Agrupación de Nuevas Keywords")
        df_keywords = generar_nuevas_keywords(df_filtrados)
        st.dataframe(df_keywords)

        st.header("3️⃣ Sugerencias de Contenidos")
        df_sugerencias = sugerir_contenidos(df_keywords)
        st.dataframe(df_sugerencias)

    except Exception as e:
        st.error(f"Ocurrió un error al procesar los archivos: {e}")
else:
    st.info("Por favor, sube ambos archivos para comenzar.")
