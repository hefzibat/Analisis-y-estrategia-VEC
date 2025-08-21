import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_keywords_por_cluster

st.title("Análisis SEO y Estrategia de Contenidos")

# Subida de archivos
archivo_analisis = st.file_uploader("Sube el archivo de análisis (CSV o XLSX)", type=["csv", "xlsx"])
archivo_auditoria = st.file_uploader("Sube el archivo de auditoría (CSV o XLSX)", type=["csv", "xlsx"])

if archivo_analisis and archivo_auditoria:
    try:
        if archivo_analisis.name.endswith('.csv'):
            df_analisis = pd.read_csv(archivo_analisis)
        else:
            df_analisis = pd.read_excel(archivo_analisis)

        if archivo_auditoria.name.endswith('.csv'):
            df_auditoria = pd.read_csv(archivo_auditoria)
        else:
            df_auditoria = pd.read_excel(archivo_auditoria)

        st.success("Archivos cargados correctamente.")

        if st.button("Filtrar contenidos con potencial"):
            resultado = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
            st.subheader("Contenidos con mayor potencial")
            st.dataframe(resultado)

        if st.button("Generar nuevas palabras clave por cluster"):
            df_merged = pd.merge(df_analisis, df_auditoria.rename(columns={"URL": "url"}), on="url", how="inner")
            resultado_kw = generar_keywords_por_cluster(df_merged)
            st.subheader("Palabras clave sugeridas")
            st.dataframe(resultado_kw)

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
