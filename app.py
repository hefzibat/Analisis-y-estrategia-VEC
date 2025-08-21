import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_ideas_con_keywords_externas

st.title("🔍 Análisis y estrategia de contenido SEO")

st.markdown("""
Sube tus archivos:
1. 📈 **Análisis de contenido** (con posición, volumen, tráfico, etc.)
2. 📋 **Auditoría** (con leads, cluster, sub-cluster)
3. 🧠 **Palabras clave externas** (Google Ads, Semrush, etc. Opcional para nuevas ideas)
""")

archivo_analisis = st.file_uploader("📈 Archivo de análisis SEO", type=["csv", "xlsx"])
archivo_auditoria = st.file_uploader("📋 Archivo de auditoría de contenidos", type=["csv", "xlsx"])
archivo_keywords_externas = st.file_uploader("🧠 Archivo externo de palabras clave (opcional)", type=["csv", "xlsx"])

# Función para leer CSV o Excel
def cargar_csv_o_excel(archivo):
    if archivo.name.endswith('.csv'):
        return pd.read_csv(archivo)
    else:
        return pd.read_excel(archivo)

if archivo_analisis and archivo_auditoria:
    try:
        df_analisis = cargar_csv_o_excel(archivo_analisis)
        df_auditoria = cargar_csv_o_excel(archivo_auditoria)

        resultado = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.success("✅ Parte 1: Análisis completado")
        st.dataframe(resultado)

    except Exception as e:
        st.error(f"❌ Error en Parte 1: {e}")

    # PARTE 2: Ideas desde archivo externo (si se subió)
    if archivo_keywords_externas:
        st.subheader("💡 Parte 2: Ideas nuevas desde archivo externo de palabras clave")
        try:
            df_keywords_externas = cargar_csv_o_excel(archivo_keywords_externas)

            df_ideas_externas = generar_ideas_con_keywords_externas(
                df_analisis, df_auditoria, df_keywords_externas
            )

            if df_ideas_externas.empty:
                st.info("No se generaron ideas nuevas desde el archivo externo.")
            else:
                st.success("✅ Ideas nuevas generadas correctamente")
                st.dataframe(df_ideas_externas)

        except Exception as e:
            st.error(f"❌ Error en Parte 2: {e}")
