import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_keywords_por_cluster

st.set_page_config(page_title="SEO Optimización VEC", layout="wide")
st.title("🚀 Análisis de Contenidos para SEO y Conversión")

st.markdown("""
Esta aplicación permite:
1. Detectar los contenidos con mayor potencial de optimización combinando análisis SEO + auditoría.
2. Generar nuevas ideas de palabras clave agrupadas por cluster y subcluster.
""")

# Cargar archivos
st.sidebar.header("Carga tus archivos")
archivo_seo = st.sidebar.file_uploader("Archivo de análisis SEO (CSV o Excel)", type=["csv", "xlsx"])
archivo_auditoria = st.sidebar.file_uploader("Archivo de auditoría (CSV o Excel)", type=["csv", "xlsx"])

# Procesar archivos
if archivo_seo and archivo_auditoria:
    if archivo_seo.name.endswith(".csv"):
        df_seo = pd.read_csv(archivo_seo)
    else:
        df_seo = pd.read_excel(archivo_seo)

    if archivo_auditoria.name.endswith(".csv"):
        df_auditoria = pd.read_csv(archivo_auditoria)
    else:
        df_auditoria = pd.read_excel(archivo_auditoria)

    # Merge de los archivos
    df_combined = pd.merge(df_seo, df_auditoria, how='inner', left_on='url', right_on='url')

    st.header("📌 Parte 1: Contenidos con potencial de optimización")
    df_opt = filtrar_contenidos_con_potencial(df_combined)
    st.dataframe(df_opt, use_container_width=True)
    st.download_button("📥 Descargar tabla de contenidos a optimizar", df_opt.to_csv(index=False), file_name="contenidos_optimizables.csv")

    st.header("🧠 Parte 2: Palabras clave sugeridas por cluster y subcluster")
    df_keywords = generar_keywords_por_cluster(df_combined)
    st.dataframe(df_keywords, use_container_width=True)
    st.download_button("📥 Descargar palabras clave sugeridas", df_keywords.to_csv(index=False), file_name="keywords_sugeridas.csv")

else:
    st.info("👈 Por favor, carga los dos archivos para iniciar el análisis.")
