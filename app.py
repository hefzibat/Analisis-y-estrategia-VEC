import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_keywords_por_cluster

st.title("Análisis SEO de Contenidos")

st.markdown("### 1. Carga tus archivos")
archivo_keywords = st.file_uploader("Sube el archivo de keywords (CSV)", type=["csv"])
archivo_auditoria = st.file_uploader("Sube el archivo de auditoría (XLSX)", type=["xlsx"])

if archivo_keywords and archivo_auditoria:
    df_keywords = pd.read_csv(archivo_keywords)
    df_auditoria = pd.read_excel(archivo_auditoria)

    st.markdown("### 2. Contenidos con potencial de optimización")
    try:
        df_filtrado = filtrar_contenidos_con_potencial(df_keywords, df_auditoria)
        st.dataframe(df_filtrado)
    except Exception as e:
        st.error(f"❌ Error al analizar contenidos con potencial: {e}")

    st.markdown("### 3. Keywords sugeridas por cluster")
    try:
        df_keywords_sugeridas = generar_keywords_por_cluster(df_keywords, df_auditoria)
        st.dataframe(df_keywords_sugeridas)
    except Exception as e:
        st.error(f"❌ Error al generar keywords sugeridas: {e}")
