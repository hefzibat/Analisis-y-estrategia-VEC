import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_nuevas_keywords, generar_sugerencias

st.set_page_config(layout="wide")
st.title("Análisis SEO - Estrategia de Contenidos")

uploaded_analisis = st.file_uploader("Carga el archivo de resultados de keywords", type=[".xlsx", ".csv"])
uploaded_auditoria = st.file_uploader("Carga el archivo de auditoría de contenidos", type=[".xlsx", ".csv"])

if uploaded_analisis and uploaded_auditoria:
    try:
        if uploaded_analisis.name.endswith(".csv"):
            df_analisis = pd.read_csv(uploaded_analisis)
        else:
            df_analisis = pd.read_excel(uploaded_analisis)

        if uploaded_auditoria.name.endswith(".csv"):
            df_auditoria = pd.read_csv(uploaded_auditoria)
        else:
            df_auditoria = pd.read_excel(uploaded_auditoria)

        st.subheader("1. Contenidos con potencial")
        df_filtrado = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.dataframe(df_filtrado)

        st.subheader("2. Nuevas Keywords por Clúster")
        df_clusterizado, palabras_por_cluster = generar_nuevas_keywords(df_filtrado)
        st.dataframe(df_clusterizado)

        st.subheader("3. Sugerencias de Títulos y Canales")
        df_sugerencias = generar_sugerencias(df_clusterizado)
        st.dataframe(df_sugerencias)

        st.download_button("Descargar sugerencias en Excel", data=df_sugerencias.to_excel(index=False), file_name="sugerencias_seo.xlsx")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar los archivos: {e}")
else:
    st.info("Por favor, carga ambos archivos para iniciar el análisis.")
