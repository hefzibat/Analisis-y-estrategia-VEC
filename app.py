import streamlit as st
import pandas as pd
from seo_utils import (
    filtrar_contenidos_con_potencial,
    generar_keywords_por_cluster
)

st.set_page_config(page_title="Análisis y Estrategia SEO - VEC", layout="wide")
st.title("🔍 Análisis y Estrategia SEO - VEC")

# Subida de archivos
st.sidebar.header("Carga de archivos")
archivo_seo = st.sidebar.file_uploader("Sube el archivo SEO (.xlsx)", type=["xlsx"])
archivo_auditoria = st.sidebar.file_uploader("Sube el archivo de auditoría (.csv o .xlsx)", type=["csv", "xlsx"])

if archivo_seo and archivo_auditoria:
    try:
        df_seo = pd.read_excel(archivo_seo)
        if archivo_auditoria.name.endswith('.csv'):
            df_auditoria = pd.read_csv(archivo_auditoria)
        else:
            df_auditoria = pd.read_excel(archivo_auditoria)

        # PARTE 1
        st.subheader("✅ 1️⃣ Contenidos con mayor potencial de optimización")
        df_potencial = filtrar_contenidos_con_potencial(df_seo, df_auditoria)
        st.dataframe(df_potencial, use_container_width=True)

        csv_potencial = df_potencial.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar tabla de contenidos con potencial",
            data=csv_potencial,
            file_name="contenido_con_potencial.csv",
            mime="text/csv"
        )

        # PARTE 2
        st.subheader("✨ 2️⃣ Palabras clave sugeridas por cluster y etapa del funnel")
        df_keywords = generar_keywords_por_cluster(df_seo, df_auditoria)
        st.dataframe(df_keywords, use_container_width=True)

        csv_keywords = df_keywords.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar tabla de nuevas keywords",
            data=csv_keywords,
            file_name="nuevas_keywords_por_cluster.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"❌ Error al procesar los archivos: {str(e)}")
else:
    st.info("⬅️ Por favor, sube ambos archivos para comenzar el análisis.")
