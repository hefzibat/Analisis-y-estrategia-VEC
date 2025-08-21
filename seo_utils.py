import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


def estandarizar_columnas(df):
    mapping = {
        'url': ['url', 'URL', 'Url'],
        'palabra_clave': ['palabra_clave', 'PALABRA CLAVE', 'palabra clave', 'Palabra Clave'],
        'posicion': ['posición promedio', 'posicion', 'Posición promedio', 'Posicion promedio', 'posición', 'posición_promedio'],
        'volumen': ['volumen', 'Volumen'],
        'dificultad': ['dificultad', 'Dificultad'],
        'trafico': ['tráfico', 'Trafico', 'tráfico estimado', 'Tráfico']
    }
    columnas_originales = df.columns.tolist()
    nuevas_columnas = {}
    for nueva, variantes in mapping.items():
        for variante in variantes:
            if variante in columnas_originales:
                nuevas_columnas[variante] = nueva
                break
    return df.rename(columns=nuevas_columnas)


def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    df_analisis = estandarizar_columnas(df_analisis)
    df_auditoria = estandarizar_columnas(df_auditoria)

    df_auditoria = df_auditoria[['url', 'cluster', 'subcluster']].drop_duplicates()
    df_analisis = df_analisis.merge(df_auditoria, on='url', how='left')

    for col in ['url', 'palabra_clave', 'posicion', 'volumen', 'dificultad', 'trafico']:
        if col not in df_analisis.columns:
            raise KeyError(f"Falta la columna requerida en df_analisis: {col}")

    df_filtrado = df_analisis[
        (df_analisis['posicion'] > 6) & (df_analisis['posicion'] <= 30) &
        (df_analisis['volumen'] > 100) &
        (df_analisis['trafico'] > 0)
    ].copy()

    df_filtrado['score'] = (
        (30 - df_filtrado['posicion']) * 0.4 +
        df_filtrado['volumen'] * 0.3 +
        df_filtrado['trafico'] * 0.2 -
        df_filtrado['dificultad'] * 0.1
    )

    return df_filtrado.sort_values(by='score', ascending=False).head(45)


def generar_nuevas_keywords(df_filtrado):
    tfidf = TfidfVectorizer(stop_words='spanish')
    X = tfidf.fit_transform(df_filtrado['palabra_clave'])
    kmeans = KMeans(n_clusters=5, random_state=0).fit(X)
    df_filtrado['nuevo_cluster'] = kmeans.labels_

    nuevas_keywords = df_filtrado.groupby('nuevo_cluster').apply(
        lambda x: {
            'cluster': x['cluster'].iloc[0] if 'cluster' in x else '',
            'subcluster': x['subcluster'].iloc[0] if 'subcluster' in x else '',
            'sugerencia': ' '.join(x['palabra_clave'].values[:3])
        }
    ).tolist()

    return nuevas_keywords


def generar_sugerencias_contenido(df_filtrado):
    sugerencias = []
    for _, fila in df_filtrado.iterrows():
        cluster = fila.get('cluster', '')
        subcluster = fila.get('subcluster', '')
        keyword = fila['palabra_clave']
        canal = 'Blog' if fila['volumen'] > 500 else 'Video'
        titulo = f"Cómo mejorar tu estrategia de {keyword} en {subcluster}"
        sugerencias.append({
            'cluster': cluster,
            'subcluster': subcluster,
            'palabra_clave': keyword,
            'canal': canal,
            'titulo_sugerido': titulo
        })
    return sugerencias
