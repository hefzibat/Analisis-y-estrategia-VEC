import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    df = pd.merge(df_analisis, df_auditoria, how='left', left_on='url', right_on='URL')

    # Definir el score de optimización combinando métricas clave
    df['score_optimizacion'] = (
        df['volumen_de_búsqueda'].fillna(0) * 0.4 +
        df['tráfico_estimado'].fillna(0) * 0.3 +
        (1 / (df['posición_promedio'].fillna(100) + 1)) * 100 * 0.2 +
        df['Leads 90 d'].fillna(0) * 0.1
    )

    # Filtrar solo los contenidos con alto potencial
    df_filtrado = df[df['score_optimizacion'] > df['score_optimizacion'].quantile(0.6)]

    columnas_a_mostrar = [
        'url', 'palabra_clave', 'posición_promedio', 'volumen_de_búsqueda',
        'dificultad', 'tráfico_estimado', 'tipo_de_contenido',
        'Cluster', 'Sub-cluster (si aplica)', 'Leads 90 d', 'score_optimizacion'
    ]

    return df_filtrado[columnas_a_mostrar]


def generar_keywords_por_cluster(df_analisis, df_auditoria, df_keywords_externas=None):
    # Normalizar columnas necesarias
    df_analisis = df_analisis.rename(columns={
        df_analisis.columns[1]: 'palabra_clave',
        df_analisis.columns[0]: 'url'
    })

    # Merge con auditoría para obtener cluster y subcluster
    df = pd.merge(df_analisis, df_auditoria, how='left', left_on='url', right_on='URL')

    # Asegurar que no haya nulos en cluster y subcluster
    df['Cluster'] = df['Cluster'].fillna('Sin cluster')
    df['Sub-cluster (si aplica)'] = df['Sub-cluster (si aplica)'].fillna('Sin subcluster')

    # Agrupar keywords internas por cluster y subcluster
    keywords_por_grupo = df.groupby(['Cluster', 'Sub-cluster (si aplica)'])['palabra_clave'].apply(lambda x: ' '.join(x)).reset_index()

    # Si se subió un archivo externo de keywords
    if df_keywords_externas is not None and not df_keywords_externas.empty:
        try:
            # Intentar detectar y renombrar la primera columna como palabra_clave
            df_keywords_externas = df_keywords_externas.rename(columns={df_keywords_externas.columns[0]: 'palabra_clave'})
            df_keywords_externas['Cluster'] = 'Sugerencias externas'
            df_keywords_externas['Sub-cluster (si aplica)'] = 'Sugerencias externas'

            # Agrupar keywords externas
            keywords_externas_agrupadas = df_keywords_externas.groupby(['Cluster', 'Sub-cluster (si aplica)'])['palabra_clave'].apply(lambda x: ' '.join(x)).reset_index()

            # Combinar internas y externas
            keywords_por_grupo = pd.concat([keywords_por_grupo, keywords_externas_agrupadas], ignore_index=True)
        except Exception as e:
            print("⚠️ Error al procesar keywords externas:", e)

    # Generar nuevas keywords con TF-IDF por grupo
    nuevas_keywords = []
    for _, fila in keywords_por_grupo.iterrows():
        cluster = fila['Cluster']
        subcluster = fila['Sub-cluster (si aplica)']
        texto = fila['palabra_clave']

        try:
            vectorizer = TfidfVectorizer(max_features=10, stop_words='spanish')
            X = vectorizer.fit_transform([texto])
            keywords = vectorizer.get_feature_names_out()
            nuevas_keywords.append({
                'Cluster': cluster,
                'Sub-cluster (si aplica)': subcluster,
                'Nuevas keywords sugeridas': ', '.join(keywords)
            })
        except Exception as e:
            print(f"⚠️ Error al generar keywords para {cluster} / {subcluster}: {e}")

    return pd.DataFrame(nuevas_keywords)
