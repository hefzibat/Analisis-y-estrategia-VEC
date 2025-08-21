import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import defaultdict
import numpy as np

# ✔ PRIMERA FUNCION CORRECTA - NO TOCAR
def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    df = df_analisis.merge(df_auditoria, how='left', left_on='url', right_on='URL')

    df['score_optimizacion'] = (
        (1 / (df['posicion_promedio'] + 1)) * 0.3 +
        (df['volumen_de_busqueda'] / df['volumen_de_busqueda'].max()) * 0.2 +
        ((100 - df['dificultad']) / 100) * 0.1 +
        (df['tráfico_estimado'] / df['tráfico_estimado'].max()) * 0.2 +
        (df['Leads 90 d'] / df['Leads 90 d'].max()) * 0.2
    )

    df = df.sort_values(by='score_optimizacion', ascending=False)
    df_filtrado = df.head(45)

    columnas_resultado = [
        'url', 'palabra_clave', 'posicion_promedio', 'volumen_de_búsqueda',
        'dificultad', 'tráfico_estimado', 'tipo_de_contenido', 'score_optimizacion',
        'Cluster', 'Sub-cluster (si aplica)', 'Leads 90 d', 'Eje Estratégico'
    ]

    return df_filtrado[columnas_resultado]

# ✔ SEGUNDA FUNCION AJUSTADA PARA FUSIONAR KEYWORDS INTERNAS Y EXTERNAS
def generar_keywords_por_cluster(df_filtrado, df_keywords_externas=None):
    grouped = df_filtrado.groupby(['Cluster', 'Sub-cluster (si aplica)'])
    keywords_sugeridas = defaultdict(list)

    for (cluster, subcluster), group in grouped:
        corpus = group['palabra_clave'].dropna().astype(str).tolist()

        if not corpus:
            continue

        vectorizer = TfidfVectorizer(stop_words='spanish', max_features=20)
        tfidf_matrix = vectorizer.fit_transform(corpus)

        if tfidf_matrix.shape[0] < 2:
            top_keywords = vectorizer.get_feature_names_out()
        else:
            num_clusters = min(3, tfidf_matrix.shape[0])
            km = KMeans(n_clusters=num_clusters, random_state=42, n_init='auto')
            km.fit(tfidf_matrix)

            for i in range(num_clusters):
                cluster_center = km.cluster_centers_[i]
                top_indices = cluster_center.argsort()[::-1][:3]
                top_keywords = [vectorizer.get_feature_names_out()[j] for j in top_indices]
                keywords_sugeridas[(cluster, subcluster)].extend(top_keywords)

        if df_keywords_externas is not None:
            try:
                df_keywords_externas.columns = df_keywords_externas.columns.str.lower().str.strip()
                keyword_col = [col for col in df_keywords_externas.columns if "keyword" in col or "palabra" in col]
                if not keyword_col:
                    raise ValueError("No se encontró una columna de palabras clave en el archivo externo.")

                kw_col = keyword_col[0]
                corpus_externo = df_keywords_externas[kw_col].dropna().astype(str).tolist()
                vectorizer_ext = TfidfVectorizer(stop_words='spanish', max_features=20)
                tfidf_ext = vectorizer_ext.fit_transform(corpus_externo)
                top_ext_keywords = vectorizer_ext.get_feature_names_out()
                keywords_sugeridas[(cluster, subcluster)].extend(top_ext_keywords[:5])
            except Exception as e:
                print(f"Error procesando archivo externo: {e}")

    resultado = []
    for (cluster, subcluster), keywords in keywords_sugeridas.items():
        for kw in list(set(keywords)):
            resultado.append({
                'cluster': cluster,
                'subcluster': subcluster,
                'keyword_sugerida': kw
            })

    return pd.DataFrame(resultado)
