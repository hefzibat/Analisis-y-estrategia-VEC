# seo_utils.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    df_analisis = df_analisis.copy()
    df_auditoria = df_auditoria.copy()

    df_analisis = df_analisis.rename(columns={
        'url': 'URL',
        'palabra_clave': 'Palabra clave',
        'posición_promedio': 'Posición promedio',
        'volumen_de_búsqueda': 'Volumen de búsqueda',
        'dificultad': 'Dificultad',
        'tráfico_estimado': 'Tráfico estimado'
    })

    df_auditoria = df_auditoria.rename(columns={
        "Leads 90 d *(esta se usará como 'genera_leads')": 'genera_leads'
    })

    df = pd.merge(df_analisis, df_auditoria, on='URL', how='inner')

    df = df[(df['Posición promedio'] >= 4) & (df['Posición promedio'] <= 20)]
    df = df[df['Volumen de búsqueda'] >= 100]
    df = df[df['genera_leads'] >= 1]

    df['Score'] = (
        (1 / df['Posición promedio']) * 0.4 +
        df['Volumen de búsqueda'].rank(pct=True) * 0.3 +
        df['Tráfico estimado'].rank(pct=True) * 0.3
    )

    df = df.sort_values(by='Score', ascending=False)
    return df

def generar_keywords_por_cluster(df_analisis, df_auditoria, df_keywords_externas=None):
    df = pd.merge(df_analisis, df_auditoria, left_on='url', right_on='URL', how='inner')

    # Procesar keywords internas
    df_internas = df[['palabra_clave', 'Cluster', 'Sub-cluster (si aplica)']].copy()
    df_internas = df_internas.rename(columns={'Sub-cluster (si aplica)': 'Subcluster'})

    if df_keywords_externas is not None:
        # Intentar detectar columnas relevantes automáticamente
        columnas = df_keywords_externas.columns.tolist()

        # Identificar la columna de palabra clave
        col_keyword = next((col for col in columnas if 'keyword' in col.lower() or 'palabra' in col.lower()), columnas[0])

        df_externas = df_keywords_externas[[col_keyword]].copy()
        df_externas = df_externas.rename(columns={col_keyword: 'palabra_clave'})

        # Añadir columnas vacías para merge posterior
        df_externas['Cluster'] = None
        df_externas['Subcluster'] = None

        # Unir ambas
        df_total = pd.concat([df_internas, df_externas], ignore_index=True)
    else:
        df_total = df_internas.copy()

    df_total = df_total.dropna(subset=['palabra_clave'])
    df_total = df_total.drop_duplicates(subset=['palabra_clave'])

    # Vectorización y clustering
    tfidf = TfidfVectorizer(stop_words='spanish')
    X = tfidf.fit_transform(df_total['palabra_clave'])
    kmeans = KMeans(n_clusters=5, random_state=0, n_init='auto')
    df_total['cluster_tfidf'] = kmeans.fit_predict(X)

    return df_total
