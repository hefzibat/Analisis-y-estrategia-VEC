import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial

st.set_page_config(layout="wide")
st.title("🔍 Análisis de Contenidos para Optimización SEO")

st.markdown("Carga dos archivos:")
st.markdown("- El archivo de **Análisis SEO** (con columnas como `url`, `palabra_clave`, `posición_promedio`, etc.)")
st.markdown("- El archivo de **Auditoría de contenidos** (con columnas como `URL`, `Cluster`, `Leads 90 d`, etc.)")

archivo_analisis = st.file_uploader("📂 Cargar archivo de análisis (.csv o .xlsx)", type=["csv", "xlsx"])
archivo_auditoria = st.file_uploader("📂 Cargar archivo de auditoría (.csv o .xlsx)", type=["csv", "xlsx"])

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

        st.subheader("🔧 Archivos cargados correctamente")
        st.write("Filtrando contenidos con potencial…")

        try:
            df_resultado = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
            st.success("✅ Análisis completado")
            st.dataframe(df_resultado, use_container_width=True)

            st.download_button(
                label="📥 Descargar resultados como CSV",
                data=df_resultado.to_csv(index=False).encode("utf-8"),
                file_name="contenidos_con_potencial.csv",
                mime="text/csv"
            )

        except ValueError as ve:
            st.error(str(ve))

    except Exception as e:
        st.error(f"❌ Error al procesar los archivos: {e}")
