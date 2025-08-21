import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np

# ------------------------ FUNCIÓN 1: FILTRAR CONTENIDOS CON POTENCIAL ------------------------

def filtrar_contenidos_con_potencial(df_seo, df_auditoria):
    df_seo = df_seo.copy()
    df_auditoria = df_auditoria.copy()

    df_seo.rename(columns=lambda x: x.strip().lower(), inplace=True)
    df_auditoria.rename(columns=lambda x: x.strip().lower(), inplace=True)

    # Renombrar columnas para uso interno (sin afectar nombres reales)
    df_seo.rename(columns={
        'url': 'url',
        'palabra_clave': 'palabra_clave',
        'posición_promedio': 'posicion',
        'volumen_de_búsqueda': 'volumen',
        'dificultad': 'dificultad',
        'tráfico_estimado': 'trafico'
    }, inplace=True)

    df_auditoria.rename(columns={
        'url': 'url',
        'leads 90 d': 'genera_leads',
        'tipo de contenido': 'tipo_contenido',
        'cluster': 'cluster',
        'sub-cluster (si aplica)': 'subcluster'
    }, inplace=True)

    df_auditoria['genera_leads'] = pd.to_numeric(df_auditoria['genera_leads'], errors='coerce').fillna(0)

    df_merged = pd.merge(df_seo, df_auditoria, on='url', how='inner')

    df_merged = df_merged[(df_merged['posicion'] > 4) & (df_merged['posicion'] <= 20)]
    df_merged = df_merged[df_merged['trafico'] > 0]
    df_merged = df_merged[df_merged['genera_leads'] > 0]

    df_merged['score'] = (1 / df_merged['posicion']) * np.log1p(df_merged['volumen']) * np.log1p(df_merged['trafico']) * (df_merged['genera_leads'] + 1)

    columnas_finales = ['url', 'palabra_clave', 'posicion', 'volumen', 'dificultad', 'trafico', 'genera_leads', 'tipo_contenido', 'cluster', 'subcluster', 'score']
    df_resultado = df_merged[columnas_finales].sort_values(by='score', ascending=False)

    return df_resultado


# ------------------------ FUNCIÓN 2: GENERAR SUGERENCIAS DE NUEVAS KEYWORDS ------------------------

def generar_keywords_por_cluster(df_seo, df_auditoria, top_n=5):
    df_seo = df_seo.copy()
    df_auditoria = df_auditoria.copy()

    df_seo.rename(columns=lambda x: x.strip().lower(), inplace=True)
    df_auditoria.rename(columns=lambda x: x.strip().lower(), inplace=True)

    df_merged = pd.merge(df_seo, df_auditoria, on='url', how='inner')

    if 'cluster' not in df_merged.columns or 'sub-cluster (si aplica)' not in df_merged.columns:
        raise ValueError("Faltan las columnas 'cluster' o 'sub-cluster (si aplica)' en el archivo de auditoría.")

    resultados = []

    grouped = df_merged.groupby(['cluster', 'sub-cluster (si aplica)'])

    for (cluster, subcluster), grupo in grouped:
        palabras = grupo['palabra_clave'].dropna().astype(str).tolist()

        if not palabras:
            continue

        vectorizer = TfidfVectorizer(stop_words='spanish', ngram_range=(1, 2))
        X = vectorizer.fit_transform(palabras)
        tfidf_scores = X.sum(axis=0).A1
        palabras_unicas = vectorizer.get_feature_names_out()

        ranking = sorted(zip(palabras_unicas, tfidf_scores), key=lambda x: x[1], reverse=True)[:top_n]

        for palabra, score in ranking:
            resultados.append({
                'Cluster': cluster,
                'Sub-cluster (si aplica)': subcluster,
                'Palabra clave sugerida': palabra,
                'Funnel': 'Consideración'  # Valor fijo por ahora
            })

    return pd.DataFrame(resultados)
