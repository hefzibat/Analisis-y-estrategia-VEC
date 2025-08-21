import streamlit as st
import pandas as pd
from io import BytesIO
from seo_utils import (
    filtrar_contenidos_potenciales,
    generar_keywords_sugeridas,
)

st.set_page_config(page_title="Análisis SEO y Estrategia de Contenidos", layout="wide")
st.title("🔍 Análisis de Contenidos y Estrategia SEO para VEC")

st.markdown("---")

# Carga de archivos
st.header("Paso 1: Subir Archivos")
seo_file = st.file_uploader("📥 Subir archivo SEO (.xlsx o .csv)", type=["xlsx", "csv"])
auditoria_file = st.file_uploader("📥 Subir archivo Auditoría (.xlsx o .csv)", type=["xlsx", "csv"])

if seo_file and auditoria_file:
    # Detectar tipo y cargar
    if seo_file.name.endswith(".csv"):
        df_seo = pd.read_csv(seo_file)
    else:
        df_seo = pd.read_excel(seo_file)

    if auditoria_file.name.endswith(".csv"):
        df_auditoria = pd.read_csv(auditoria_file)
    else:
        df_auditoria = pd.read_excel(auditoria_file)

    # Normalización de nombres de columnas
    df_seo.columns = df_seo.columns.str.strip().str.lower()
    df_auditoria.columns = df_auditoria.columns.str.strip().str.lower()

    st.success("Archivos cargados correctamente. ¡Listos para analizar!")

    if 'url' not in df_seo.columns or 'url' not in df_auditoria.columns:
        st.error("❌ Error: Uno de los archivos no contiene la columna 'url'. Verifica los nombres reales.")
    else:
        # Merge
        df_combined = pd.merge(df_seo, df_auditoria, on='url', how='inner')

        # Parte 1 - Contenidos con mayor potencial
        st.header("📊 Parte 1: Contenidos con mayor potencial de optimización")
        df_filtrado = filtrar_contenidos_potenciales(df_combined)
        st.dataframe(df_filtrado)

        # Parte 2 - Generación de nuevas keywords
        st.header("🧠 Parte 2: Sugerencias de nuevas palabras clave")
        df_sugerencias = generar_keywords_sugeridas(df_combined)
        st.dataframe(df_sugerencias)

        # Descargar sugerencias
        output = BytesIO()
        df_sugerencias.to_excel(output, index=False)
        output.seek(0)
        st.download_button(
            label="📥 Descargar sugerencias de keywords",
            data=output,
            file_name="sugerencias_keywords.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.info("⬆️ Sube los dos archivos para comenzar el análisis.")
