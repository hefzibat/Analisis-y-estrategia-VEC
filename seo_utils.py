import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    # Usa los nombres reales sin renombrar nada
    columnas_necesarias = ['url', 'palabra_clave', 'posición_promedio', 'volumen_de_búsqueda', 'dificultad', 'tráfico_estimado']
    for col in columnas_necesarias:
        if col not in df_analisis.columns:
            raise ValueError(f"Columna faltante en archivo de análisis: '{col}'")

    columnas_auditoria = ['URL', 'Leads 90 d *(esta se usará como \'genera_leads\')', 'Cluster', 'Sub-cluster (si aplica)', 'Tipo de contenido']
    for col in columnas_auditoria:
        if col not in df_auditoria.columns:
            raise ValueError(f"Columna faltante en archivo de auditoría: '{col}'")

    # Combinar ambos archivos por URL
    df = df_analisis.merge(df_auditoria, left_on='url', right_on='URL', how='inner')

    # Filtro básico de ejemplo
    df_filtrado = df[
        (df['posición_promedio'] > 5) &
        (df['posición_promedio'] <= 20) &
        (df['volumen_de_búsqueda'] > 100) &
        (df['tráfico_estimado'] > 0)
    ]

    return df_filtrado

def generar_keywords_por_cluster(df_analisis, df_auditoria, df_keywords_externas=None):
    if 'Cluster' not in df_auditoria.columns or 'Sub-cluster (si aplica)' not in df_auditoria.columns:
        raise ValueError("Las columnas 'Cluster' o 'Sub-cluster (si aplica)' no están en el archivo de auditoría")

    df = df_analisis.merge(df_auditoria, left_on='url', right_on='URL', how='inner')
    df = df.dropna(subset=['palabra_clave'])

    resultados = []
    for (cluster, subcluster), grupo in df.groupby(['Cluster', 'Sub-cluster (si aplica)']):
        tfidf = TfidfVectorizer(max_features=10)
        tfidf_matrix = tfidf.fit_transform(grupo['palabra_clave'].astype(str))
        palabras = tfidf.get_feature_names_out()
        for palabra in palabras:
            resultados.append({
                'Cluster': cluster,
                'Subcluster': subcluster,
                'Palabra clave sugerida': palabra,
                'Fuente': 'Interna'
            })

    if df_keywords_externas is not None and 'Keyword' in df_keywords_externas.columns:
        for keyword in df_keywords_externas['Keyword'].dropna().unique():
            resultados.append({
                'Cluster': 'Por clasificar',
                'Subcluster': 'Por clasificar',
                'Palabra clave sugerida': keyword,
                'Fuente': 'Externa'
            })

    return pd.DataFrame(resultados)
