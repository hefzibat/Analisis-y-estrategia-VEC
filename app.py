import streamlit as st
import pandas as pd
from io import BytesIO
from seo_utils import (
    filtrar_contenidos_con_potencial,
    generar_nuevas_keywords,
    generar_sugerencias_contenido
)

st.set_page_config(layout="wide")
st.title("Análisis SEO y Estrategia de Contenidos")

st.sidebar.header("Carga de Archivos")
archivo_analisis = st.sidebar.file_uploader("Carga el archivo de Análisis", type=[".xlsx", ".csv"])
archivo_auditoria = st.sidebar.file_uploader("Carga el archivo de Auditoría", type=[".xlsx", ".csv"])

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

        st.subheader("1. Contenidos con potencial")
        df_filtrado = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
        st.dataframe(df_filtrado[[
            "URL", "PALABRA CLAVE", "CLUSTER", "SUBCLUSTER", "VOLUMEN", "TRÁFICO", "DIFICULTAD", "GENERA LEADS", "SCORE"
        ]])

        st.subheader("2. Nuevas palabras clave")
        df_clusterizado, nuevas_keywords = generar_nuevas_keywords(df_filtrado)
        st.dataframe(df_clusterizado[["URL", "PALABRA CLAVE", "CLUSTER"]])

        st.subheader("3. Sugerencias de títulos y canales")
        df_sugerencias = generar_sugerencias_contenido(nuevas_keywords, df_clusterizado)
        st.dataframe(df_sugerencias)

        def generar_excel():
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df_filtrado.to_excel(writer, sheet_name="Contenidos Potenciales", index=False)
                df_clusterizado.to_excel(writer, sheet_name="Nuevas Keywords", index=False)
                df_sugerencias.to_excel(writer, sheet_name="Sugerencias", index=False)
            output.seek(0)
            return output

        st.download_button(
            label="Descargar resultados en Excel",
            data=generar_excel(),
            file_name="estrategia_contenidos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Ocurrió un error al procesar los archivos: {e}")
