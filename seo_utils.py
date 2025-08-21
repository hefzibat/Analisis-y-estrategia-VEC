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
    
def generar_ideas_con_keywords_externas(df_analisis, df_auditoria, df_keywords_externas):
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    # Renombrar columna si viene como 'Keyword'
    if 'Keyword' in df_keywords_externas.columns:
        df_keywords_externas = df_keywords_externas.rename(columns={"Keyword": "palabra_clave"})

    # Validar columnas necesarias
    columnas_analisis = ['palabra_clave']
    columnas_auditoria = ['Cluster', 'Sub-cluster (si aplica)']
    columnas_externas = ['palabra_clave']

    for col in columnas_analisis:
        if col not in df_analisis.columns:
            raise ValueError(f"Falta columna en archivo de análisis: {col}")
    for col in columnas_auditoria:
        if col not in df_auditoria.columns:
            raise ValueError(f"Falta columna en auditoría: {col}")
    for col in columnas_externas:
        if col not in df_keywords_externas.columns:
            raise ValueError(f"Falta columna en keywords externas: {col}")

    # Preprocesar
    df_analisis['palabra_clave'] = df_analisis['palabra_clave'].str.lower().str.strip()
    df_keywords_externas['palabra_clave'] = df_keywords_externas['palabra_clave'].str.lower().str.strip()

    # Filtrar keywords externas nuevas
    keywords_actuales = df_analisis['palabra_clave'].unique()
    df_nuevas = df_keywords_externas[~df_keywords_externas['palabra_clave'].isin(keywords_actuales)].copy()

    if df_nuevas.empty:
        return pd.DataFrame(columns=["Palabra Clave", "Título posible", "Cluster", "Subcluster", "Canal sugerido"])

    # Similaridad para clusters y subclusters
    df_nuevas['match_cluster'] = ''
    df_nuevas['match_subcluster'] = ''

    clusters = df_auditoria['Cluster'].dropna().unique()
    subclusters = df_auditoria['Sub-cluster (si aplica)'].dropna().unique()

    vectorizer = TfidfVectorizer().fit(list(df_nuevas['palabra_clave']) + list(clusters) + list(subclusters))
    keyword_vecs = vectorizer.transform(df_nuevas['palabra_clave'])

    if len(clusters) > 0:
        cluster_vecs = vectorizer.transform(clusters)
        sim_cluster = cosine_similarity(keyword_vecs, cluster_vecs)
        best_cluster = sim_cluster.argmax(axis=1)
        df_nuevas['match_cluster'] = [clusters[i] for i in best_cluster]

    if len(subclusters) > 0:
        subcluster_vecs = vectorizer.transform(subclusters)
        sim_subcluster = cosine_similarity(keyword_vecs, subcluster_vecs)
        best_subcluster = sim_subcluster.argmax(axis=1)
        df_nuevas['match_subcluster'] = [subclusters[i] for i in best_subcluster]
    else:
        df_nuevas['match_subcluster'] = ''

    def canal_sugerido(palabra):
        palabra = palabra.lower()
        if any(x in palabra for x in ["automatiza", "herramienta", "plantilla", "generador"]):
            return "herramienta de ia"
        elif any(x in palabra for x in ["flujo", "proceso", "etapas", "pasos"]):
            return "flujo"
        elif any(x in palabra for x in ["email", "newsletter", "correos"]):
            return "email"
        elif any(x in palabra for x in ["ebook", "guía", "checklist", "descargable"]):
            return "lead magnet"
        else:
            return "blog"

    df_nuevas['canal'] = df_nuevas['palabra_clave'].apply(canal_sugerido)
    df_nuevas['titulo'] = df_nuevas['palabra_clave'].apply(lambda x: f"Cómo aprovechar {x} en tu estrategia")

    df_resultado = df_nuevas.rename(columns={
        'palabra_clave': 'Palabra Clave',
        'match_cluster': 'Cluster',
        'match_subcluster': 'Subcluster',
        'canal': 'Canal sugerido',
        'titulo': 'Título posible'
    })[
        ['Palabra Clave', 'Título posible', 'Cluster', 'Subcluster', 'Canal sugerido']
    ]

    return df_resultado
    
    def recomendar_mix_contenido(df_sugerencias):
    import pandas as pd

    if df_sugerencias.empty:
        return pd.DataFrame(columns=["Tipo de contenido", "Cantidad sugerida", "Objetivo asociado"])

    total_sugerencias = len(df_sugerencias)

    # Definir porcentajes sugeridos por tipo de canal
    mix_porcentaje = {
        "blog": 0.5,
        "lead magnet": 0.2,
        "email": 0.15,
        "herramienta de ia": 0.1,
        "flujo": 0.05
    }

    # Objetivos asociados
    objetivos = {
        "blog": "Aumentar visitantes",
        "lead magnet": "Incrementar leads",
        "email": "Convertir leads a MQL",
        "herramienta de ia": "Captación con valor",
        "flujo": "Nutrición y automatización"
    }

    resultado = []
    for tipo, porcentaje in mix_porcentaje.items():
        cantidad = round(total_sugerencias * porcentaje)
        resultado.append({
            "Tipo de contenido": tipo,
            "Cantidad sugerida": cantidad,
            "Objetivo asociado": objetivos[tipo]
        })

    return pd.DataFrame(resultado)
