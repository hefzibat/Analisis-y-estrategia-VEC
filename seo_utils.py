import pandas as pd
from difflib import get_close_matches

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

def generar_ideas_desde_keywords_externas(df_contenidos_actuales, df_keywords_externas, df_auditoria):
    # Validación de columnas esperadas en el archivo externo
    columnas_esperadas = ["Keyword", "Avg. monthly searches"]
    for col in columnas_esperadas:
        if col not in df_keywords_externas.columns:
            raise ValueError(f"Falta la columna requerida '{col}' en el archivo de keywords externas.")

    # 1. Limpiar y normalizar
    df_keywords_externas = df_keywords_externas.dropna(subset=["Keyword"])
    df_keywords_externas["Keyword"] = df_keywords_externas["Keyword"].str.strip().str.lower()

    # 2. Crear set de palabras clave ya usadas
    usadas = df_contenidos_actuales["palabra_clave"].str.lower().unique()

    # 3. Filtrar las nuevas
    df_nuevas = df_keywords_externas[~df_keywords_externas["Keyword"].isin(usadas)].copy()
    df_nuevas = df_nuevas.rename(columns={
        "Keyword": "palabra_clave",
        "Avg. monthly searches": "volumen_de_busqueda"
    })

    # 4. Preparar dataset de referencia para clusterización
    df_ref = df_auditoria[["Cluster", "Sub-cluster (si aplica)", "URL"]].dropna(subset=["Cluster"])
    df_ref = df_ref.drop_duplicates()
    df_ref["palabras_ref"] = df_ref["URL"].str.extract(r'([^/]+)$').fillna("")

    # 5. Asignar cluster y subcluster por similitud textual con palabras clave
    cluster_resultados = []
    for idx, row in df_nuevas.iterrows():
        keyword = row["palabra_clave"]
        coincidencias = get_close_matches(keyword, df_ref["palabras_ref"], n=1, cutoff=0.4)

        if coincidencias:
            match = coincidencias[0]
            cluster = df_ref[df_ref["palabras_ref"] == match]["Cluster"].values[0]
            subcluster = df_ref[df_ref["palabras_ref"] == match]["Sub-cluster (si aplica)"].values[0]
        else:
            cluster = "Por definir"
            subcluster = "Por definir"

        cluster_resultados.append((cluster, subcluster))

    df_nuevas[["cluster", "subcluster"]] = pd.DataFrame(cluster_resultados, index=df_nuevas.index)

    # 6. Sugerir canal según volumen de búsqueda
    df_nuevas["canal_sugerido"] = df_nuevas["volumen_de_busqueda"].apply(
        lambda x: "Inbound" if x >= 100 else "Contenido asistido por IA"
    )

    # 7. Reordenar columnas
    columnas_finales = [
        "palabra_clave", "cluster", "subcluster", "volumen_de_busqueda", "canal_sugerido"
    ]
    return df_nuevas[columnas_finales]
