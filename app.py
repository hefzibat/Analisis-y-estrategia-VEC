import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_keywords_por_cluster

st.set_page_config(page_title="Análisis SEO", layout="wide")
st.title("🔍 Análisis SEO y Estrategia de Contenidos")

# 📁 Carga de archivos
st.sidebar.header("Sube tus archivos")
archivo_analisis = st.sidebar.file_uploader("Archivo de análisis (CSV o Excel)", type=["csv", "xlsx"])
archivo_auditoria = st.sidebar.file_uploader("Archivo de auditoría (CSV o Excel)", type=["csv", "xlsx"])
archivo_keywords_externas = st.sidebar.file_uploader("Palabras clave externas (opcional)", type=["csv", "xlsx"])

if archivo_analisis and archivo_auditoria:
    try:
        # Leer archivos
        df_analisis = pd.read_csv(archivo_analisis) if archivo_analisis.name.endswith('.csv') else pd.read_excel(archivo_analisis)
        df_auditoria = pd.read_csv(archivo_auditoria) if archivo_auditoria.name.endswith('.csv') else pd.read_excel(archivo_auditoria)
        df_keywords_externas = None
        if archivo_keywords_externas:
            df_keywords_externas = pd.read_csv(archivo_keywords_externas) if archivo_keywords_externas.name.endswith('.csv') else pd.read_excel(archivo_keywords_externas)

        # PARTE 1 – Contenidos con potencial
        st.subheader("📈 Parte 1: Contenidos con potencial de optimización")
        try:
            df_potencial = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
            st.success("Análisis completado.")
            st.dataframe(df_potencial)
        except Exception as e:
            st.error(f"Error en Parte 1: {str(e)}")

        # PARTE 2 – Nuevas keywords por cluster
        st.subheader("🧠 Parte 2: Sugerencia de nuevas keywords por cluster")
        try:
            df_keywords = generar_keywords_por_cluster(df_analisis, df_auditoria, df_keywords_externas)
            st.success("Generación de keywords completada.")
            st.dataframe(df_keywords)
        except Exception as e:
            st.error(f"Error en Parte 2: {str(e)}")

    except Exception as e:
        st.error(f"Error general al procesar los archivos: {str(e)}")

else:
    st.warning("Por favor sube el archivo de análisis y el de auditoría.")
