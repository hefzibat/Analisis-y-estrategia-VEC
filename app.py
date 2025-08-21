import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_keywords_por_cluster

st.set_page_config(page_title="Análisis SEO y Estrategia de Contenidos", layout="wide")

st.title("🔍 Análisis SEO y Estrategia de Contenidos")

st.markdown("## Carga el archivo de análisis interno (CSV o Excel)")
file_analisis = st.file_uploader("Cargar archivo de análisis", type=["csv", "xlsx"])

st.markdown("## Carga el archivo de auditoría interna (CSV o Excel)")
file_auditoria = st.file_uploader("Cargar archivo de auditoría", type=["csv", "xlsx"])

st.markdown("## Parte 2: Carga de keywords externas (opcional)")
file_keywords_externas = st.file_uploader("Cargar el archivo externo (CSV o Excel) con keywords", type=["csv", "xlsx"])

if file_analisis and file_auditoria:
    try:
        df_analisis = pd.read_csv(file_analisis) if file_analisis.name.endswith('.csv') else pd.read_excel(file_analisis)
        df_auditoria = pd.read_csv(file_auditoria) if file_auditoria.name.endswith('.csv') else pd.read_excel(file_auditoria)

        st.success("Archivos de análisis y auditoría cargados correctamente.")

        df_potencial = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)

        st.markdown("### 📈 Contenidos con mayor potencial")
        st.dataframe(df_potencial)

        if file_keywords_externas:
            try:
                df_keywords_externas = (
                    pd.read_csv(file_keywords_externas) 
                    if file_keywords_externas.name.endswith('.csv') 
                    else pd.read_excel(file_keywords_externas)
                )

                df_keywords_resultado = generar_keywords_por_cluster(
                    df_potencial, df_keywords_externas, df_auditoria
                )

                st.markdown("### 💡 Sugerencias combinadas de keywords por cluster y subcluster")
                st.dataframe(df_keywords_resultado)

            except Exception as e:
                st.error(f"Error al procesar el archivo de keywords externas: {e}")

    except Exception as e:
        st.error(f"Error al cargar archivos: {e}")
