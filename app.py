import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_nuevas_keywords, generar_sugerencias_contenido

st.set_page_config(layout="wide")
st.title("Análisis SEO + Estrategia de Contenidos")

# Subida de archivos
archivo_analisis = st.file_uploader("Sube archivo de análisis (CSV o Excel)", type=["csv", "xlsx"])
archivo_auditoria = st.file_uploader("Sube archivo de auditoría (CSV o Excel)", type=["csv", "xlsx"])

if archivo_analisis and archivo_auditoria:
    try:
        ext1 = archivo_analisis.name.split(".")[-1]
        ext2 = archivo_auditoria.name.split(".")[-1]

        df_analisis = pd.read_csv(archivo_analisis) if ext1 == "csv" else pd.read_excel(archivo_analisis)
        df_auditoria = pd.read_csv(archivo_auditoria) if ext2 == "csv" else pd.read_excel(archivo_auditoria)

        st.subheader("1. Contenidos con potencial de optimización")
        df_filtrado = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.dataframe(df_filtrado)

        st.subheader("2. Nuevas palabras clave por clúster")
        df_keywords, sugerencias_kw = generar_nuevas_keywords(df_filtrado)
        st.write(sugerencias_kw)

        st.subheader("3. Sugerencias de títulos y canales")
        df_sugerencias = generar_sugerencias_contenido(sugerencias_kw, df_keywords)
        st.dataframe(df_sugerencias)

    except Exception as e:
        st.error(f"Ocurrió un error al procesar los archivos: {e}")
