import pandas as pd
import numpy as np
import re

def limpiar_keywords(keywords):
    if pd.isna(keywords):
        return []
    if isinstance(keywords, str):
        return [k.strip().lower() for k in re.split(r",|\||;", keywords) if k.strip()]
    return []

def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    # Homogeneiza nombres
    df_analisis.columns = df_analisis.columns.str.upper().str.strip()
    df_auditoria.columns = df_auditoria.columns.str.upper().str.strip()

    # Validación de columnas necesarias
    columnas_requeridas = ["URL", "PALABRA CLAVE", "VOLUMEN", "TRÁFICO", "DIFICULTAD"]
    for col in columnas_requeridas:
        if col not in df_analisis.columns:
            raise KeyError(f"Falta la columna requerida en df_analisis: {col}")

    # Renombrar columna de leads si existe
    if "LEADS 90 D" in df_analisis.columns:
        df_analisis = df_analisis.rename(columns={"LEADS 90 D": "GENERA LEADS"})
    elif "LEADS" in df_analisis.columns:
        df_analisis = df_analisis.rename(columns={"LEADS": "GENERA LEADS"})
    else:
        df_analisis["GENERA LEADS"] = False  # columna dummy si no existe

    # Unir con auditoría
    df = pd.merge(df_analisis, df_auditoria, on="URL", how="left")

    columnas_post_merge = ["PALABRA CLAVE", "VOLUMEN", "TRÁFICO", "DIFICULTAD", "GENERA LEADS"]
    df = df.dropna(subset=columnas_post_merge, how="any")

    # Normalización de métricas
    df["VOLUMEN_NORM"] = (df["VOLUMEN"] - df["VOLUMEN"].min()) / (df["VOLUMEN"].max() - df["VOLUMEN"].min())
    df["TRÁFICO_NORM"] = (df["TRÁFICO"] - df["TRÁFICO"].min()) / (df["TRÁFICO"].max() - df["TRÁFICO"].min())
    df["DIFICULTAD_NORM"] = 1 - ((df["DIFICULTAD"] - df["DIFICULTAD"].min()) / (df["DIFICULTAD"].max() - df["DIFICULTAD"].min()))
    df["LEADS_NORM"] = df["GENERA LEADS"].apply(lambda x: 1 if x else 0)

    df["SCORE"] = df[["VOLUMEN_NORM", "TRÁFICO_NORM", "DIFICULTAD_NORM", "LEADS_NORM"]].mean(axis=1)
    df_ordenado = df.sort_values("SCORE", ascending=False)

    top_contenidos = df_ordenado.head(int(len(df_ordenado) * 0.45))

    return top_contenidos
