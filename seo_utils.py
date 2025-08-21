import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def estandarizar_columnas(df):
    df.columns = df.columns.str.strip().str.upper().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    return df

def renombrar_columnas(df):
    mapping = {
        'LEADS 90 D': 'GENERA LEADS',
        'KEYWORD': 'PALABRA CLAVE',
        'KW': 'PALABRA CLAVE',
        'URL FINAL': 'URL',
        'VOLUME': 'VOLUMEN',
        'TRAFFIC': 'TRAFICO'
    }
    df = df.rename(columns={k: v for k, v in mapping.items() if k in df.columns})
    return df

def validar_columnas(df, requeridas):
    faltantes = [col for col in requeridas if col not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {', '.join(faltantes)}")

def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    df_analisis = estandarizar_columnas(df_analisis)
    df_analisis = renombrar_columnas(df_analisis)
    df_auditoria = estandarizar_columnas(df_auditoria)
    df_auditoria = renombrar_columnas(df_auditoria)

    columnas_necesarias = ['URL', 'PALABRA CLAVE', 'VOLUMEN', 'DIFICULTAD', 'TRAFICO']
    validar_columnas(df_analisis, columnas_necesarias)

    if 'GENERA LEADS' not in df_analisis.columns and 'LEADS 90 D' in df_analisis.columns:
        df_analisis['GENERA LEADS'] = df_analisis['LEADS 90 D']

    df_analisis = df_analisis.copy()
    df_analisis['VOLUMEN'] = pd.to_numeric(df_analisis['VOLUMEN'], errors='coerce')
    df_analisis['TRAFICO'] = pd.to_numeric(df_analisis['TRAFICO'], errors='coerce')
    df_analisis['DIFICULTAD'] = pd.to_numeric(df_analisis['DIFICULTAD'], errors='coerce')
    df_analisis['GENERA LEADS'] = pd.to_numeric(df_analisis['GENERA LEADS'], errors='coerce')

    df_analisis['SCORE'] = (
        df_analisis['VOLUMEN'].fillna(0) * 0.3 +
        df_analisis['TRAFICO'].fillna(0) * 0.3 +
        df_analisis['GENERA LEADS'].fillna(0) * 0.4
    ) / (df_analisis['DIFICULTAD'].replace(0, 1))

    df_filtrado = df_analisis.sort_values(by='SCORE', ascending=False).head(45)

    if 'CLUSTER' not in df_filtrado.columns and 'CLUSTER NOMBRE' in df_auditoria.columns:
        df_auditoria = df_auditoria[['URL', 'CLUSTER NOMBRE', 'SUBCLUSTER', 'ETAPA DEL FUNNEL']]
        df_auditoria = df_auditoria.rename(columns={
            'CLUSTER NOMBRE': 'CLUSTER'
        })
        df_filtrado = df_filtrado.merge(df_auditoria, on='URL', how='left')

    return df_filtrado

def limpiar_keywords(texto):
    if pd.isnull(texto):
        return ""
    return str(texto).lower().strip()

def generar_nuevas_keywords(df):
    df = df.copy()
    df['PALABRA CLAVE LIMPIA'] = df['PALABRA CLAVE'].apply(limpiar_keywords)
    vectorizer = TfidfVectorizer(stop_words='spanish')
    X = vectorizer.fit_transform(df['PALABRA CLAVE LIMPIA'])

    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    df['CLUSTER_NUEVO'] = kmeans.fit_predict(X)

    nuevas_keywords = (
        df.groupby('CLUSTER_NUEVO')['PALABRA CLAVE LIMPIA']
        .apply(lambda x: ', '.join(x.unique()[:3]))
        .reset_index(name='NUEVAS KEYWORDS')
    )

    return df, nuevas_keywords

def generar_sugerencias_contenido(nuevas_keywords, df):
    sugerencias = nuevas_keywords.copy()
    sugerencias['TITULO PROPUESTO'] = sugerencias['NUEVAS KEYWORDS'].apply(
        lambda x: f"Guía esencial sobre {x.split(',')[0]}"
    )
    sugerencias['CANAL SUGERIDO'] = 'Blog'
    if 'ETAPA DEL FUNNEL' in df.columns:
        etapas = df[['CLUSTER_NUEVO', 'ETAPA DEL FUNNEL']].dropna().drop_duplicates()
        sugerencias = sugerencias.merge(etapas, on='CLUSTER_NUEVO', how='left')
    return sugerencias
