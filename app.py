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
# Parte 2: Ideas nuevas a partir de palabras clave externas
st.markdown("---")
st.subheader("Parte 2: Ideas nuevas a partir de palabras clave externas")

archivo_keywords = st.file_uploader("Carga tu archivo de palabras clave externas (opcional)", type=['csv', 'xlsx'])

if archivo_keywords is not None:
    try:
        if archivo_keywords.name.endswith('.csv'):
            df_keywords_externas = pd.read_csv(archivo_keywords)
        else:
            df_keywords_externas = pd.read_excel(archivo_keywords)
        
        df_ideas_externas = generar_ideas_con_keywords_externas(df_auditoria, df_keywords_externas, df_contenidos_potenciales)

        if not df_ideas_externas.empty:
            st.success(f"✅ {len(df_ideas_externas)} ideas nuevas generadas")
            st.dataframe(df_ideas_externas)
        else:
            st.warning("No se encontraron palabras clave nuevas que no estén ya usadas en los contenidos actuales.")

    except Exception as e:
        st.error(f"Error al procesar el archivo de palabras clave externas: {e}")
