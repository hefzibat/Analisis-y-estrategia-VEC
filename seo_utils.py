import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

# ✔ Parte 1: IDENTIFICAR CONTENIDOS CON POTENCIAL DE OPTIMIZACIÓN (NO TOCAR)
def identificar_contenidos_con_potencial(df_analisis, df_auditoria):
    df_auditoria['genera_leads'] = df_auditoria['Leads 90 d'] > 0

    df_merged = pd.merge(
        df_analisis,
        df_auditoria,
        how='left',
        left_on='url',
        right_on='URL'
    )

    df_merged['score_optimizacion'] = (
        (1 / (df_merged['posición_promedio'] + 1)) * 0.25 +
        df_merged['volumen_de_búsqueda'].rank(pct=True) * 0.2 +
        (1 - df_merged['dificultad'].rank(pct=True)) * 0.2 +
        df_merged['tráfico_estimado'].rank(pct=True) * 0.15 +
        df_merged['genera_leads'].astype(int) * 0.2
    )

    df_top = df_merged.sort_values('score_optimizacion', ascending=False).head(45)
    columnas_resultado = [
        'palabra_clave', 'url', 'posición_promedio', 'volumen_de_búsqueda', 'dificultad',
        'tráfico_estimado', 'score_optimizacion', 'Cluster', 'Sub-cluster (si aplica)', 'tipo_de_contenido'
    ]
    return df_top[columnas_resultado]


# ✔ Parte 2: GENERAR NUEVAS PALABRAS CLAVE (MODIFICADA PARA COMBINAR INTERNAS Y EXTERNAS)
def generar_nuevas_keywords(df_analisis, df_auditoria, df_keywords_externas):
    # Combinar palabras clave internas con las externas
    df_keywords_externas.columns = df_keywords_externas.columns.str.strip()
    if 'palabra_clave' not in df_keywords_externas.columns:
        df_keywords_externas.rename(columns={df_keywords_externas.columns[0]: 'palabra_clave'}, inplace=True)

    df_keywords_externas = df_keywords_externas.dropna(subset=['palabra_clave'])
    df_keywords_externas['palabra_clave'] = df_keywords_externas['palabra_clave'].str.lower().str.strip()
    df_analisis['palabra_clave'] = df_analisis['palabra_clave'].str.lower().str.strip()

    # Combinar ambas fuentes
    df_combinado = pd.concat([df_analisis[['palabra_clave']], df_keywords_externas[['palabra_clave']]], ignore_index=True).drop_duplicates()

    # Agrupar por cluster y subcluster existentes
    df_temp = pd.merge(df_combinado, df_auditoria[['Cluster', 'Sub-cluster (si aplica)', 'palabra_clave']], on='palabra_clave', how='left')

    df_resultado = []
    for (cluster, subcluster), grupo in df_temp.groupby(['Cluster', 'Sub-cluster (si aplica)']):
        palabras = grupo['palabra_clave'].dropna().unique()
        if len(palabras) < 2:
            continue

        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(palabras)

        n_clusters = min(5, len(palabras))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)

        for i in range(n_clusters):
            cluster_palabras = [palabras[j] for j in range(len(palabras)) if labels[j] == i]
            for kw in cluster_palabras:
                df_resultado.append({
                    'Cluster': cluster,
                    'Subcluster': subcluster,
                    'Palabra Clave Sugerida': kw
                })

    return pd.DataFrame(df_resultado)
