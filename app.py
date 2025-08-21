import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial

st.set_page_config(layout="wide")

st.title("🔍 Análisis de Contenidos SEO con Potencial de Optimización")

st.markdown("Carga los dos archivos para comenzar:")

archivo_analisis = st.file_uploader("📄 Archivo de análisis (ej: posiciones, tráfico, volumen)", type=["xlsx", "csv"])
archivo_auditoria = st.file_uploader("📄 Archivo de auditoría (ej: leads, clústers, etc.)", type=["xlsx", "csv"])

if archivo_analisis and archivo_auditoria:
    try:
        # Detectar extensión y cargar
        if archivo_analisis.name.endswith(".xlsx"):
            df_analisis = pd.read_excel(archivo_analisis)
        else:
            df_analisis = pd.read_csv(archivo_analisis)

        if archivo_auditoria.name.endswith(".xlsx"):
            df_auditoria = pd.read_excel(archivo_auditoria)
        else:
            df_auditoria = pd.read_csv(archivo_auditoria)

        # Aplicar análisis
        df_resultado = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)

        st.success("✅ Análisis completado. Aquí están los contenidos con mayor potencial de optimización:")
        st.dataframe(df_resultado, use_container_width=True)

        # Opción de descarga
        csv = df_resultado.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Descargar resultados como CSV",
            data=csv,
            file_name="contenidos_con_potencial.csv",
            mime="text/csv",
        )

    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.info("👈 Sube ambos archivos para iniciar el análisis.")
