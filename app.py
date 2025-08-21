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
        
# --- SECCIÓN PARTE 2: IDEAS NUEVAS DESDE ARCHIVO EXTERNO ---
st.header("🔍 Parte 2: Ideas nuevas de contenido desde keywords externas")

# Subir archivo de palabras clave externas
archivo_keywords_externas = st.file_uploader("📂 Sube el archivo de keywords externas (Google Ads / Semrush)", type=["csv", "xlsx"])

if archivo_keywords_externas is not None:
    try:
        if archivo_keywords_externas.name.endswith('.csv'):
            df_keywords_externas = pd.read_csv(archivo_keywords_externas)
        else:
            df_keywords_externas = pd.read_excel(archivo_keywords_externas)

        # Verifica si ya se cargaron las otras dos partes (contenidos actuales y auditoría)
        if 'df_contenidos_actuales' in st.session_state and 'df_auditoria' in st.session_state:
            with st.spinner("🔄 Generando ideas nuevas de contenido..."):
                df_ideas_nuevas = generar_ideas_desde_keywords_externas(
                    st.session_state['df_contenidos_actuales'],
                    df_keywords_externas,
                    st.session_state['df_auditoria']
                )
            st.success("✅ Ideas nuevas generadas exitosamente")

            st.subheader("📊 Ideas nuevas sugeridas")
            st.dataframe(df_ideas_nuevas)

            # Botón para descargar
            csv_ideas = df_ideas_nuevas.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Descargar ideas nuevas en CSV",
                data=csv_ideas,
                file_name="ideas_nuevas_desde_keywords_externas.csv",
                mime="text/csv"
            )
        else:
            st.warning("⚠️ Carga primero los archivos de análisis y auditoría en la Parte 1.")

    except Exception as e:
        st.error(f"⚠️ Error al generar ideas nuevas: {e}")
