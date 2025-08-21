import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_nuevas_keywords, generar_sugerencias_contenido

st.set_page_config(page_title="SEO Vec", layout="wide")
st.title("Estrategia SEO VEC")

df_ana = st.file_uploader("Archivo Análisis (keywords)", type=["csv", "xlsx"])
df_aud = st.file_uploader("Archivo Auditoría (cluster)", type=["csv", "xlsx"])

if df_ana and df_aud:
    try:
        df_analisis = pd.read_excel(df_ana) if df_ana.name.endswith(".xlsx") else pd.read_csv(df_ana)
        df_auditoria = pd.read_excel(df_aud) if df_aud.name.endswith(".xlsx") else pd.read_csv(df_aud)

        st.header("1. Contenido con Potencial")
        df_filtrado = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.dataframe(df_filtrado)

        st.header("2. Nuevas Keywords por Cluster")
        df_clustered, keywords_by_cluster = generar_nuevas_keywords(df_filtrado)
        st.write(keywords_by_cluster)

        st.header("3. Sugerencias de Contenido")
        df_sugs = generar_sugerencias_contenido(df_clustered)
        st.dataframe(df_sugs)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Carga ambos archivos para iniciar.")
