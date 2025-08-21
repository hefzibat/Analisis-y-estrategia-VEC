import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def generar_keywords_por_cluster(df_keywords, df_auditoria):
    try:
        df_keywords = df_keywords.copy()
        df_auditoria = df_auditoria.copy()

        df_auditoria = df_auditoria.rename(columns={'URL': 'url'})
        df = pd.merge(df_keywords, df_auditoria[['url', 'Cluster', 'Sub-cluster (si aplica)']], on='url', how='left')
        df.dropna(subset=['Cluster'], inplace=True)

        resultados = []

        for (cluster, subcluster), grupo in df.groupby(['Cluster', 'Sub-cluster (si aplica)']):
            corpus = grupo['palabra_clave'].dropna().astype(str).tolist()
            if len(corpus) < 2:
                continue

            vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=20)
            X = vectorizer.fit_transform(corpus)

            n_clusters = min(3, len(corpus))
            kmeans = KMeans(n_clusters=n_clusters, random_state=0, n_init=10)
            kmeans.fit(X)

            top_keywords = vectorizer.get_feature_names_out()
            for palabra in top_keywords:
                resultados.append({
                    'Cluster': cluster,
                    'Sub-cluster (si aplica)': subcluster,
                    'Palabra clave sugerida': palabra
                })

        return pd.DataFrame(resultados)

    except Exception as e:
        raise ValueError(f"Error en generación de keywords: {str(e)}")

def fusionar_keywords(df_internas, df_externas):
    if df_externas.shape[1] > 1:
        df_externas.columns = [col.lower() for col in df_externas.columns]
        df_externas.rename(columns={df_externas.columns[0]: 'palabra_clave'}, inplace=True)
    else:
        df_externas.columns = ['palabra_clave']

    df_externas['tipo'] = 'externa'
    df_internas['tipo'] = 'interna'
    return pd.concat([df_internas, df_externas], ignore_index=True)
