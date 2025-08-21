import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np

def encontrar_columna(df, posibles_nombres):
    for col in df.columns:
        for nombre in posibles_nombres:
            if col.strip().lower().replace("_", "").replace(" ", "").replace("-", "") == nombre.strip().lower().replace("_", "").replace(" ", "").replace("-", ""):
                return col
    return None

def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    # Nombres esperados
    nombres_palabra_clave = ['palabraclave']
    nombres_url = ['url']
    nombres_volumen = ['volumen']
    nombres_posicion = ['posicion']
    nombres_dificultad = ['dificultad']
    nombres_trafico = ['trafico']

    col_palabra_clave = encontrar_columna(df_analisis, nombres_palabra_clave)
    col_url = encontrar_columna(df_analisis, nombres_url)
    col_volumen = encontrar_columna(df_analisis, nombres_volumen)
    col_posicion = encontrar_columna(df_analisis, nombres_posicion)
    col_dificultad = encontrar_columna(df_analisis, nombres_dificultad)
    col_trafico = encontrar_columna(df_analisis, nombres_trafico)

    for col in [col_palabra_clave, col_url, col_volumen, col_posicion, col_dificultad, col_trafico]:
        if col is None:
            raise KeyError("Falta alguna de las columnas requeridas en df_analisis.")

    df_analisis = df_analisis[[col_palabra_clave, col_url, col_volumen, col_posicion, col_dificultad, col_trafico]].copy()
    df_auditoria = df_auditoria.copy()

    col_url_aud = encontrar_columna(df_auditoria, nombres_url)
    if col_url_aud is None:
        raise KeyError("Falta columna URL en auditoría")

    df_combinado = pd.merge(df_analisis, df_auditoria, left_on=col_url, right_on=col_url_aud, how='left')
    df_combinado['Score optimización'] = (
        df_combinado[col_volumen].fillna(0) * 0.25 +
        (100 - df_combinado[col_posicion].fillna(100)) * 0.35 +
        (100 - df_combinado[col_dificultad].fillna(100)) * 0.2 +
        df_combinado[col_trafico].fillna(0) * 0.2
    )

    df_combinado.sort_values(by='Score optimización', ascending=False, inplace=True)
    return df_combinado.head(45)

def generar_nuevas_keywords(df, num_clusters=5):
    if 'PALABRA CLAVE' not in df.columns:
        raise KeyError("Falta la columna 'PALABRA CLAVE'")
    texto = df['PALABRA CLAVE'].fillna('')
    vectorizer = TfidfVectorizer(stop_words='spanish')
    X = vectorizer.fit_transform(texto)

    model = KMeans(n_clusters=num_clusters, random_state=42)
    clusters = model.fit_predict(X)

    df['Cluster'] = clusters
    palabras_por_cluster = {}
    for i in range(num_clusters):
        indices = np.where(clusters == i)[0]
        palabras_cluster = texto.iloc[indices].tolist()
        palabras_por_cluster[f'Cluster_{i}'] = palabras_cluster[:5]
    return df, palabras_por_cluster

def generar_sugerencias(df):
    campos_obligatorios = ['PALABRA CLAVE', 'Cluster', 'CLUSTER', 'SUBCLUSTER', 'Etapa del funnel']
    faltantes = [campo for campo in campos_obligatorios if campo not in df.columns]
    if faltantes:
        raise KeyError(f"Faltan columnas necesarias para generar sugerencias: {faltantes}")

    sugerencias = []
    for _, row in df.iterrows():
        keyword = row['PALABRA CLAVE']
        cluster = row.get('CLUSTER', 'Contenido')
        subcluster = row.get('SUBCLUSTER', '')
        etapa = row.get('Etapa del funnel', 'TOFU')

        titulo = f"Cómo mejorar tu estrategia de {keyword.lower()} para {subcluster.lower()}"
        canal = "Blog, YouTube Shorts y LinkedIn"

        sugerencias.append({
            'Keyword sugerida': keyword,
            'Cluster': cluster,
            'Subcluster': subcluster,
            'Etapa del funnel': etapa,
            'Título propuesto': titulo,
            'Canal sugerido': canal
        })

    return pd.DataFrame(sugerencias)
