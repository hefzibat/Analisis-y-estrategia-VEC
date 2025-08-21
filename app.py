import streamlit as st
import pandas as pd
from seo_utils import (
    filtrar_contenidos_con_potencial,
    generar_keywords_por_cluster
)

st.set_page_config(page_title="Análisis SEO Estratégico", layout="wide")

st.title("🔍 Análisis y estrategia SEO - VEC")

st.markdown("Cargue los archivos para comenzar el análisis:")

archivo_analisis = st.file_uploader("📄 Archivo de Análisis (Excel)", type=["xlsx"])
archivo_auditoria = st.file_uploader("📄 Archivo de Auditoría (CSV)", type=["csv"])

if archivo_analisis and archivo_auditoria:
    try:
        df_analisis = pd.read_excel(archivo_analisis)
        df_auditoria = pd.read_csv(archivo_auditoria)

        st.header("1️⃣ Contenidos con potencial para optimizar")
        try:
            df_contenidos = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
            st.success("✅ Análisis completado")
            st.dataframe(df_contenidos, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error en filtrado: {e}")

        st.header("2️⃣ Palabras clave sugeridas por cluster y etapa del funnel")
        try:
            df_keywords = generar_keywords_por_cluster(df_analisis, df_auditoria)
            st.success("✅ Sugerencias generadas")
            st.dataframe(df_keywords, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error en generación de keywords: {e}")

    except Exception as e:
        st.error(f"❌ Error al procesar los archivos: {e}")
else:
    st.warning("⚠️ Por favor, cargue ambos archivos para comenzar el análisis.")
