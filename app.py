import streamlit as st
import pandas as pd
from seo_utils import (
    cargar_datos,
    filtrar_contenido_optimizacion,
    generar_sugerencias_keywords
)

st.set_page_config(page_title="Análisis y Estrategia SEO - VEC", layout="wide")
st.title("🔍 Análisis y Estrategia SEO - VEC")

# Subida de archivos
st.sidebar.header("Carga de archivos")
archivo_seo = st.sidebar.file_uploader("Sube el archivo SEO (.xlsx o .csv)", type=["xlsx", "csv"])
archivo_auditoria = st.sidebar.file_uploader("Sube el archivo de auditoría (.xlsx o .csv)", type=["xlsx", "csv"])

if archivo_seo and archivo_auditoria:
    try:
        df_seo, df_auditoria = cargar_datos(archivo_seo, archivo_auditoria)

        # PARTE 1: Contenido con potencial
        st.subheader("✅ Parte 1: Contenido con mayor potencial de optimización")
        contenido_potencial = filtrar_contenido_optimizacion(df_seo, df_auditoria)
        st.dataframe(contenido_potencial, use_container_width=True)

        csv_potencial = contenido_potencial.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Descargar tabla de contenidos con potencial",
            data=csv_potencial,
            file_name="contenido_con_potencial.csv",
            mime="text/csv",
        )

        # PARTE 2: Sugerencias de nuevas keywords
        st.subheader("✨ Parte 2: Sugerencias de nuevas keywords por clúster")
        sugerencias_keywords = generar_sugerencias_keywords(df_seo, df_auditoria)
        st.dataframe(sugerencias_keywords, use_container_width=True)

        csv_keywords = sugerencias_keywords.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Descargar tabla de nuevas keywords",
            data=csv_keywords,
            file_name="nuevas_keywords_por_cluster.csv",
            mime="text/csv",
        )

    except Exception as e:
        st.error(f"❌ Error al procesar los archivos: {str(e)}")
else:
    st.info("⬅️ Por favor, sube ambos archivos para comenzar el análisis.")
