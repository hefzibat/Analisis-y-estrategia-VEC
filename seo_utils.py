import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from collections import Counter
import re
import random
import matplotlib.pyplot as plt

# ---------- UTILIDAD GENERAL ----------
def limpiar_keywords(keywords):
    if pd.isna(keywords):
        return []
    if isinstance(keywords, str):
        return [k.strip().lower() for k in re.split(r",|\||;", keywords) if k.strip()]
    return []

# ---------- FASE 1: FILTRAR CONTENIDOS CON POTENCIAL ----------
def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    df_analisis.columns = df_analisis.columns.str.strip().str.upper()
    df_auditoria.columns = df_auditoria.columns.str.strip().str.upper()

    posibles_nombres = {
        "URL": ["URL", "url"],
        "PALABRA CLAVE": ["PALABRA CLAVE", "palabra_clave", "PALABRA_CLAVE"],
        "VOLUMEN": ["VOLUMEN"],
        "TRÁFICO": ["TRÁFICO", "TRAFICO"],
        "LEADS 90 D": ["LEADS 90 D", "LEADS90D", "LEADS"]
    }

    nombre_columnas = {}
    for key, variantes in posibles_nombres.items():
        for var in variantes:
            if var.upper() in df_analisis.columns:
                nombre_columnas[key] = var.upper()
                break
        else:
            raise KeyError(f"Falta la columna requerida en df_analisis: {key}")

    df_analisis = df_analisis.rename(columns={
        nombre_columnas["LEADS 90 D"]: "GENERA LEADS",
        nombre_columnas["PALABRA CLAVE"]: "PALABRA CLAVE",
        nombre_columnas["TRÁFICO"]: "TRÁFICO",
        nombre_columnas["VOLUMEN"]: "VOLUMEN",
        nombre_columnas["URL"]: "URL"
    })

    df = pd.merge(df_analisis, df_auditoria, on="URL", how="left")

    columnas_post_merge = ["PALABRA CLAVE", "VOLUMEN", "TRÁFICO", "DIFICULTAD", "GENERA LEADS"]
    for col in columnas_post_merge:
        if col not in df.columns:
            raise KeyError(f"Falta la columna requerida en el archivo combinado: {col}")

    df = df.dropna(subset=columnas_post_merge, how="any")

    df["VOLUMEN_NORM"] = (df["VOLUMEN"] - df["VOLUMEN"].min()) / (df["VOLUMEN"].max() - df["VOLUMEN"].min())
    df["TRÁFICO_NORM"] = (df["TRÁFICO"] - df["TRÁFICO"].min()) / (df["TRÁFICO"].max() - df["TRÁFICO"].min())
    df["DIFICULTAD_NORM"] = 1 - ((df["DIFICULTAD"] - df["DIFICULTAD"].min()) / (df["DIFICULTAD"].max() - df["DIFICULTAD"].min()))
    df["LEADS_NORM"] = df["GENERA LEADS"].apply(lambda x: 1 if x else 0)

    df["SCORE"] = df[["VOLUMEN_NORM", "TRÁFICO_NORM", "DIFICULTAD_NORM", "LEADS_NORM"]].mean(axis=1)
    df_ordenado = df.sort_values("SCORE", ascending=False)

    top_contenidos = df_ordenado.head(int(len(df_ordenado) * 0.45)).copy()

    return top_contenidos

# ---------- FASE 2: NUEVAS PALABRAS CLAVE ----------
def generar_nuevas_keywords(df):
    if not {"PALABRA CLAVE", "CLUSTER", "SUBCLUSTER"}.issubset(df.columns):
        raise KeyError("Faltan columnas necesarias para generar nuevas keywords")

    texto_keywords = [" ".join(limpiar_keywords(kw)) for kw in df["PALABRA CLAVE"]]
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texto_keywords)

    num_clusters = df["CLUSTER"].nunique()
    df["CLUSTER_NUM"] = pd.factorize(df["CLUSTER"])[0]
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    df["CLUSTER_NUM"] = kmeans.fit_predict(X)

    nuevas_keywords = []
    for i in range(num_clusters):
        subset = df[df["CLUSTER_NUM"] == i]
        palabras = []
        for kw in subset["PALABRA CLAVE"]:
            palabras.extend(limpiar_keywords(kw))
        comunes = [k for k, v in Counter(palabras).most_common(5)]
        cluster_val = subset["CLUSTER"].mode()[0] if not subset["CLUSTER"].mode().empty else f"Cluster {i}"
        subcluster_val = subset["SUBCLUSTER"].mode()[0] if not subset["SUBCLUSTER"].mode().empty else "General"
        funnel_val = subset["ETAPA DEL FUNNEL"].mode()[0] if "ETAPA DEL FUNNEL" in subset.columns and not subset["ETAPA DEL FUNNEL"].mode().empty else "No definido"

        nuevas_keywords.append({
            "cluster": cluster_val,
            "subcluster": subcluster_val,
            "funnel": funnel_val,
            "sugerencias": comunes
        })

    return df, nuevas_keywords

# ---------- FASE 3: TÍTULOS Y CANALES ----------
def generar_sugerencias_contenido(nuevas_keywords, df):
    sugerencias = []

    for item in nuevas_keywords:
        cluster = item["cluster"]
        subcluster = item["subcluster"]
        funnel = item["funnel"]

        if funnel == "TOFU":
            canales = ["Blog", "Chatbot con contenido SEO", "Secuencia automatizada en WhatsApp"]
        elif funnel == "MOFU":
            canales = ["Landing page / Lead magnet", "Email de nutrición", "Flujo en HubSpot con IA"]
        elif funnel == "BOFU":
            canales = ["Email de conversión", "WhatsApp con CTA", "Demo automatizada"]
        else:
            canales = ["Blog", "Email de nutrición", "Newsletter generado por IA"]

        for kw in item["sugerencias"]:
            canal = random.choice(canales)
            titulo = f"Estrategias para {kw} en tu organización"

            sugerencias.append({
                "Keyword": kw,
                "Título sugerido": titulo,
                "Canal": canal,
                "Cluster": cluster,
                "Subcluster": subcluster,
                "Etapa del funnel": funnel
            })

    return pd.DataFrame(sugerencias)

