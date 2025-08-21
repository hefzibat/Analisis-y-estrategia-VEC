import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import nltk
from nltk.corpus import stopwords

# Descargar stopwords si no están disponibles
try:
    stopwords.words('spanish')
except LookupError:
    nltk.download('stopwords')


def generar_keywords_por_cluster(df_keywords, df_auditoria, df_externas=None):
    try:
        df_keywords = df_keywords.copy()
        df_auditoria = df_auditoria.copy()

        df_auditoria = df_auditoria.rename(columns={
            'URL': 'url'
        })

        df = pd.merge(df_keywords, df_auditoria[['url', 'Cluster', 'Sub-cluster (si aplica)']], on='url', how='left')
        df.dropna(subset=['Cluster'], inplace=True)

        if df_externas is not None:
            df_externas = df_externas.copy()
            if 'palabra_clave' in df_externas.columns and 'Cluster' in df_externas.columns:
                df_externas['Sub-cluster (si aplica)'] = df_externas.get('Sub-cluster (si aplica)', '')
                df_externas['Fuente'] = 'externa'
                df['Fuente'] = 'interna'
                df = pd.concat([
                    df[['palabra_clave', 'Cluster', 'Sub-cluster (si aplica)', 'Fuente']],
                    df_externas[['palabra_clave', 'Cluster', 'Sub-cluster (si aplica)', 'Fuente']]
                ], ignore_index=True)
            else:
                raise ValueError("El archivo de keywords externas debe tener las columnas 'palabra_clave' y 'Cluster'")

        else:
            df['Fuente'] = 'interna'

        resultados = []

        for (cluster, subcluster), grupo in df.groupby(['Cluster', 'Sub-cluster (si aplica)']):
            corpus = grupo['palabra_clave'].dropna().astype(str).tolist()
            if len(corpus) < 2:
                continue

            vectorizer = TfidfVectorizer(stop_words=None, ngram_range=(1, 2), max_features=20)
            X = vectorizer.fit_transform(corpus)

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
