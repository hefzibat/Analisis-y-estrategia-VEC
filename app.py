import streamlit as st
import pandas as pd
from seo_utils import analizar_contenidos

st.set_page_config(layout="wide")
st.title("🔍 Análisis SEO y Estrategia de Contenidos")

st.markdown("### 📂 Carga tus archivos:")
archivo_analisis = st.file_uploader("Archivo de análisis (CSV/XLSX):", type=["csv", "xlsx"])
archivo_auditoria = st.file_uploader("Archivo de auditoría (CSV/XLSX):", type=["csv", "xlsx"])

if archivo_analisis and archivo_auditoria:
    try:
        if archivo_analisis.name.endswith(".csv"):
            df_analisis = pd.read_csv(archivo_analisis)
        else:
            df_analisis = pd.read_excel(archivo_analisis)

        if archivo_auditoria.name.endswith(".csv"):
            df_auditoria = pd.read_csv(archivo_auditoria)
        else:
            df_auditoria = pd.read_excel(archivo_auditoria)

        st.markdown("### 🔍 Columnas en archivo de análisis:")
        st.write(list(df_analisis.columns))

        st.markdown("### 🔍 Columnas en archivo de auditoría:")
        st.write(list(df_auditoria.columns))

        try:
            resultados = analizar_contenidos(df_analisis, df_auditoria)

            st.markdown("### ✅ Contenidos con potencial de optimización")
            st.dataframe(resultados['contenido_potencial'].rename(columns={
                'url': 'URL',
                'palabra_clave': 'Keyword',
                'posición_promedio': 'Posición',
                'volumen_de_búsqueda': 'Volumen',
                'dificultad': 'Dificultad',
                'tráfico_estimado': 'Tráfico',
                'tipo_de_contenido': 'Tipo',
                'Cluster': 'Cluster',
                'Sub-cluster (si aplica)': 'Subcluster',
                'Leads 90 d': 'Leads',
                'Vigencia del contenido': 'Vigencia'
            }))

        except Exception as e:
            st.error(f"❌ Error en el análisis: {e}")

    except Exception as e:
        st.error(f"❌ Error al procesar los archivos: {e}")

else:
    st.info("Por favor, sube ambos archivos para comenzar el análisis.")
