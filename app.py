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
        
# PARTE 2 - Generación de ideas desde keywords externas
st.markdown("---")
st.subheader("🔎 Parte 2: Generación de nuevas ideas de contenido")

archivo_keywords = st.file_uploader("📂 Sube el archivo con palabras clave externas (Google Ads, Semrush, etc)", type=["csv", "xlsx"])

if archivo_keywords is not None:
    if 'contenidos_actuales' in locals():
        try:
            nuevas_ideas_df = generar_ideas_desde_keywords_externas(archivo_keywords, contenidos_actuales)
            st.success("✅ Ideas de contenido generadas correctamente.")
            st.dataframe(nuevas_ideas_df)

            # Botón para descargar
            csv_ideas = nuevas_ideas_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Descargar ideas nuevas en CSV",
                data=csv_ideas,
                file_name="ideas_contenido_nuevas.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"⚠️ Error al generar ideas nuevas: {e}")
    else:
        st.warning("⚠️ Primero debes ejecutar la Parte 1 para tener los contenidos actuales.")
