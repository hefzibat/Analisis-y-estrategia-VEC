# Contenido corregido de seo_utils.py

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize

# -------------------------
# FUNCION 1: Contenidos con potencial
# -------------------------
def filtrar_contenidos_con_potencial(df_keywords, df_auditoria):
    try:
        # Convertir columnas numéricas de auditoría a float
        for col in ['Número de visitas', 'Rebote %', 'Leads 90 d', 'CTR']:
            if col in df_auditoria.columns:
                df_auditoria[col] = pd.to_numeric(df_auditoria[col], errors='coerce')

        # Unir por URL (respetando nombres reales)
        df = pd.merge(df_keywords, df_auditoria, left_on='url', right_on='URL', how='inner')

        # Agregar columna 'etapa_funnel'
        condiciones = [
            (df['posición_promedio'] > 20),
            (df['posición_promedio'] <= 20) & (df['posición_promedio'] > 10),
            (df['posición_promedio'] <= 10)
        ]
        valores = ['TOFU', 'MOFU', 'BOFU']
        df['etapa_funnel'] = np.select(condiciones, valores, default='TOFU')

        # Guardar df con columna etapa_funnel para futuras funciones
        return df
    except Exception as e:
        raise RuntimeError(f"Error al procesar los archivos: {e}")

# -------------------------
# FUNCION 2: Nuevas palabras clave por cluster y etapa
# -------------------------
def generar_keywords_sugeridas(df_combinado):
    try:
        # Agrupar por Cluster y etapa_funnel
        resultados = []
        for (cluster, etapa), grupo in df_combinado.groupby(['Cluster', 'etapa_funnel']):
            textos = grupo['palabra_clave'].astype(str).tolist()
            if not textos:
                continue
            vectorizer = TfidfVectorizer()
            X = vectorizer.fit_transform(textos)
            kmeans = KMeans(n_clusters=min(5, len(textos)), random_state=0).fit(X)
            grupo['cluster_keywords'] = kmeans.labels_
            top_keywords = []
            for i in range(kmeans.n_clusters):
                indices = np.where(kmeans.labels_ == i)
                palabras = X[indices].sum(axis=0).A1
                top_n = np.argsort(palabras)[-5:][::-1]
                terms = [vectorizer.get_feature_names_out()[j] for j in top_n]
                top_keywords.append(', '.join(terms))

            resultados.append({
                'Cluster': cluster,
                'Etapa del Funnel': etapa,
                'Palabras clave sugeridas': top_keywords
            })

        return pd.DataFrame(resultados)
    except Exception as e:
        raise RuntimeError(f"Error al generar palabras clave: {e}")
