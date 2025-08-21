import pandas as pd

# --- FUNCIONES ---
def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    # Normalizar nombres de columnas y eliminar espacios
    df_analisis.columns = df_analisis.columns.str.lower().str.strip()
    df_auditoria.columns = df_auditoria.columns.str.lower().str.strip()

    # Renombrar solo lo necesario para hacer merge y análisis
    df_auditoria = df_auditoria.rename(columns={
        "sub-cluster (si aplica)": "subcluster",
        "leads 90 d": "genera_leads"
    })

    # Validar que existan columnas requeridas
    columnas_requeridas_analisis = [
        "url", "palabra_clave", "posición_promedio", "volumen_de_búsqueda",
        "dificultad", "tráfico_estimado", "tipo_de_contenido"
    ]
    columnas_requeridas_auditoria = [
        "url", "cluster", "subcluster", "genera_leads"
    ]

    for col in columnas_requeridas_analisis:
        if col not in df_analisis.columns:
            raise ValueError(f"Falta la columna requerida en df_analisis: {col}")
    for col in columnas_requeridas_auditoria:
        if col not in df_auditoria.columns:
            raise ValueError(f"Falta la columna requerida en df_auditoria: {col}")

    # Unificar URLs
    df_analisis["url"] = df_analisis["url"].str.strip().str.lower()
    df_auditoria["url"] = df_auditoria["url"].str.strip().str.lower()

    # Merge
    df = pd.merge(df_analisis, df_auditoria, on="url", how="inner")

    # Conversión de numéricos
    columnas_numericas = [
        "posición_promedio", "volumen_de_búsqueda", "dificultad", "tráfico_estimado"
    ]
    for col in columnas_numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Rellenar NaNs de leads
    df["genera_leads"] = pd.to_numeric(df["genera_leads"], errors="coerce").fillna(0)

    # Score de priorización
    df["score"] = (
        (1 / (df["posición_promedio"] + 1)) * 0.3 +
        (df["volumen_de_búsqueda"] / df["volumen_de_búsqueda"].max()) * 0.3 +
        (df["tráfico_estimado"] / df["tráfico_estimado"].max()) * 0.2 +
        (1 - df["dificultad"] / 100) * 0.1 +
        (df["genera_leads"] > 0).astype(int) * 0.1
    )

    df_resultado = df.sort_values(by="score", ascending=False).head(45)

    # Renombrar columnas solo para mostrar en la tabla final
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
