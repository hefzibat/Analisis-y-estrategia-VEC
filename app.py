import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial

st.title("🔍 Análisis y estrategia de contenido SEO")

st.markdown("""
Sube dos archivos:
1. 📈 **Análisis de contenido** (con posición, volumen, tráfico, etc.)
2. 📋 **Auditoría** (con leads, cluster, sub-cluster)
""")

archivo_analisis = st.file_uploader("📈 Archivo de análisis SEO", type=["csv", "xlsx"])
archivo_auditoria = st.file_uploader("📋 Archivo de auditoría de contenidos", type=["csv", "xlsx"])

if archivo_analisis and archivo_auditoria:
    try:
        if archivo_analisis.name.endswith(".csv"):
            df_analisis = pd.read_csv(archivo_analisis)
        else:
            df_analisis = pd.read_excel(archivo_analisis)

        if archivo_auditoria.name.endswith(".csv"):
            df_auditoria = pd.read_csv(archivo_auditoria)
        else:
            df_auditoria = pd.read_excel(archivo_auditoria)

        resultado = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)

        st.success("✅ Análisis completado")
        st.dataframe(resultado)

    except Exception as e:
        st.error(f"❌ Error: {e}")
