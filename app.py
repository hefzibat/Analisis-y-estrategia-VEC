import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_nuevas_keywords, generar_sugerencias_contenido

st.set_page_config(page_title="Análisis y Estrategia VEC", layout="wide")

st.title("🔍 Análisis y estrategia de contenidos VEC")

uploaded_file_analisis = st.file_uploader("📂 Sube el archivo de análisis (ej. Resultado_Final_Keywords.xlsx)", type=["xlsx", "csv"])
uploaded_file_auditoria = st.file_uploader("📂 Sube el archivo de auditoría (ej. VEC_Auditoría.xlsx)", type=["xlsx", "csv"])

if uploaded_file_analisis and uploaded_file_auditoria:
    try:
        df_analisis = pd.read_excel(uploaded_file_analisis) if uploaded_file_analisis.name.endswith('.xlsx') else pd.read_csv(uploaded_file_analisis)
        df_auditoria = pd.read_excel(uploaded_file_auditoria) if uploaded_file_auditoria.name.endswith('.xlsx') else pd.read_csv(uploaded_file_auditoria)

        # FASE 1
        st.header("1️⃣ Contenidos con potencial")
        df_filtrados = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.dataframe(df_filtrados)

        # FASE 2
        st.header("2️⃣ Nuevas keywords sugeridas por clúster")
        nuevas_keywords = generar_nuevas_keywords(df_filtrados)
        st.dataframe(nuevas_keywords)

        # FASE 3
        st.header("3️⃣ Sugerencias de títulos y canales")
        sugerencias = generar_sugerencias_contenido(nuevas_keywords)
        st.dataframe(sugerencias)

    except Exception as e:
        st.error(f"Ocurrió un error al procesar los archivos: {e}")
