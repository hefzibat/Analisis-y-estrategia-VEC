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

def generar_ideas_desde_keywords_externas(df_keywords_externas, df_analisis, df_auditoria):
    import numpy as np

    # Validar columnas necesarias
    columnas_keywords = ['Keyword', 'Avg. monthly searches', 'Competition']
    for col in columnas_keywords:
        if col not in df_keywords_externas.columns:
            raise ValueError(f"Falta la columna requerida en el archivo de keywords: {col}")

    # Limpiar y normalizar columnas
    df_keywords_externas.columns = df_keywords_externas.columns.str.strip()
    df_keywords_externas = df_keywords_externas.rename(columns={
        'Keyword': 'palabra_clave_externa',
        'Avg. monthly searches': 'volumen',
        'Competition': 'competencia'
    })

    # Filtrar keywords nuevas que no estén ya en contenidos existentes
    keywords_existentes = df_analisis['palabra_clave'].str.lower().unique()
    df_nuevas = df_keywords_externas[
        ~df_keywords_externas['palabra_clave_externa'].str.lower().isin(keywords_existentes)
    ].copy()

    # Normalizar valores y limpiar nulos
    df_nuevas['volumen'] = pd.to_numeric(df_nuevas['volumen'], errors='coerce').fillna(0)
    df_nuevas['competencia'] = pd.to_numeric(df_nuevas['competencia'], errors='coerce').fillna(0)

    # Estimar canal sugerido
    def sugerir_canal(row):
        if row['competencia'] < 0.4:
            return 'Inbound (contenido evergreen)'
        elif row['competencia'] < 0.7:
            return 'Inbound con IA / Lead magnet'
        else:
            return 'Campaña puntual / Email + IA'

    df_nuevas['Canal sugerido'] = df_nuevas.apply(sugerir_canal, axis=1)

    # Estimar tipo de contenido
    def sugerir_tipo_contenido(row):
        if row['volumen'] >= 1000 and row['competencia'] < 0.5:
            return 'Blog educativo o comparativo'
        elif row['volumen'] >= 500:
            return 'Lead magnet descargable'
        else:
            return 'Checklist, mini guía o herramienta automatizada'

    df_nuevas['Tipo de contenido sugerido'] = df_nuevas.apply(sugerir_tipo_contenido, axis=1)

    # Asignar cluster y subcluster por similitud
    df_auditoria = df_auditoria.rename(columns={
        'URL': 'url',
        'Sub-cluster (si aplica)': 'Subcluster',
        'Leads 90 d': 'genera_leads'
    })

    clusters_keywords = df_analisis[['palabra_clave', 'url']].merge(
        df_auditoria[['url', 'Cluster', 'Subcluster']], on='url', how='left'
    )

    def asignar_cluster(palabra):
        coincidencias = clusters_keywords[
            clusters_keywords['palabra_clave'].str.contains(palabra.split()[0], case=False, na=False)
        ]
        if not coincidencias.empty:
            top = coincidencias.iloc[0]
            return pd.Series([top['Cluster'], top['Subcluster']])
        else:
            return pd.Series(['No identificado', 'No identificado'])

    df_nuevas[['Cluster', 'Subcluster']] = df_nuevas['palabra_clave_externa'].apply(asignar_cluster)

    # Ordenar por volumen para mostrar ideas más atractivas
    df_final = df_nuevas.sort_values(by='volumen', ascending=False)

    # Renombrar para visualización final
    df_final = df_final.rename(columns={
        'palabra_clave_externa': 'Palabra Clave',
        'volumen': 'Volumen',
        'competencia': 'Competencia'
    })

    return df_final[[
        'Palabra Clave', 'Volumen', 'Competencia',
        'Cluster', 'Subcluster',
        'Tipo de contenido sugerido', 'Canal sugerido'
    ]]
