import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_nuevas_keywords, generar_sugerencias_contenido

st.set_page_config(page_title="Análisis y Estrategia VEC", layout="wide")

st.title("📊 Análisis y estrategia de contenidos VEC")

# Parte 1: Subida de archivos
st.header("1. Cargar archivos")
archivo_analisis = st.file_uploader("📁 Carga el archivo de análisis SEO", type=["csv", "xlsx"])
archivo_auditoria = st.file_uploader("📁 Carga el archivo de auditoría de contenidos", type=["csv", "xlsx"])

if archivo_analisis and archivo_auditoria:
    try:
        df_analisis = pd.read_csv(archivo_analisis) if archivo_analisis.name.endswith("csv") else pd.read_excel(archivo_analisis)
        df_auditoria = pd.read_csv(archivo_auditoria) if archivo_auditoria.name.endswith("csv") else pd.read_excel(archivo_auditoria)

        st.success("Archivos cargados correctamente.")

        # Parte 2: Filtrado de contenidos con potencial
        st.header("2. Contenidos con potencial de optimización")
        df_filtrados = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.dataframe(df_filtrados, use_container_width=True)

        # Parte 3: Agrupamiento y sugerencias
        st.header("3. Nuevas keywords y estrategia de contenidos")
        df_clusterizado, nuevas_keywords = generar_nuevas_keywords(df_filtrados)
        df_sugerencias = generar_sugerencias_contenido(nuevas_keywords, df_clusterizado)

        st.dataframe(df_sugerencias, use_container_width=True)

        # Descarga
        st.download_button(
            label="📥 Descargar sugerencias en CSV",
            data=df_sugerencias.to_csv(index=False).encode("utf-8"),
            file_name="sugerencias_contenido.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Ocurrió un error al procesar los archivos: {e}")
