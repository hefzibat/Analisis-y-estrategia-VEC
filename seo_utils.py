import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


def filtrar_contenidos_con_potencial(df_keywords, df_auditoria):
    try:
        columnas_necesarias = [
            'url', 'palabra_clave', 'posición_promedio',
            'volumen_de_búsqueda', 'dificultad', 'tráfico_estimado', 'tipo_de_contenido'
        ]
        df_keywords = df_keywords[columnas_necesarias].copy()
        df_auditoria = df_auditoria.copy()

        # Asegurar tipos numéricos
        df_keywords['posición_promedio'] = pd.to_numeric(df_keywords['posición_promedio'], errors='coerce')
        df_keywords['volumen_de_búsqueda'] = pd.to_numeric(df_keywords['volumen_de_búsqueda'], errors='coerce')
        df_keywords['tráfico_estimado'] = pd.to_numeric(df_keywords['tráfico_estimado'], errors='coerce')
        df_keywords['dificultad'] = pd.to_numeric(df_keywords['dificultad'], errors='coerce')

        df_keywords.dropna(subset=['posición_promedio', 'volumen_de_búsqueda', 'tráfico_estimado', 'dificultad'], inplace=True)

        df_keywords = df_keywords[df_keywords['posición_promedio'] > 6]
        df_keywords = df_keywords[df_keywords['volumen_de_búsqueda'] > 100]
        df_keywords = df_keywords[df_keywords['tráfico_estimado'] > 20]
        df_keywords = df_keywords[df_keywords['dificultad'] <= 70]

        df_merge = pd.merge(
            df_keywords,
            df_auditoria,
            how='left',
            left_on='url',
            right_on='URL'
        )

        columnas_resultado = [
            'palabra_clave', 'posición_promedio', 'volumen_de_búsqueda',
            'dificultad', 'tráfico_estimado', 'tipo_de_contenido',
            'Título', 'Cluster', 'Sub-cluster', 'Etapa del funnel', 'Leads 90 d', 'Reciclable'
        ]

        return df_merge[columnas_resultado]
    except Exception as e:
        raise ValueError(f"Error en filtrado: {e}")


def generar_keywords_por_cluster(df_keywords, df_auditoria):
    try:
        df_keywords = df_keywords.copy()
        df_auditoria = df_auditoria.copy()

        df_merge = pd.merge(
            df_keywords,
            df_auditoria[['URL', 'Cluster', 'Sub-cluster']],
            how='left',
            left_on='url',
            right_on='URL'
        )

        df_merge.dropna(subset=['Cluster', 'Sub-cluster'], inplace=True)

        resultados = []
        for (cluster, subcluster), grupo in df_merge.groupby(['Cluster', 'Sub-cluster']):
            texto = " ".join(grupo['palabra_clave'].astype(str))
            tfidf = TfidfVectorizer(max_features=10, stop_words='spanish')
            X = tfidf.fit_transform([texto])
            palabras = tfidf.get_feature_names_out()
            for palabra in palabras:
                resultados.append({
                    'Cluster': cluster,
                    'Sub-cluster': subcluster,
                    'palabra_clave_sugerida': palabra,
                    'Etapa del funnel': 'Consideración'
                })

        return pd.DataFrame(resultados)
    except Exception as e:
        raise ValueError(f"Error en generación de keywords: {e}")
