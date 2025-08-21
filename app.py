import streamlit as st
import pandas as pd
from seo_utils import (
    filtrar_contenidos_con_potencial,
    generar_keywords_sugeridas
)

# Subir archivos
st.title("Análisis SEO + Estrategia de Contenidos")

archivo_seo = st.file_uploader("Sube el archivo de análisis SEO (CSV o Excel)", type=["csv", "xlsx"])
archivo_auditoria = st.file_uploader("Sube el archivo de auditoría de contenidos", type=["csv", "xlsx"])

if archivo_seo and archivo_auditoria:
    try:
        # Leer archivos
        if archivo_seo.name.endswith('.csv'):
            df_seo = pd.read_csv(archivo_seo)
        else:
            df_seo = pd.read_excel(archivo_seo)

        if archivo_auditoria.name.endswith('.csv'):
            df_auditoria = pd.read_csv(archivo_auditoria)
        else:
            df_auditoria = pd.read_excel(archivo_auditoria)

        # Estandarizar nombres de columnas (minúsculas)
        df_seo.columns = df_seo.columns.str.lower()
        df_auditoria.columns = df_auditoria.columns.str.lower()

        # Merge seguro
        df_combined = pd.merge(df_seo, df_auditoria, how='inner', on='url')

        # Parte 1: Contenidos con potencial
        st.header("📈 Parte 1: Contenidos con potencial para optimización")
        df_resultado = filtrar_contenidos_con_potencial(df_combined)
        st.dataframe(df_resultado)

        # Parte 2: Keywords sugeridas
        st.header("🔍 Parte 2: Palabras clave sugeridas para contenidos nuevos")
        df_keywords = generar_keywords_sugeridas(df_combined)
        st.dataframe(df_keywords)

        # Opción de descarga
        st.download_button("Descargar tabla de palabras clave", df_keywords.to_csv(index=False), "keywords_sugeridas.csv", "text/csv")

    except Exception as e:
        st.error(f"Ocurrió un error procesando los archivos: {e}")
