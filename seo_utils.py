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

def generar_ideas_desde_keywords_externas(archivo_keywords, df_resultado_parte1, df_auditoria):
    import pandas as pd

    # Cargar archivo de keywords externas
    if archivo_keywords.name.endswith(".csv"):
        df_keywords = pd.read_csv(archivo_keywords)
    else:
        df_keywords = pd.read_excel(archivo_keywords)

    # Normalizar nombres de columnas
    df_keywords.columns = df_keywords.columns.str.strip().str.lower()
    columnas_validas = ['keyword', 'avg. monthly searches', 'competition']
    if not all(col in df_keywords.columns for col in columnas_validas):
        raise ValueError("El archivo debe contener las columnas: 'Keyword', 'Avg. monthly searches', 'Competition'")

    df_keywords.rename(columns={
        'keyword': 'palabra_clave',
        'avg. monthly searches': 'volumen_de_búsqueda',
        'competition': 'competencia'
    }, inplace=True)

    # Filtrar palabras clave nuevas
    keywords_actuales = df_resultado_parte1["palabra_clave"].str.lower().unique()
    df_keywords_nuevas = df_keywords[~df_keywords['palabra_clave'].str.lower().isin(keywords_actuales)].copy()

    # Normalizar auditoría
    df_auditoria.columns = df_auditoria.columns.str.strip().str.lower()
    auditoria_reducida = df_auditoria[['url', 'cluster', 'sub-cluster (si aplica)']].copy()
    auditoria_reducida.rename(columns={
        'sub-cluster (si aplica)': 'subcluster'
    }, inplace=True)

    # Asignar cluster y subcluster por coincidencia parcial
    def asignar_cluster_subcluster(palabra, auditoria_df):
        for _, fila in auditoria_df.iterrows():
            if pd.notnull(fila['url']) and palabra.lower() in str(fila['url']).lower():
                return fila['cluster'], fila['subcluster']
        return None, None

    df_keywords_nuevas[['cluster', 'subcluster']] = df_keywords_nuevas.apply(
        lambda row: pd.Series(asignar_cluster_subcluster(row['palabra_clave'], auditoria_reducida)), axis=1
    )

    # Crear título sugerido simple
    df_keywords_nuevas['título sugerido'] = df_keywords_nuevas['palabra_clave'].apply(
        lambda x: f"Cómo usar {x} para mejorar tu estrategia"
    )

    # Canal sugerido basado en volumen y competencia
    def canal_sugerido(row):
        vol = row['volumen_de_búsqueda']
        comp = row['competencia']
        if pd.isna(vol) or pd.isna(comp):
            return "Blog"
        if vol > 1000 and comp < 0.4:
            return "Lead magnet descargable"
        elif vol > 1000 and comp >= 0.4:
            return "Bot o herramienta con IA"
        elif vol > 500:
            return "Email educativo o nurturing"
        else:
            return "Blog"

    df_keywords_nuevas['canal sugerido'] = df_keywords_nuevas.apply(canal_sugerido, axis=1)

    # Reordenar columnas finales
    columnas_finales = [
        'palabra_clave', 'volumen_de_búsqueda', 'competencia',
        'cluster', 'subcluster', 'título sugerido', 'canal sugerido'
    ]
    return df_keywords_nuevas[columnas_finales]
