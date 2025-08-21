import streamlit as st
import pandas as pd
from seo_utils import generar_ideas_desde_keywords_externas

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

        # ✅ Guardar los datos en session_state
        st.session_state['df_contenidos_actuales'] = resultado
        st.session_state['df_auditoria'] = df_auditoria

        st.success("✅ Análisis completado")
        st.dataframe(resultado)

    except Exception as e:
        st.error(f"❌ Error: {e}")
        
# PARTE 2: Ideas de contenido con palabras clave externas
st.subheader("Parte 2: Ideas nuevas a partir de palabras clave externas")

archivo_keywords = st.file_uploader("Carga el archivo de palabras clave externas (AdWords)", type=["csv", "xlsx"])

if archivo_keywords is not None:
    try:
        if archivo_keywords.name.endswith(".csv"):
            df_keywords = pd.read_csv(archivo_keywords)
        else:
            df_keywords = pd.read_excel(archivo_keywords)
        
        st.success("Archivo de palabras clave cargado correctamente.")

        # Llama a la función con 3 argumentos
        df_ideas = generar_ideas_desde_keywords_externas(df_keywords, df_analisis, df_auditoria)

        st.write("Ideas nuevas de contenido basadas en las keywords externas:")
        st.dataframe(df_ideas)

    except Exception as e:
        st.error(f"⚠️ Error al generar ideas nuevas: {e}")
