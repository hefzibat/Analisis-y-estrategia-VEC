import streamlit as st
import pandas as pd
from seo_utils import (
    filtrar_contenidos_con_potencial,
    generar_palabras_clave_sugeridas,
    generar_sugerencias_titulos_y_canales,
)

st.set_page_config(page_title="Análisis SEO", layout="wide")

st.title("🔍 Análisis de Contenidos SEO para Optimización")

# Parte 1: Cargar archivos
st.markdown("### 📂 1. Carga de archivos")
archivo_keywords = st.file_uploader("Carga el archivo de resultados de keywords (XLSX)", type=["xlsx"])
archivo_auditoria = st.file_uploader("Carga el archivo de auditoría de contenidos (CSV o Excel)", type=["csv", "xlsx"])

# Validar que se hayan subido ambos archivos
if archivo_keywords is not None and archivo_auditoria is not None:
    try:
        df_keywords = pd.read_excel(archivo_keywords)
        if archivo_auditoria.name.endswith(".csv"):
            df_auditoria = pd.read_csv(archivo_auditoria)
        else:
            df_auditoria = pd.read_excel(archivo_auditoria)

        # Parte 1: Contenidos con potencial
        st.markdown("### 1️⃣ Contenidos con potencial para optimizar")
        df_contenido_potencial = filtrar_contenidos_con_potencial(df_keywords, df_auditoria)

        if not df_contenido_potencial.empty:
            st.dataframe(df_contenido_potencial)
        else:
            st.warning("No se encontraron contenidos con potencial.")

        # Parte 2: Palabras clave sugeridas
        st.markdown("### 2️⃣ Palabras clave sugeridas por cluster y etapa del funnel")
        df_palabras_sugeridas = generar_palabras_clave_sugeridas(df_contenido_potencial)

        if not df_palabras_sugeridas.empty:
            st.dataframe(df_palabras_sugeridas)
        else:
            st.warning("No se pudieron generar palabras clave sugeridas.")

        # Parte 3: Sugerencias de títulos y canales
        st.markdown("### 3️⃣ Sugerencias de títulos y canales")
        df_sugerencias = generar_sugerencias_titulos_y_canales(df_palabras_sugeridas)

        if not df_sugerencias.empty:
            st.dataframe(df_sugerencias)
        else:
            st.warning("No se generaron sugerencias de títulos y canales.")

    except Exception as e:
        st.error(f"❌ Error al procesar los archivos: {e}")

else:
    st.info("Por favor, carga ambos archivos para comenzar.")
