import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np

# ------------------------------
# FUNCIÓN 1: Filtrar contenidos con potencial
# ------------------------------

def filtrar_contenidos_con_potencial(df):
    # Normaliza nombres de columnas por si vienen con mayúsculas o espacios
    df.columns = df.columns.str.strip().str.lower()

    required_cols = ['url', 'palabra_clave', 'posición_promedio', 'volumen_de_búsqueda', 'dificultad', 'tráfico_estimado']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Falta la columna requerida: {col}")

    # Cálculo de un score combinado (puedes ajustar pesos si lo deseas)
    df['score_optimizacion'] = (
        (1 / (df['posición_promedio'] + 1)) * 0.4 + 
        (df['volumen_de_búsqueda'] / (df['volumen_de_búsqueda'].max() + 1)) * 0.3 +
        (df['tráfico_estimado'] / (df['tráfico_estimado'].max() + 1)) * 0.3
    )

    # Filtramos los que tienen más potencial: top 40 (ajustable)
    df_optimizables = df.sort_values(by='score_optimizacion', ascending=False).head(40).copy()

    return df_optimizables


# ------------------------------
# FUNCIÓN 2: Generar nuevas keywords por cluster y subcluster
# ------------------------------

def generar_keywords_por_cluster(df):
    df.columns = df.columns.str.strip().str.lower()

    # Verificamos que estén todas las columnas necesarias
    for col in ['palabra_clave', 'cluster', 'sub-cluster', 'tipo_de_contenido']:
        if col not in df.columns:
            raise ValueError(f"Falta la columna requerida: {col}")

    resultados = []

    # Agrupamos por cluster y sub-cluster
    agrupaciones = df.groupby(['cluster', 'sub-cluster'])

    for (cluster, subcluster), grupo in agrupaciones:
        palabras = grupo['palabra_clave'].dropna().astype(str).tolist()

        if len(palabras) < 2:
            continue

        # Vectorización TF-IDF
        vectorizer = TfidfVectorizer(stop_words='spanish', max_features=30)
        tfidf_matrix = vectorizer.fit_transform(palabras)
        vocabulario = vectorizer.get_feature_names_out()

        # Aplicamos clustering KMeans con número limitado de grupos
        n_clusters = min(3, len(palabras))  # para evitar errores con pocos datos
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
        kmeans.fit(tfidf_matrix)

        for i in range(n_clusters):
            indices = np.where(kmeans.labels_ == i)[0]
            cluster_palabras = [palabras[idx] for idx in indices]
            cluster_keywords = list(set(" ".join(cluster_palabras).split()))
            keywords_sugeridas = list(set([kw for kw in cluster_keywords if kw in vocabulario]))

            if keywords_sugeridas:
                resultados.append({
                    'Cluster': cluster,
                    'Subcluster': subcluster,
                    'Palabras clave sugeridas': ", ".join(keywords_sugeridas),
                    'Etapa del funnel': inferir_etapa_funnel(subcluster)
                })

    return pd.DataFrame(resultados)


# ------------------------------
# FUNCIÓN AUXILIAR: Inferir etapa del funnel (según subcluster)
# ------------------------------

def inferir_etapa_funnel(subcluster):
    subcluster = str(subcluster).lower()
    if any(x in subcluster for x in ['introducción', 'conceptos', 'qué es', 'tendencias', 'guía']):
        return 'TOFU'
    elif any(x in subcluster for x in ['estrategias', 'comparativa', 'tipos', 'herramientas']):
        return 'MOFU'
    elif any(x in subcluster for x in ['caso', 'servicio', 'beneficio', 'certificación']):
        return 'BOFU'
    else:
        return 'MOFU'
