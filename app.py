import streamlit as st
import pandas as pd
from seo_utils import (
    filtrar_contenidos_con_potencial,
    generar_keywords_por_cluster
)

st.set_page_config(layout="wide")

st.title("🔍 Análisis y estrategia de contenidos")

uploaded_file = st.file_uploader("Sube tu archivo de análisis (.csv o .xlsx)", type=["csv", "xlsx"])
uploaded_auditoria = st.file_uploader("Sube tu archivo de auditoría (.csv o .xlsx)", type=["csv", "xlsx"])

if uploaded_file and uploaded_auditoria:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, engine='openpyxl')

        if uploaded_auditoria.name.endswith('.csv'):
            df_aud = pd.read_csv(uploaded_auditoria)
        else:
            df_aud = pd.read_excel(uploaded_auditoria, engine='openpyxl')

        # ✅ Parte 1
        st.subheader("1️⃣ Contenidos con potencial para optimizar")
        try:
            df_filtrado = filtrar_contenidos_con_potencial(df)
            st.write(df_filtrado)
        except Exception as e:
            st.error(f"❌ Error al procesar los archivos: {e}")

        # ✅ Parte 2
        st.subheader("2️⃣ Palabras clave sugeridas por cluster y etapa del funnel")
        try:
            df_keywords = generar_keywords_por_cluster(df_aud)
            st.write(df_keywords)
        except Exception as e:
            st.error(f"❌ Error al procesar los archivos: {e}")

    except Exception as e:
        st.error(f"❌ Error al leer los archivos: {e}")
