import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def filtrar_contenidos_con_potencial(df):
    try:
        df['posición_promedio'] = pd.to_numeric(df['posición_promedio'], errors='coerce')
        df['volumen_de_búsqueda'] = pd.to_numeric(df['volumen_de_búsqueda'], errors='coerce')
        df['tráfico_estimado'] = pd.to_numeric(df['tráfico_estimado'], errors='coerce')
        df['dificultad'] = pd.to_numeric(df['dificultad'], errors='coerce')
        df['Leads 90 d'] = pd.to_numeric(df['Leads 90 d'], errors='coerce')

        df = df.dropna(subset=['posición_promedio', 'volumen_de_búsqueda', 'tráfico_estimado', 'dificultad', 'Leads 90 d'])

        df_filtrado = df[
            (df['posición_promedio'] > 3) &
            (df['posición_promedio'] <= 20) &
            (df['volumen_de_búsqueda'] >= 100) &
            (df['tráfico_estimado'] > 0) &
            (df['dificultad'] <= 80) &
            (df['Leads 90 d'] > 0)
        ]
        return df_filtrado
    except Exception as e:
        raise ValueError(f"Error en filtrado: {e}")

def generar_keywords_por_cluster(df):
    try:
        if 'palabra_clave' not in df.columns or 'Cluster' not in df.columns:
            raise ValueError("Faltan columnas necesarias: 'palabra_clave' o 'Cluster'")

        resultados = []
        clusters = df['Cluster'].dropna().unique()

        for cluster in clusters:
            sub_df = df[df['Cluster'] == cluster]
            subclusters = sub_df['Sub-cluster'].dropna().unique()

            for subcluster in subclusters:
                contenido = sub_df[sub_df['Sub-cluster'] == subcluster]['palabra_clave'].dropna().astype(str)
                if len(contenido) >= 2:
                    vectorizer = TfidfVectorizer()
                    X = vectorizer.fit_transform(contenido)
                    n_clusters = min(3, len(contenido))
                    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
                    kmeans.fit(X)
                    palabras = vectorizer.get_feature_names_out()

                    for i in range(n_clusters):
                        centroide = kmeans.cluster_centers_[i]
                        top_palabras_idx = centroide.argsort()[-3:][::-1]
                        top_palabras = [palabras[idx] for idx in top_palabras_idx]

                        for palabra in top_palabras:
                            resultados.append({
                                'Cluster': cluster,
                                'Sub-cluster': subcluster,
                                'palabra_clave_sugerida': palabra,
                                'Etapa del funnel': 'Consideración'
                            })
        return pd.DataFrame(resultados)

    except Exception as e:
        raise ValueError(f"Error al generar keywords: {e}")
