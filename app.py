import streamlit as st
import pandas as pd
from seo_utils import (
    identificar_contenidos_con_potencial,
    generar_nuevas_keywords,
    sugerir_titulos_y_canales
)

st.set_page_config(page_title="Análisis SEO", layout="wide")

st.title("🔍 Análisis de contenidos SEO")

# Parte 0: Subida de archivos
st.header("Sube tus archivos")

archivo_analisis = st.file_uploader("Archivo de análisis (CSV o Excel)", type=["csv", "xlsx"])
archivo_auditoria = st.file_uploader("Archivo de auditoría (CSV o Excel)", type=["csv", "xlsx"])
uploaded_external_keywords = st.file_uploader("Opcional: Archivo de palabras clave externas (CSV o Excel)", type=["csv", "xlsx"])

# Leer archivos
def leer_archivo(archivo):
    if archivo.name.endswith('.csv'):
        return pd.read_csv(archivo)
    else:
        return pd.read_excel(archivo)

df_analisis = leer_archivo(archivo_analisis) if archivo_analisis else None
df_auditoria = leer_archivo(archivo_auditoria) if archivo_auditoria else None
df_keywords_externas = leer_archivo(uploaded_external_keywords) if uploaded_external_keywords else None

st.markdown("---")

# Parte 1: Contenidos con potencial de optimización
st.header("Parte 1: Identificar contenidos con potencial de optimización")
try:
    if df_analisis is not None and df_auditoria is not None:
        df_optimizables = identificar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.success("Contenidos con potencial identificados:")
        st.dataframe(df_optimizables)
    else:
        st.info("Por favor, sube ambos archivos para comenzar el análisis.")
except Exception as e:
    st.error(f"❌ Error en Parte 1: {e}")

st.markdown("---")

# Parte 2: Generar nuevas palabras clave
st.header("Parte 2: Generar nuevas palabras clave")

try:
    if df_analisis is not None and df_auditoria is not None:
        sugerencias_keywords = generar_nuevas_keywords(df_analisis, df_auditoria, df_keywords_externas)
        st.success("Sugerencias de palabras clave generadas.")
        st.dataframe(sugerencias_keywords)
    else:
        st.info("Para generar nuevas palabras clave, primero sube los archivos necesarios.")
except Exception as e:
    st.error(f"❌ Error en Parte 2: {e}")

st.markdown("---")

# Parte 3: Sugerencias de títulos y canales
st.header("Parte 3: Sugerencias de títulos y canales de distribución")

try:
    if df_analisis is not None and df_auditoria is not None:
        df_sugerencias = sugerir_titulos_y_canales(df_analisis, df_auditoria)
        st.success("Sugerencias generadas.")
        st.dataframe(df_sugerencias)
    else:
        st.info("Para generar sugerencias, asegúrate de subir los archivos necesarios.")
except Exception as e:
    st.error(f"❌ Error en Parte 3: {e}")
