import pandas as pd

def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    # Limpiar nombres de columnas
    df_analisis.columns = df_analisis.columns.str.strip()
    df_auditoria.columns = df_auditoria.columns.str.strip()

    # Validar columnas necesarias
    columnas_analisis = [
        "url", "palabra_clave", "posición_promedio", "volumen_de_búsqueda",
        "dificultad", "tráfico_estimado", "tipo_de_contenido"
    ]
    columnas_auditoria = [
        "URL", "Cluster", "Sub-cluster (si aplica)", "Leads 90 d"
    ]
    for col in columnas_analisis:
        if col not in df_analisis.columns:
            raise ValueError(f"Falta la columna requerida en df_analisis: {col}")
    for col in columnas_auditoria:
        if col not in df_auditoria.columns:
            raise ValueError(f"Falta la columna requerida en df_auditoria: {col}")

    # Homologar URLs
    df_analisis["url"] = df_analisis["url"].str.lower().str.strip()
    df_auditoria["URL"] = df_auditoria["URL"].str.lower().str.strip()

    # Renombrar columnas para merge
    df_auditoria = df_auditoria.rename(columns={
        "URL": "url",
        "Leads 90 d": "genera_leads"
    })

    # Conservar columnas útiles
    columnas_utiles = ["url", "Cluster", "Sub-cluster (si aplica)", "genera_leads"]
    df_auditoria = df_auditoria[columnas_utiles]

    # Hacer merge
    df = pd.merge(df_analisis, df_auditoria, on="url", how="inner")

    # Convertir a numérico
    for col in ["posición_promedio", "volumen_de_búsqueda", "dificultad", "tráfico_estimado"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["genera_leads"] = pd.to_numeric(df["genera_leads"], errors="coerce").fillna(0)

    # Calcular score
    df["score"] = (
        (1 / (df["posición_promedio"] + 1)) * 0.3 +
        (df["volumen_de_búsqueda"] / df["volumen_de_búsqueda"].max()) * 0.3 +
        (df["tráfico_estimado"] / df["tráfico_estimado"].max()) * 0.2 +
        (1 - df["dificultad"] / 100) * 0.1 +
        (df["genera_leads"] > 0).astype(int) * 0.1
    )

    df_resultado = df.sort_values(by="score", ascending=False).head(45)

    # Renombrar columnas solo para visualización
    df_resultado = df_resultado.rename(columns={
        "palabra_clave": "Palabra Clave",
        "volumen_de_búsqueda": "Volumen",
        "tráfico_estimado": "Tráfico",
        "dificultad": "Dificultad",
        "genera_leads": "Genera Leads",
        "score": "Score"
    })

    # Seleccionar columnas a mostrar
    columnas_finales = [
        "url", "Palabra Clave", "Cluster", "Sub-cluster (si aplica)",
        "Volumen", "Tráfico", "Dificultad", "Genera Leads", "Score"
    ]
    return df_resultado[columnas_finales]
    from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from collections import defaultdict

def generar_keywords_por_cluster(df, top_n=10):
    """
    Genera nuevas palabras clave usando TF-IDF, agrupadas por cluster y subcluster.
    También asigna etapa del funnel según el tipo de contenido.

    Parámetros:
    - df: DataFrame combinado con columnas ['palabra_clave', 'cluster', 'subcluster', 'tipo_de_contenido']
    - top_n: número de palabras clave sugeridas por grupo

    Retorna:
    - DataFrame con columnas ['cluster', 'subcluster', 'palabra_clave_sugerida', 'funnel']
    """
    resultado = []

    if df.isnull().any().any():
        df = df.dropna(subset=['palabra_clave', 'cluster', 'subcluster'])

    agrupado = df.groupby(['cluster', 'subcluster'])

    for (cluster, subcluster), grupo in agrupado:
        corpus = grupo['palabra_clave'].dropna().astype(str).tolist()
        if not corpus:
            continue

        vectorizer = TfidfVectorizer(stop_words='spanish')
        X = vectorizer.fit_transform(corpus)
        X_norm = normalize(X, norm='l1', axis=1)
        tfidf_scores = X_norm.sum(axis=0).A1
        vocabulario = vectorizer.get_feature_names_out()
        ranking = sorted(zip(vocabulario, tfidf_scores), key=lambda x: x[1], reverse=True)

        # Determinar funnel según tipo de contenido más frecuente
        funnel = grupo['tipo_de_contenido'].mode().iloc[0] if 'tipo_de_contenido' in grupo else 'desconocido'
        funnel = _mapear_funnel(funnel)

        for palabra, score in ranking[:top_n]:
            resultado.append({
                'cluster': cluster,
                'subcluster': subcluster,
                'palabra_clave_sugerida': palabra,
                'funnel': funnel
            })

    return pd.DataFrame(resultado)

def _mapear_funnel(tipo):
    tipo = tipo.lower()
    if any(x in tipo for x in ['ebook', 'infografía', 'blog']):
        return 'ToFu'
    elif any(x in tipo for x in ['caso', 'webinar', 'checklist']):
        return 'MoFu'
    elif any(x in tipo for x in ['demo', 'servicio', 'cotización']):
        return 'BoFu'
    return 'desconocido'
