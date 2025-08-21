import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_keywords_por_cluster

st.title("Análisis de Contenidos SEO")

st.sidebar.header("Carga de archivos")

archivo_keywords = st.sidebar.file_uploader("Sube el archivo de palabras clave", type=["csv", "xlsx"])
archivo_auditoria = st.sidebar.file_uploader("Sube el archivo de auditoría", type=["csv", "xlsx"])

def cargar_archivo(archivo):
    if archivo is not None:
        if archivo.name.endswith('.csv'):
            return pd.read_csv(archivo)
        elif archivo.name.endswith('.xlsx'):
            return pd.read_excel(archivo)
    return None

df_keywords = cargar_archivo(archivo_keywords)
df_auditoria = cargar_archivo(archivo_auditoria)

if df_keywords is not None and df_auditoria is not None:
    st.success("Archivos cargados correctamente.")

    st.subheader("Parte 1: Contenidos con potencial de optimización")
    try:
        contenidos_potenciales = filtrar_contenidos_con_potencial(df_keywords, df_auditoria)
        st.dataframe(contenidos_potenciales)
    except Exception as e:
        st.error(f"❌ Error al filtrar contenidos: {e}")

    st.subheader("Parte 2: Palabras clave sugeridas por cluster")
    try:
        keywords_sugeridas = generar_keywords_por_cluster(df_keywords, df_auditoria)
        st.dataframe(keywords_sugeridas)
    except Exception as e:
        st.error(f"❌ Error al generar keywords sugeridas: {e}")
        st.subheader("Paso 3: Cargar archivo opcional de palabras clave externas")
archivo_keywords_externas = st.file_uploader("Carga aquí un CSV con palabras clave adicionales (1 columna)", type=["csv"], key="keywords_extra")
df_keywords_externas = None
if archivo_keywords_externas is not None:
    try:
        df_keywords_externas = pd.read_csv(archivo_keywords_externas)
        if df_keywords_externas.shape[1] != 1:
            st.error("El archivo de palabras clave externas debe tener solo una columna.")
            df_keywords_externas = None
    except Exception as e:
        st.error(f"Error al cargar el archivo de palabras clave externas: {e}")
