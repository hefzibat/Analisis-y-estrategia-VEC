# seo_utils.py

import pandas as pd

def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    # Limpiar nombres de columnas
    df_analisis.columns = df_analisis.columns.str.strip()
    df_auditoria.columns = df_auditoria.columns.str.strip()

    print("\n📌 Columnas exactas en df_auditoria:")
    for idx, col in enumerate(df_auditoria.columns):
        print(f"{idx}: '{col}' → length: {len(col)}")

    # Validar columnas necesarias
    columnas_analisis = [
        "url", "palabra_clave", "posición_promedio", "volumen_de_búsqueda",
        "dificultad", "tráfico_estimado", "tipo_de_contenido"
    ]
    for col in columnas_analisis:
        if col not in df_analisis.columns:
            raise ValueError(f"Falta la columna requerida en df_analisis: {col}")

    columnas_auditoria = [
        "URL", "Cluster", "Sub-cluster (si aplica)", "Leads 90 d"
    ]
    for col in columnas_auditoria:
        if col not in df_auditoria.columns:
            raise ValueError(f"Falta la columna requerida en df_auditoria: {col}")

    # Homologar y renombrar
    df_analisis["url"] = df_analisis["url"].str.lower().str.strip()
    df_auditoria["URL"] = df_auditoria["URL"].str.lower().str.strip()

    df_auditoria_renombrado = df_auditoria.rename(columns={
        "URL": "url",
        "Leads 90 d": "genera_leads"
    })

    columnas_utiles = ["url", "Cluster", "Sub-cluster (si aplica)", "genera_leads"]
    df_auditoria_renombrado = df_auditoria_renombrado[columnas_utiles]

    # Merge
    df = pd.merge(df_analisis, df_auditoria_renombrado, on="url", how="inner")

    columnas_numericas = ["posición_promedio", "volumen_de_búsqueda", "dificultad", "tráfico_estimado"]
    for col in columnas_numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["genera_leads"] = pd.to_numeric(df["genera_leads"], errors="coerce").fillna(0)

    df["score"] = (
        (1 / (df["posición_promedio"] + 1)) * 0.3 +
        (df["volumen_de_búsqueda"] / df["volumen_de_búsqueda"].max()) * 0.3 +
        (df["tráfico_estimado"] / df["tráfico_estimado"].max()) * 0.2 +
        (1 - df["dificultad"] / 100) * 0.1 +
        (df["genera_leads"] > 0).astype(int) * 0.1
    )

    df_resultado = df.sort_values(by="score", ascending=False).head(45)

    df_resultado = df_resultado.rename(columns={
        "palabra_clave": "Palabra Clave",
        "volumen_de_búsqueda": "Volumen",
        "tráfico_estimado": "Tráfico",
        "dificultad": "Dificultad",
        "genera_leads": "Genera Leads",
        "score": "Score"
    })

    columnas_finales = [
        "url", "Palabra Clave", "Cluster", "Sub-cluster (si aplica)",
        "Volumen", "Tráfico", "Dificultad", "Genera Leads", "Score"
    ]
    columnas_disponibles = [col for col in columnas_finales if col in df_resultado.columns]

    return df_resultado[columnas_disponibles]
