import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_keywords_por_cluster

st.set_page_config(page_title="Análisis SEO", layout="wide")
st.title("🔍 Análisis SEO y Estrategia de Contenidos")

# Carga de archivos
archivo_analisis = st.file_uploader("📄 Sube el archivo de análisis (CSV o Excel)", type=["csv", "xlsx"])
archivo_auditoria = st.file_uploader("📄 Sube el archivo de auditoría (CSV o Excel)", type=["csv", "xlsx"])

if archivo_analisis and archivo_auditoria:
    try:
        df_analisis = pd.read_csv(archivo_analisis) if archivo_analisis.name.endswith(".csv") else pd.read_excel(archivo_analisis)
        df_auditoria = pd.read_csv(archivo_auditoria) if archivo_auditoria.name.endswith(".csv") else pd.read_excel(archivo_auditoria)
    except Exception as e:
        st.error(f"❌ Error al leer los archivos: {e}")
        st.stop()

    # PARTE 1
    st.subheader("📊 Parte 1: Contenidos con mayor potencial de optimización")
    try:
        df_potencial = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.success("✅ Contenidos con potencial identificados")
        st.dataframe(df_potencial)
    except Exception as e:
        st.error(f"Error en Parte 1: {e}")

    # PARTE 2
    st.subheader("🧠 Parte 2: Nuevas palabras clave por cluster")
    try:
        columnas_texto = ['Título', 'Tipo de contenido', 'Eje Estratégico', 'Área temática']
        df_keywords = generar_keywords_por_cluster(df_auditoria, columnas_texto)
        st.success("✅ Nuevas keywords generadas")
        st.dataframe(df_keywords)
    except Exception as e:
        st.error(f"Error en Parte 2: {e}")
