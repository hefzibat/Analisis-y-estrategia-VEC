import pandas as pd

# --- FUNCIONES ---
def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    # Normalizar columnas en ambos DataFrames
    df_analisis.columns = df_analisis.columns.str.lower().str.strip()
    df_auditoria.columns = df_auditoria.columns.str.lower().str.strip()

    # Renombrar columnas clave en auditoría para que coincidan con análisis
    df_auditoria = df_auditoria.rename(columns={
        "url": "url",
        "leads 90 d": "genera_leads",
        "sub-cluster (si aplica)": "subcluster"
    })

    # Validación de columnas mínimas requeridas
    columnas_requeridas_analisis = [
        "url", "palabra_clave", "posición_promedio", "volumen_de_búsqueda",
        "dificultad", "tráfico_estimado", "tipo_de_contenido"
    ]
    columnas_requeridas_auditoria = ["url", "cluster", "subcluster", "genera_leads"]

    for col in columnas_requeridas_analisis:
        if col not in df_analisis.columns:
            raise ValueError(f"Falta la columna requerida en df_analisis: {col}")

    for col in columnas_requeridas_auditoria:
        if col not in df_auditoria.columns:
            raise ValueError(f"Falta la columna requerida en df_auditoria: {col}")

    # Convertir todas las URL a minúsculas para asegurar coincidencia
    df_analisis["url"] = df_analisis["url"].str.lower().str.strip()
    df_auditoria["url"] = df_auditoria["url"].str.lower().str.strip()

    # Unir ambos dataframes por URL
    df = pd.merge(df_analisis, df_auditoria, on="url", how="inner")

    # Validación y limpieza de columnas numéricas necesarias
    columnas_numericas = ["posición_promedio", "volumen_de_búsqueda", "dificultad", "tráfico_estimado"]
    for col in columnas_numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Rellenar NaNs
    df["genera_leads"] = df["genera_leads"].fillna(0)

    # Normalizar y calcular SCORE de priorización (ajustable)
    df["score"] = (
        (1 / (df["posición_promedio"] + 1)) * 0.3 +
        (df["volumen_de_búsqueda"] / df["volumen_de_búsqueda"].max()) * 0.3 +
        (df["tráfico_estimado"] / df["tráfico_estimado"].max()) * 0.2 +
        (1 - df["dificultad"] / 100) * 0.1 +
        (df["genera_leads"] > 0).astype(int) * 0.1
    )

    # Ordenar por score y filtrar los top 45 (o menos si no hay suficientes)
    df_resultado = df.sort_values(by="score", ascending=False).head(45)

    # Renombrar columnas para visualización limpia
    df_resultado = df_resultado.rename(columns={
        "palabra_clave": "Palabra Clave",
        "volumen_de_búsqueda": "Volumen",
        "tráfico_estimado": "Tráfico",
        "dificultad": "Dificultad",
        "genera_leads": "Genera Leads",
        "cluster": "Cluster",
        "subcluster": "Subcluster",
        "score": "Score"
    })

    return df_resultado[[
        "url", "Palabra Clave", "Cluster", "Subcluster",
        "Volumen", "Tráfico", "Dificultad", "Genera Leads", "Score"
    ]]
