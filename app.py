# app.py
import streamlit as st
import pandas as pd
from seo_utils import filtrar_contenidos_con_potencial, generar_nuevas_keywords, generar_sugerencias_contenido

def main():
    st.set_page_config(layout="wide")
    st.title("Análisis SEO y Estrategia de Contenidos")

    st.markdown("""
        Esta herramienta permite:
        1. Identificar contenidos con potencial de mejora.
        2. Generar nuevas keywords estratégicas.
        3. Obtener sugerencias de títulos y canales de difusión.
    """)

    archivo_analisis = st.file_uploader("Carga el archivo de resultados de keywords (Resultado_Final_Keywords.xlsx)", type=["csv", "xlsx"])
    archivo_auditoria = st.file_uploader("Carga el archivo de auditoría (VEC_Auditoría.xlsx)", type=["csv", "xlsx"])

    if archivo_analisis and archivo_auditoria:
        try:
            df_analisis = pd.read_excel(archivo_analisis) if archivo_analisis.name.endswith("xlsx") else pd.read_csv(archivo_analisis)
            df_auditoria = pd.read_excel(archivo_auditoria) if archivo_auditoria.name.endswith("xlsx") else pd.read_csv(archivo_auditoria)

            st.subheader("1⬛ Contenidos con potencial")
            df_filtrados = filtrar_contenidos_con_potencial(df_analisis, df_auditoria)
            st.dataframe(df_filtrados)

            st.subheader("2⃣ Nuevas keywords sugeridas")
            df_keywords = generar_nuevas_keywords(df_filtrados)
            st.dataframe(df_keywords)

            st.subheader("3⃣ Sugerencias de contenido y canales")
            df_sugerencias = generar_sugerencias_contenido(df_keywords)
            st.dataframe(df_sugerencias)

        except Exception as e:
            st.error(f"Ocurrió un error al procesar los archivos: {e}")

if __name__ == "__main__":
    main()
