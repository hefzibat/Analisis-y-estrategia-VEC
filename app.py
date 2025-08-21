import streamlit as st
import pandas as pd
from io import BytesIO
from seo_utils import (
    filtrar_contenidos_con_potencial,
    generar_keywords_por_cluster
)

st.set_page_config(page_title="Análisis y estrategia de contenidos VEC", layout="wide")

st.title("🔍 Análisis de contenidos y estrategia SEO")

# Subida de archivos
st.sidebar.header("Carga tus archivos")
seo_file = st.sidebar.file_uploader("Archivo SEO", type=["csv", "xlsx"])
auditoria_file = st.sidebar.file_uploader("Archivo Auditoría", type=["csv", "xlsx"])

if seo_file and auditoria_file:
    try:
        if seo_file.name.endswith(".csv"):
            df_seo = pd.read_csv(seo_file)
        else:
            df_seo = pd.read_excel(seo_file)

        if auditoria_file.name.endswith(".csv"):
            df_auditoria = pd.read_csv(auditoria_file)
        else:
            df_auditoria = pd.read_excel(auditoria_file)

        # Normalización de nombres de columna
        df_seo.columns = df_seo.columns.str.strip().str.lower()
        df_auditoria.columns = df_auditoria.columns.str.strip().str.lower()

        # Parte 1: Contenidos con potencial
        st.header("📈 Parte 1: Contenidos con potencial de optimización")
        df_potencial = filtrar_contenidos_con_potencial(df_seo, df_auditoria)

        st.dataframe(df_potencial)

        def descargar_csv(df, nombre):
            buffer = BytesIO()
            df.to_csv(buffer, index=False)
            buffer.seek(0)
            return buffer

        st.download_button(
            label="📥 Descargar contenidos con potencial",
            data=descargar_csv(df_potencial, "contenidos_potenciales.csv"),
            file_name="contenidos_potenciales.csv",
            mime="text/csv"
        )

        # Parte 2: Generación de nuevas keywords
        st.header("💡 Parte 2: Nuevas keywords sugeridas")
        df_keywords = generar_keywords_por_cluster(df_potencial)

        st.dataframe(df_keywords)

        st.download_button(
            label="📥 Descargar nuevas keywords sugeridas",
            data=descargar_csv(df_keywords, "nuevas_keywords.csv"),
            file_name="nuevas_keywords.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Error al procesar los archivos: {e}")
