import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    df_analisis = df_analisis.copy()
    df_auditoria = df_auditoria.copy()

    try:
        # Unir por URL (sin modificar nombres de columnas)
        df = pd.merge(df_analisis, df_auditoria, how='inner', on='URL')

        # Convertir columnas a numéricas con coerción de errores
        for col in ['posición_promedio', 'volumen_de_búsqueda', 'dificultad', 'tráfico_estimado', 'Leads 90 d']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Filtros
        df = df[df['posición_promedio'] > 3]
        df = df[df['posición_promedio'] <= 20]
        df = df[df['tráfico_estimado'] > 0]
        df = df[df['Leads 90 d'] > 0]

        # Calcular score
        df['score_optimización'] = (
            (21 - df['posición_promedio']) * 0.4 +
            df['volumen_de_búsqueda'] * 0.2 +
            (1 / (df['dificultad'] + 1)) * 0.1 +
            df['tráfico_estimado'] * 0.2 +
            df['Leads 90 d'] * 0.1
        )

        df = df.sort_values(by='score_optimización', ascending=False)

        columnas_resultado = [
            'URL', 'palabra_clave', 'posición_promedio', 'volumen_de_búsqueda',
            'dificultad', 'tráfico_estimado', 'tipo_de_contenido', 'Cluster',
            'Sub-cluster (si aplica)', 'Funnel', 'Leads 90 d', 'score_optimización'
        ]

        return df[columnas_resultado].head(40)
    
    except Exception as e:
        raise ValueError(f"Error en filtrar_contenidos_con_potencial: {e}")


def generar_keywords_por_cluster(df_analisis, df_auditoria, top_n=5):
    resultados = []

    try:
        agrupado = df_auditoria.groupby(['Cluster', 'Sub-cluster (si aplica)', 'Funnel'])

        for (cluster, subcluster, funnel), grupo in agrupado:
            urls = grupo['URL'].dropna().unique()
            textos = df_analisis[df_analisis['URL'].isin(urls)]['palabra_clave'].dropna().astype(str)

            if len(textos) < 2:
                continue

            vectorizer = TfidfVectorizer(stop_words='spanish')
            X = vectorizer.fit_transform(textos)
            kmeans = KMeans(n_clusters=min(len(textos), 3), random_state=0)
            kmeans.fit(X)

            terms = vectorizer.get_feature_names_out()
            order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]

            palabras_sugeridas = []
            for i in range(kmeans.n_clusters):
                for ind in order_centroids[i, :top_n]:
                    palabras_sugeridas.append(terms[ind])

            ranking = pd.Series(palabras_sugeridas).value_counts().head(top_n).items()

            for palabra, score in ranking:
                resultados.append({
                    'Cluster': cluster,
                    'Sub-cluster (si aplica)': subcluster,
                    'Funnel': funnel,
                    'Palabra clave sugerida': palabra
                })

        return pd.DataFrame(resultados)
    
    except Exception as e:
        raise ValueError(f"Error en generar_keywords_por_cluster: {e}")
