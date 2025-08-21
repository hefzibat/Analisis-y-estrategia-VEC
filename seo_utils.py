import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# ------------------------------------------------------------------------
# ✅ PARTE 1 — NO TOCAR (100% restaurada como la tenías)
# ------------------------------------------------------------------------
def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    df = df_analisis.merge(df_auditoria, how='left', left_on='url', right_on='URL')

    df['score_optimizacion'] = (
        (1 / (df['posición_promedio'] + 1)) * df['volumen_de_búsqueda'] *
        (1 - df['dificultad']) * (df['tráfico_estimado'] + 1)
    )

    df = df[df['score_optimizacion'] > df['score_optimizacion'].median()]

    columnas_resultado = [
        'url', 'palabra_clave', 'posición_promedio', 'volumen_de_búsqueda',
        'dificultad', 'tráfico_estimado', 'tipo_de_contenido',
        'score_optimizacion', 'Cluster', 'Sub-cluster (si aplica)'
    ]

    return df[columnas_resultado]

# ------------------------------------------------------------------------
# ✅ PARTE 2 — Generación de nuevas keywords internas y externas
# ------------------------------------------------------------------------
def generar_keywords_por_cluster(df_analisis, df_auditoria, df_keywords_externas=None):
    try:
        # Normalizar columnas externas (solo usamos la primera como 'palabra_clave')
        if df_keywords_externas is not None:
            primera_col = df_keywords_externas.columns[0]
            df_keywords_externas = df_keywords_externas.rename(columns={primera_col: 'palabra_clave'})
            df_keywords_externas = df_keywords_externas[['palabra_clave']]

        # Unir las keywords internas y externas
        df_all_keywords = df_analisis[['url', 'palabra_clave']].copy()
        if df_keywords_externas is not None:
            df_all_keywords = pd.concat([df_all_keywords[['palabra_clave']], df_keywords_externas], ignore_index=True)
        else:
            df_all_keywords = df_all_keywords[['palabra_clave']]

        # Limpiar
        df_all_keywords.dropna(subset=['palabra_clave'], inplace=True)
        df_all_keywords['palabra_clave'] = df_all_keywords['palabra_clave'].astype(str)

        # Validar columnas esenciales en auditoría
        if not all(col in df_auditoria.columns for col in ['URL', 'Cluster', 'Sub-cluster (si aplica)']):
            raise ValueError("El archivo de auditoría debe contener las columnas 'URL', 'Cluster' y 'Sub-cluster (si aplica)'")

        # Mapear cluster desde auditoría
        mapeo = df_auditoria[['URL', 'Cluster', 'Sub-cluster (si aplica)']].drop_duplicates()
        df_mapeado = df_analisis.merge(mapeo, how='left', left_on='url', right_on='URL')

        resultados = []

        for (cluster, subcluster), grupo in df_mapeado.groupby(['Cluster', 'Sub-cluster (si aplica)']):
            palabras = grupo['palabra_clave'].dropna().astype(str).tolist()

            # Añadir también las externas
            if df_keywords_externas is not None:
                palabras += df_keywords_externas['palabra_clave'].dropna().astype(str).tolist()

            if len(palabras) < 2:
                continue

            vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=30)
            X = vectorizer.fit_transform(palabras)

            n_clusters = min(5, len(palabras))
            if n_clusters < 2:
                continue

            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
            kmeans.fit(X)

            for i, palabra in enumerate(palabras):
                resultados.append({
                    'Cluster': cluster,
                    'Subcluster': subcluster,
                    'palabra_clave_sugerida': palabra,
                    'grupo': int(kmeans.labels_[i])
                })

        return pd.DataFrame(resultados)

    except Exception as e:
        raise ValueError(f"Error en generación de keywords: {str(e)}")
