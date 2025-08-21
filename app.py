import streamlit as st
import pandas as pd
from io import StringIO
from seo_utils import filtrar_contenidos_con_potencial, generar_keywords_por_cluster

st.set_page_config(page_title="Análisis SEO por Clúster", layout="wide")

st.title("🔍 Análisis SEO y Sugerencia de Palabras Clave por Clúster")
st.markdown("Carga los archivos necesarios para identificar oportunidades de optimización y generar nuevas keywords agrupadas por temática.")

# Subida de archivos
st.sidebar.header("📂 Carga de archivos")
archivo_analisis = st.sidebar.file_uploader("Archivo de análisis (CSV o Excel)", type=["csv", "xlsx"])
archivo_auditoria = st.sidebar.file_uploader("Archivo de auditoría (CSV o Excel)", type=["csv", "xlsx"])

# Leer archivos
def leer_archivo(archivo):
    if archivo is None:
        return None
    nombre = archivo.name.lower()
    try:
        if nombre.endswith(".csv"):
            return pd.read_csv(archivo)
        elif nombre.endswith(".xlsx"):
            return pd.read_excel(archivo)
    except Exception as e:
        st.error(f"Error al leer el archivo {nombre}: {e}")
    return None

df_analisis = leer_archivo(archivo_analisis)
df_auditoria = leer_archivo(archivo_auditoria)

# Parte 1: Contenidos con mayor potencial de optimización
st.header("1️⃣ Contenidos con mayor potencial de optimización")

if df_analisis is not None and df_auditoria is not None:
    try:
        df_resultado = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.success("Análisis realizado correctamente.")
        st.dataframe(df_resultado)

        # Descargar CSV
        csv = df_resultado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name='contenidos_con_potencial.csv',
            mime='text/csv',
        )
    except Exception as e:
        st.error(f"❌ Error al procesar los archivos: {e}")

# Parte 2: Palabras clave sugeridas por cluster y etapa del funnel
st.header("2️⃣ Palabras clave sugeridas por cluster y etapa del funnel")

if df_analisis is not None and df_auditoria is not None:
    try:
        palabras_sugeridas = generar_keywords_por_cluster(df_analisis, df_auditoria)
        st.success("Palabras clave sugeridas generadas correctamente.")
        st.dataframe(palabras_sugeridas)

        # Descargar CSV
        csv = palabras_sugeridas.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name='palabras_sugeridas.csv',
            mime='text/csv',
        )
    except Exception as e:
        st.error(f"❌ Error al procesar los archivos: {e}")
