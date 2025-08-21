import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    # Convertir nombres de columnas a minúsculas
    df_analisis.columns = df_analisis.columns.str.lower()
    df_auditoria.columns = df_auditoria.columns.str.lower()

    # Validar columnas requeridas
    columnas_analisis = ['url', 'palabra_clave', 'posición_promedio', 'volumen_de_búsqueda', 'dificultad', 'tráfico_estimado']
    columnas_auditoria = ['url', 'título', 'tipo de contenido', 'cluster', 'sub-cluster (si aplica)', 'leads 90 d *(esta se usará como \'genera_leads\')']

    for col in columnas_analisis:
        if col not in df_analisis.columns:
            raise ValueError(f"Columna faltante en archivo de análisis: {col}")
    for col in columnas_auditoria:
        if col not in df_auditoria.columns:
            raise ValueError(f"Columna faltante en archivo de auditoría: {col}")

    df = pd.merge(df_analisis, df_auditoria, on='url', how='left')

    # Calcular score combinado
    df['posición_normalizada'] = 1 - (df['posición_promedio'] / df['posición_promedio'].max())
    df['volumen_normalizado'] = df['volumen_de_búsqueda'] / df['volumen_de_búsqueda'].max()
    df['tráfico_normalizado'] = df['tráfico_estimado'] / df['tráfico_estimado'].max()
    df['score_optimizacion'] = (df['posición_normalizada'] + df['volumen_normalizado'] + df['tráfico_normalizado']) / 3

    df_resultado = df.sort_values(by='score_optimizacion', ascending=False).head(40)
    return df_resultado

def generar_keywords_por_cluster(df, num_keywords=5):
    df = df.copy()
    df.columns = df.columns.str.lower()

    if 'palabra_clave' not in df.columns or 'cluster' not in df.columns:
        raise ValueError("Las columnas 'palabra_clave' y 'cluster' deben estar en el DataFrame")

    resultados = []
    for cluster, grupo in df.groupby('cluster'):
        textos = grupo['palabra_clave'].dropna().astype(str)
        if len(textos) == 0:
            continue
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform(textos)
        sum_tfidf = tfidf.sum(axis=0).A1
        palabras = vectorizer.get_feature_names_out()
        top_keywords = [palabras[i] for i in sum_tfidf.argsort()[::-1][:num_keywords]]
        resultados.append({
            'cluster': cluster,
            'sugerencias_keywords': ', '.join(top_keywords)
        })
    return pd.DataFrame(resultados)
