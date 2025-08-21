import streamlit as st
import pandas as pd
from seo_utils import (
    cargar_datos,
    filtrar_contenidos_con_potencial,
    generar_keywords_por_cluster
)

st.set_page_config(page_title="Análisis y Estrategia SEO - VEC", layout="wide")
st.title("📊 Análisis y Estrategia SEO - VEC")

# Subida de archivos
st.sidebar.header("Carga de archivos")
archivo_analisis = st.sidebar.file_uploader("🔍 Archivo de análisis SEO (.xlsx)", type=["xlsx"])
archivo_auditoria = st.sidebar.file_uploader("📋 Archivo de auditoría (.csv o .xlsx)", type=["csv", "xlsx"])

if archivo_analisis and archivo_auditoria:
    try:
        df_analisis, df_auditoria = cargar_datos(archivo_analisis, archivo_auditoria)

        # Parte 1: Contenidos con potencial
        st.subheader("✅ Parte 1: Contenidos con mayor potencial de optimización")
        df_filtrado = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.dataframe(df_filtrado, use_container_width=True)

        # Descarga
        st.download_button(
            label="⬇️ Descargar contenidos con potencial",
            data=df_filtrado.to_csv(index=False).encode("utf-8"),
            file_name="contenido_con_potencial.csv",
            mime="text/csv"
        )

        # Parte 2: Palabras clave sugeridas
        st.subheader("2️⃣ Palabras clave sugeridas por cluster y etapa del funnel")
        df_keywords = generar_keywords_por_cluster(df_filtrado)
        st.dataframe(df_keywords, use_container_width=True)

        st.download_button(
            label="⬇️ Descargar nuevas keywords",
            data=df_keywords.to_csv(index=False).encode("utf-8"),
            file_name="nuevas_keywords_por_cluster.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"❌ Error al procesar los archivos: {str(e)}")
else:
    st.info("📂 Por favor, sube ambos archivos para comenzar el análisis.")
