import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_keywords_por_cluster

st.set_page_config(page_title="Análisis SEO VEC", layout="wide")

st.title("🔍 Análisis de Contenidos con Potencial SEO")

st.markdown("Carga los archivos de análisis y auditoría para comenzar:")

archivo_analisis = st.file_uploader("Archivo de análisis SEO (CSV o XLSX)", type=["csv", "xlsx"])
archivo_auditoria = st.file_uploader("Archivo de auditoría (CSV o XLSX)", type=["csv", "xlsx"])

if archivo_analisis and archivo_auditoria:
    try:
        # Leer los archivos según su tipo
        if archivo_analisis.name.endswith(".csv"):
            df_analisis = pd.read_csv(archivo_analisis)
        else:
            df_analisis = pd.read_excel(archivo_analisis)

        if archivo_auditoria.name.endswith(".csv"):
            df_auditoria = pd.read_csv(archivo_auditoria)
        else:
            df_auditoria = pd.read_excel(archivo_auditoria)

        st.success("Archivos cargados correctamente ✅")

        # PARTE 1: FILTRAR CONTENIDOS CON POTENCIAL
        st.subheader("1️⃣ Contenidos con mayor potencial de optimización")

        df_resultado = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.dataframe(df_resultado, use_container_width=True)

        # PARTE 2: GENERACIÓN DE NUEVAS KEYWORDS
        st.subheader("2️⃣ Palabras clave sugeridas por cluster y etapa del funnel")

        # Combinar los dataframes para pasar a la función
        df_analisis["url"] = df_analisis["url"].str.lower().str.strip()
        df_auditoria["URL"] = df_auditoria["URL"].str.lower().str.strip()
        df_combinado = pd.merge(df_analisis, df_auditoria, left_on="url", right_on="URL", how="inner")

        df_keywords = generar_keywords_por_cluster(df_combinado)
        st.dataframe(df_keywords, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al procesar los archivos: {e}")
