import streamlit as st
import pandas as pd
from seo_utils import (
    cargar_datos,
    filtrar_contenidos_potenciales,
    generar_keywords_por_cluster,
)

st.set_page_config(layout="wide")

st.title("Análisis SEO y Estrategia de Contenidos")

# Carga de archivos
st.sidebar.header("Carga de archivos")
archivo_seo = st.sidebar.file_uploader("Sube el archivo de análisis SEO (CSV o Excel)", type=["csv", "xlsx"])
archivo_auditoria = st.sidebar.file_uploader("Sube el archivo de auditoría de contenidos (CSV o Excel)", type=["csv", "xlsx"])

if archivo_seo and archivo_auditoria:
    try:
        df_seo, df_auditoria = cargar_datos(archivo_seo, archivo_auditoria)

        # PARTE 1: Contenidos a Optimizar
        st.header("🔍 Parte 1: Contenidos con Potencial de Optimización")
        df_potenciales = filtrar_contenidos_potenciales(df_seo, df_auditoria)

        if not df_potenciales.empty:
            st.dataframe(df_potenciales)
            st.download_button(
                label="📥 Descargar contenidos a optimizar",
                data=df_potenciales.to_csv(index=False),
                file_name="contenidos_a_optimizar.csv",
                mime="text/csv"
            )
        else:
            st.warning("No se encontraron contenidos con potencial claro de optimización.")

        # PARTE 2: Nuevas Keywords por Cluster/Subcluster
        st.header("✨ Parte 2: Sugerencia de Nuevas Palabras Clave")
        nuevas_keywords = generar_keywords_por_cluster(df_potenciales)

        if not nuevas_keywords.empty:
            st.dataframe(nuevas_keywords)
            st.download_button(
                label="📥 Descargar nuevas keywords sugeridas",
                data=nuevas_keywords.to_csv(index=False),
                file_name="nuevas_keywords.csv",
                mime="text/csv"
            )
        else:
            st.info("No se pudieron generar sugerencias de keywords con los datos actuales.")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar los archivos: {e}")
else:
    st.info("Por favor, sube ambos archivos para comenzar.")
