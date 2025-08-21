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

# Descargar stopwords si no están ya disponibles
nltk.download('stopwords')

def filtrar_contenidos_con_potencial(df_keywords, df_auditoria):
    try:
        df_keywords = df_keywords.copy()
        df_auditoria = df_auditoria.copy()

        df_auditoria = df_auditoria.rename(columns={
            'URL': 'url',
            'Leads 90 d': 'genera_leads'
        })

        df = pd.merge(df_keywords, df_auditoria, how='left', on='url')

        columnas_numericas = ['posición_promedio', 'volumen_de_búsqueda', 'tráfico_estimado', 'dificultad', 'genera_leads']
        for col in columnas_numericas:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df = df.dropna(subset=columnas_numericas)

        df['score'] = (
            (10 - df['posición_promedio']) * 0.25 +
            df['volumen_de_búsqueda'] * 0.15 +
            df['tráfico_estimado'] * 0.3 +
            (10 - df['dificultad']) * 0.2 +
            df['genera_leads'] * 0.1
        )

        df = df.sort_values(by='score', ascending=False)
        columnas = ['url', 'palabra_clave', 'posición_promedio', 'volumen_de_búsqueda',
                    'dificultad', 'tráfico_estimado', 'genera_leads', 'score', 'Cluster', 'Sub-cluster (si aplica)']
        columnas_presentes = [col for col in columnas if col in df.columns]
        return df[columnas_presentes]

    except Exception as e:
        raise ValueError(f"Error en filtrado: {str(e)}")


def generar_keywords_por_cluster(df_keywords, df_auditoria, archivo_keywords_externas=None):
    try:
        df_keywords = df_keywords.copy()
        df_auditoria = df_auditoria.copy()

        df_auditoria = df_auditoria.rename(columns={
            'URL': 'url'
        })

        df = pd.merge(df_keywords, df_auditoria[['url', 'Cluster', 'Sub-cluster (si aplica)']], on='url', how='left')
        df.dropna(subset=['Cluster'], inplace=True)

        resultados = []

        for (cluster, subcluster), grupo in df.groupby(['Cluster', 'Sub-cluster (si aplica)']):
            corpus = grupo['palabra_clave'].dropna().astype(str).tolist()
            if len(corpus) < 2:
                continue

            vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=20)
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
