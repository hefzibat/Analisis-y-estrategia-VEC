import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_nuevas_keywords, generar_sugerencias_contenido

st.set_page_config(page_title="Análisis SEO VEC", layout="wide")
st.title("🔍 Estrategia de Contenidos - VEC")

st.markdown("Carga los archivos para comenzar el análisis.")

# Carga de archivos
archivo_analisis = st.file_uploader("Archivo de análisis SEO (CSV o XLSX)", type=["csv", "xlsx"])
archivo_auditoria = st.file_uploader("Archivo de auditoría (CSV o XLSX)", type=["csv", "xlsx"])

if archivo_analisis and archivo_auditoria:
    # Leer archivos
    df_analisis = pd.read_csv(archivo_analisis) if archivo_analisis.name.endswith(".csv") else pd.read_excel(archivo_analisis)
    df_auditoria = pd.read_csv(archivo_auditoria) if archivo_auditoria.name.endswith(".csv") else pd.read_excel(archivo_auditoria)

    # FASE 1: Filtrar contenidos con potencial
    st.subheader("🔎 Fase 1: Contenidos con potencial")
    df_filtrados = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
    st.dataframe(df_filtrados)

    # FASE 2: Generar nuevas keywords
    st.subheader("🧠 Fase 2: Nuevas keywords agrupadas")
    df_cluster, nuevas_keywords = generar_nuevas_keywords(df_filtrados)
    st.dataframe(df_cluster[["PALABRA CLAVE", "CLUSTER"]])

    # FASE 3: Sugerencias de contenido
    st.subheader("📢 Fase 3: Títulos y canales sugeridos")
    df_sugerencias = generar_sugerencias_contenido(nuevas_keywords, df_cluster)
    st.dataframe(df_sugerencias)

    # Botón de descarga
    st.download_button("📥 Descargar sugerencias en Excel", df_sugerencias.to_csv(index=False), file_name="sugerencias_contenido.csv", mime="text/csv")

else:
    st.info("Por favor carga ambos archivos para comenzar el análisis.")
