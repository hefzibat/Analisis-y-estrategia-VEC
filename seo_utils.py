import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import numpy as np

def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    try:
        df = df_analisis.merge(df_auditoria, left_on='url', right_on='URL', how='left')

        df['posición_promedio'] = pd.to_numeric(df['posición_promedio'], errors='coerce')
        df['volumen_de_búsqueda'] = pd.to_numeric(df['volumen_de_búsqueda'], errors='coerce')
        df['dificultad'] = pd.to_numeric(df['dificultad'], errors='coerce')
        df['tráfico_estimado'] = pd.to_numeric(df['tráfico_estimado'], errors='coerce')
        df['leads 90 d'] = pd.to_numeric(df['leads 90 d'], errors='coerce')

        df = df.dropna(subset=['posición_promedio', 'volumen_de_búsqueda', 'dificultad', 'tráfico_estimado'])

        df['score_optimización'] = (
            (1 / (df['posición_promedio'] + 1)) *
            df['volumen_de_búsqueda'] *
            (1 - df['dificultad'] / 100) *
            (df['tráfico_estimado'] + 1)
        )

        df_ordenado = df.sort_values(by='score_optimización', ascending=False)
        df_top = df_ordenado.head(45)

        columnas_resultado = [
            'url', 'palabra_clave', 'posición_promedio', 'volumen_de_búsqueda',
            'dificultad', 'tráfico_estimado', 'tipo_de_contenido', 'Cluster',
            'Sub-cluster (si aplica)', 'Etapa del funnel', 'leads 90 d', 'score_optimización'
        ]

        df_resultado = df_top[columnas_resultado].copy()

        return df_resultado

    except Exception as e:
        raise ValueError(f"Error en filtrado: {e}")

def generar_keywords_por_cluster(df_analisis, df_auditoria):
    try:
        df = df_analisis.merge(df_auditoria, left_on='url', right_on='URL', how='left')
        df.dropna(subset=['palabra_clave'], inplace=True)

        agrupado = df.groupby(['Cluster', 'Sub-cluster (si aplica)', 'Etapa del funnel'])

        resultados = []

        for (cluster, subcluster, funnel), grupo in agrupado:
            palabras = grupo['palabra_clave'].astype(str).tolist()
            corpus = [" ".join(palabras)]

            if not corpus[0].strip():
                continue

            vectorizer = TfidfVectorizer()
            X = vectorizer.fit_transform(corpus)

            num_clusters = min(1, X.shape[0])
            if num_clusters == 0:
                continue

            kmeans = KMeans(n_clusters=1, random_state=0, n_init='auto').fit(X)
            centroide = kmeans.cluster_centers_[0]

            similitudes = cosine_similarity(X, [centroide])
            top_n = min(5, len(palabras))

            palabras_importantes = [palabra for palabra, _ in Counter(palabras).most_common(top_n)]

            for palabra in palabras_importantes:
                resultados.append({
                    'Cluster': cluster,
                    'Sub-cluster (si aplica)': subcluster,
                    'Palabra clave sugerida': palabra,
                    'Etapa del funnel': funnel
                })

        return pd.DataFrame(resultados)

    except Exception as e:
        raise ValueError(f"Error en generación de keywords: {e}")
