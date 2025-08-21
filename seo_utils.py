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

def generar_ideas_desde_keywords_externas(archivo_keywords_externas, contenidos_actuales):
    try:
        # Leer archivo externo
        df_keywords = pd.read_csv(archivo_keywords_externas)
        df_keywords.columns = [col.strip().lower() for col in df_keywords.columns]

        # Validación de columna 'keyword'
        if 'keyword' not in df_keywords.columns:
            return pd.DataFrame({'Error': ['La columna "Keyword" no se encontró en el archivo.']})

        # Limpiar keywords externas
        df_keywords['keyword'] = df_keywords['keyword'].str.strip().str.lower()

        # Obtener títulos y URLs ya usados en la Parte 1
        usados = set()
        if not contenidos_actuales.empty:
            if 'palabra_clave' in contenidos_actuales.columns:
                usados = set(contenidos_actuales['palabra_clave'].str.strip().str.lower().dropna().tolist())
            elif 'título' in contenidos_actuales.columns:
                usados = set(contenidos_actuales['título'].str.strip().str.lower().dropna().tolist())

        # Filtrar palabras clave no utilizadas
        df_nuevas = df_keywords[~df_keywords['keyword'].isin(usados)].copy()

        # Sugerir canal según criterio simple
        def sugerir_canal(palabra):
            if any(ia in palabra for ia in ['ai', 'inteligencia artificial', 'automatización']):
                return 'Inbound + IA'
            return 'Inbound (SEO / Blog / Webinar)'

        df_nuevas['canal_sugerido'] = df_nuevas['keyword'].apply(sugerir_canal)

        # Columnas cluster y subcluster (se dejarán vacías por ahora si no se pueden inferir)
        df_nuevas['cluster'] = ''
        df_nuevas['subcluster'] = ''

        # Reordenar columnas
        df_final = df_nuevas[['keyword', 'cluster', 'subcluster', 'canal_sugerido']]
        df_final.columns = ['Palabra clave', 'Cluster', 'Subcluster', 'Canal sugerido']

        return df_final

    except Exception as e:
        return pd.DataFrame({'Error': [str(e)]})
