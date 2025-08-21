import streamlit as st
import pandas as pd
from seo_utils import generar_keywords_por_cluster

st.set_page_config(page_title="Análisis SEO por Clúster", layout="wide")
st.title("🔍 Análisis SEO por Clúster y Sugerencia de Keywords")

st.markdown("""
Esta aplicación permite:
1. Analizar y priorizar contenidos existentes para optimización.
2. Generar nuevas palabras clave agrupadas por cluster y subcluster.
3. Combinar sugerencias internas y externas para plan de contenido.
""")

# -------------------------
# Carga de archivos
# -------------------------
st.sidebar.header("📁 Cargar archivos de entrada")
archivo_keywords = st.sidebar.file_uploader("Archivo de análisis de keywords (.csv o .xlsx)", type=["csv", "xlsx"])
archivo_auditoria = st.sidebar.file_uploader("Archivo de auditoría de contenidos (.csv o .xlsx)", type=["csv", "xlsx"])

if archivo_keywords and archivo_auditoria:
    try:
        if archivo_keywords.name.endswith('.csv'):
            df_keywords = pd.read_csv(archivo_keywords)
        else:
            df_keywords = pd.read_excel(archivo_keywords)

        if archivo_auditoria.name.endswith('.csv'):
            df_auditoria = pd.read_csv(archivo_auditoria)
        else:
            df_auditoria = pd.read_excel(archivo_auditoria)

        st.success("Archivos cargados correctamente.")
    except Exception as e:
        st.error(f"Error al cargar archivos: {str(e)}")
        st.stop()
else:
    st.info("Por favor, carga ambos archivos para comenzar.")
    st.stop()

# -------------------------
# Parte 1: Identificar contenidos a optimizar
# -------------------------
st.subheader("Parte 1: Identificar contenidos con potencial de optimización")

try:
    df_merged = pd.merge(
        df_keywords,
        df_auditoria.rename(columns={'URL': 'url'}),
        on='url',
        how='left'
    )

    df_merged['score_optimizacion'] = (
        df_merged['tráfico_estimado'].fillna(0) * 0.4 +
        df_merged['volumen_de_búsqueda'].fillna(0) * 0.3 +
        df_merged['posición_promedio'].rsub(100).fillna(0) * 0.2 +
        df_merged['leads 90 d'].fillna(0) * 0.1
    )

    df_top = df_merged.sort_values(by='score_optimizacion', ascending=False).head(40)

    st.markdown("### 📝 Contenidos prioritarios para optimizar")
    st.dataframe(df_top[[
        'url', 'palabra_clave', 'posición_promedio', 'volumen_de_búsqueda',
        'dificultad', 'tráfico_estimado', 'leads 90 d', 'Cluster',
        'Sub-cluster (si aplica)', 'tipo_de_contenido'
    ]])
except Exception as e:
    st.error(f"❌ Error en Parte 1: {str(e)}")

# -------------------------
# Parte 2: Generar nuevas palabras clave
# -------------------------
st.subheader("Parte 2: Generar nuevas palabras clave")
archivo_externo = st.file_uploader("Cargar archivo de palabras clave externas (opcional)", type=["csv", "xlsx"])

df_externas = None
if archivo_externo is not None:
    try:
        if archivo_externo.name.endswith('.csv'):
            df_externas = pd.read_csv(archivo_externo)
        else:
            df_externas = pd.read_excel(archivo_externo)
        st.success("Archivo de palabras clave externas cargado con éxito.")
    except Exception as e:
        st.error(f"Error al cargar archivo externo: {str(e)}")

if st.button("Generar palabras clave sugeridas"):
    try:
        resultados_keywords = generar_keywords_por_cluster(df_keywords, df_auditoria, df_externas)
        st.success("Palabras clave sugeridas generadas exitosamente.")
        st.dataframe(resultados_keywords)
    except Exception as e:
        st.error(f"❌ Error al generar keywords sugeridas: {str(e)}")
