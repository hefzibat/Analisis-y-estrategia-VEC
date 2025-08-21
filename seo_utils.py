import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import defaultdict


def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    df_analisis = df_analisis.copy()
    df_auditoria = df_auditoria.copy()

    df_auditoria = df_auditoria.rename(columns={
        "Leads 90 d *(esta se usará como 'genera_leads')": "genera_leads"
    })

    df = pd.merge(df_analisis, df_auditoria, how="inner", left_on="url", right_on="URL")

    df['score'] = (
        (1 / (df['posición_promedio'] + 1)) * 0.4 +
        (df['volumen_de_búsqueda'] / (df['volumen_de_búsqueda'].max() + 1)) * 0.2 +
        (df['tráfico_estimado'] / (df['tráfico_estimado'].max() + 1)) * 0.2 +
        (df['genera_leads'] / (df['genera_leads'].max() + 1)) * 0.2
    )

    df_filtrado = df[df['score'] > df['score'].median()].copy()

    return df_filtrado


def generar_keywords_por_cluster(df, columnas_texto):
    df = df.copy()

    if 'Cluster' not in df.columns or 'Sub-cluster (si aplica)' not in df.columns:
        raise ValueError("Faltan columnas 'Cluster' o 'Sub-cluster (si aplica)' en el archivo de auditoría")

    if not set(columnas_texto).issubset(df.columns):
        raise ValueError(f"Las columnas de texto proporcionadas no existen en el DataFrame: {columnas_texto}")

    df['texto_completo'] = df[columnas_texto].fillna('').agg(' '.join, axis=1)

    resultados = defaultdict(list)

    for (cluster, subcluster), grupo in df.groupby(['Cluster', 'Sub-cluster (si aplica)']):
        textos = grupo['texto_completo'].values
        if len(textos) < 2:
            continue

        vectorizer = TfidfVectorizer(stop_words='spanish', max_features=50)
        X = vectorizer.fit_transform(textos)

        k = min(5, X.shape[0])
        modelo = KMeans(n_clusters=k, random_state=42, n_init='auto')
        modelo.fit(X)

        palabras = vectorizer.get_feature_names_out()
        orden_centroides = modelo.cluster_centers_.argsort()[:, ::-1]

        keywords = set()
        for i in range(k):
            for idx in orden_centroides[i, :3]:
                keywords.add(palabras[idx])

        resultados[(cluster, subcluster)] = list(keywords)

    df_resultado = pd.DataFrame([
        {'Cluster': c, 'Sub-cluster': s, 'Palabras clave sugeridas': ', '.join(kws)}
        for (c, s), kws in resultados.items()
    ])

    return df_resultado
