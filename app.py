import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_nuevas_keywords, generar_sugerencias_contenido

st.set_page_config(layout="wide", page_title="Análisis SEO VEC")

st.title("🔍 Estrategia de Contenidos y Análisis SEO")
st.markdown("Carga tus archivos para comenzar:")

archivo_analisis = st.file_uploader("📄 Archivo de Análisis (keywords)", type=["xlsx"])
archivo_auditoria = st.file_uploader("📄 Archivo de Auditoría (cluster)", type=["xlsx"])

if archivo_analisis and archivo_auditoria:
    try:
        df_analisis = pd.read_excel(archivo_analisis)
        df_auditoria = pd.read_excel(archivo_auditoria)

        st.subheader("1️⃣ Contenidos con Potencial")
        df_filtrados = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.dataframe(df_filtrados)

        st.subheader("2️⃣ Nuevas Keywords por Cluster")
        df_clustering, nuevas_keywords = generar_nuevas_keywords(df_filtrados)
        st.write(nuevas_keywords)

        st.subheader("3️⃣ Sugerencias de Contenido")
        df_sugerencias = generar_sugerencias_contenido(nuevas_keywords, df_clustering)
        st.dataframe(df_sugerencias)

        # Exportar resultados
        with pd.ExcelWriter("resultado_vec_estrategia.xlsx") as writer:
            df_filtrados.to_excel(writer, sheet_name="Top Contenidos", index=False)
            df_sugerencias.to_excel(writer, sheet_name="Sugerencias", index=False)
        with open("resultado_vec_estrategia.xlsx", "rb") as file:
            st.download_button("📥 Descargar Excel completo", file, file_name="resultado_vec_estrategia.xlsx")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar los archivos: {e}")
