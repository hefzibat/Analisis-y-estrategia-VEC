import streamlit as st
import pandas as pd
from seo_utils import (
    filtrar_contenido_con_potencial,
    generar_nuevas_keywords,
    generar_estrategia_contenido
)

st.set_page_config(layout="wide")

st.title("🔍 Análisis y Estrategia de Contenidos SEO - VEC")

st.markdown("""
Esta aplicación te ayuda a identificar qué contenidos optimizar y sugiere una estrategia SEO basada en datos.
""")

# Subida de archivos
st.header("1. Cargar archivos")
seo_file = st.file_uploader("📥 Cargar archivo SEO (CSV o XLSX)", type=["csv", "xlsx"])
auditoria_file = st.file_uploader("📥 Cargar archivo de auditoría (CSV o XLSX)", type=["csv", "xlsx"])

if seo_file and auditoria_file:
    try:
        # Cargar archivo SEO
        if seo_file.name.endswith(".csv"):
            df_seo = pd.read_csv(seo_file)
        else:
            df_seo = pd.read_excel(seo_file)

        # Cargar archivo de auditoría
        if auditoria_file.name.endswith(".csv"):
            df_auditoria = pd.read_csv(auditoria_file)
        else:
            df_auditoria = pd.read_excel(auditoria_file)

        # Limpieza de columnas
        df_seo.columns = df_seo.columns.str.strip()
        df_auditoria.columns = df_auditoria.columns.str.strip()

        # Asegurar que 'URL' esté estandarizada a 'url'
        if "URL" in df_auditoria.columns:
            df_auditoria.rename(columns={"URL": "url"}, inplace=True)
        if "url" not in df_seo.columns:
            raise KeyError("Falta la columna 'url' en el archivo SEO.")
        if "url" not in df_auditoria.columns:
            raise KeyError("Falta la columna 'url' en el archivo de auditoría.")

        # Merge de ambos archivos
        df_combined = pd.merge(df_seo, df_auditoria, on="url", how="inner")

        st.success("✅ Archivos cargados correctamente y combinados")

        # Ejecutar análisis
        st.header("2. Resultados del Análisis")

        resultados = filtrar_contenido_con_potencial(df_combined)
        st.subheader("Contenidos con mayor potencial de optimización")
        st.dataframe(resultados)

        st.download_button("📥 Descargar contenidos con potencial", resultados.to_csv(index=False), "potencial_optimizar.csv", "text/csv")

        st.divider()

        nuevas_keywords = generar_nuevas_keywords(df_combined)
        st.subheader("Sugerencias de nuevas palabras clave")
        st.dataframe(nuevas_keywords)

        st.download_button("📥 Descargar nuevas keywords", nuevas_keywords.to_csv(index=False), "nuevas_keywords.csv", "text/csv")

        st.divider()

        estrategia = generar_estrategia_contenido(df_combined)
        st.subheader("Sugerencias de estrategia de contenido")
        st.dataframe(estrategia)

        st.download_button("📥 Descargar estrategia de contenido", estrategia.to_csv(index=False), "estrategia_contenido.csv", "text/csv")

    except Exception as e:
        st.error(f"Error al procesar los archivos: {e}")
