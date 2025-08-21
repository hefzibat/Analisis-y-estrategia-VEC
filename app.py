import streamlit as st
from seo_utils import (
    cargar_datos, seleccionar_contenidos_para_optimizar,
    mostrar_clusters, generar_estrategia_contenido
)

st.set_page_config(page_title="SEO VEC - Estrategia de Contenidos", layout="wide")

st.title("🔍 SEO VEC - Estrategia de Contenidos")

# Parte 1: Selección de contenidos para optimizar
st.header("📌 Parte 1: Contenidos Recomendados para Optimizar")
df_optimizacion = cargar_datos()
if df_optimizacion is not None:
    seleccionados = seleccionar_contenidos_para_optimizar(df_optimizacion)
    st.dataframe(seleccionados)

# Parte 2: Visualización de clusters
st.header("🧠 Parte 2: Distribución por Clusters y Subclusters")
if df_optimizacion is not None:
    mostrar_clusters(df_optimizacion)

# Parte 3: Sugerencias de nueva estrategia de contenido
st.header("🪄 Parte 3: Estrategia de Contenido con Nuevas Palabras Clave")
if df_optimizacion is not None:
    generar_estrategia_contenido(df_optimizacion)