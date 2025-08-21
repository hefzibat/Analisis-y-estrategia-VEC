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

# ---------- NORMALIZACIÓN DE NOMBRES DE COLUMNAS ----------
def estandarizar_columnas(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("á", "a").str.replace("é", "e").str.replace("í", "i").str.replace("ó", "o").str.replace("ú", "u")
    return df

# ---------- FASE 1: FILTRAR CONTENIDOS CON POTENCIAL ----------
def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    df_analisis = estandarizar_columnas(df_analisis)
    df_auditoria = estandarizar_columnas(df_auditoria)

    columnas_necesarias = ["url", "palabra_clave", "volumen", "trafico", "leads_90_d"]
    for col in columnas_necesarias:
        if col not in df_analisis.columns:
            raise KeyError(f"Falta la columna requerida en df_analisis: {col}")

    df_analisis = df_analisis.rename(columns={"leads_90_d": "genera_leads"})

    df = pd.merge(df_analisis, df_auditoria, on="url", how="left")

    columnas_post_merge = ["palabra_clave", "volumen", "trafico", "dificultad", "genera_leads"]
    for col in columnas_post_merge:
        if col not in df.columns:
            raise KeyError(f"Falta la columna requerida en el archivo combinado: {col}")

    df = df.dropna(subset=columnas_post_merge, how="any")

    df["volumen_norm"] = (df["volumen"] - df["volumen"].min()) / (df["volumen"].max() - df["volumen"].min())
    df["trafico_norm"] = (df["trafico"] - df["trafico"].min()) / (df["trafico"].max() - df["trafico"].min())
    df["dificultad_norm"] = 1 - ((df["dificultad"] - df["dificultad"].min()) / (df["dificultad"].max() - df["dificultad"].min()))
    df["leads_norm"] = df["genera_leads"].apply(lambda x: 1 if x else 0)

    df["score"] = df[["volumen_norm", "trafico_norm", "dificultad_norm", "leads_norm"]].mean(axis=1)
    df_ordenado = df.sort_values("score", ascending=False)

    top_contenidos = df_ordenado.head(int(len(df_ordenado) * 0.45))

    return top_contenidos

# ---------- FASE 2: NUEVAS PALABRAS CLAVE ----------
def generar_nuevas_keywords(df):
    for col in ["palabra_clave", "cluster", "subcluster"]:
        if col not in df.columns:
            raise KeyError(f"Falta la columna requerida para clustering: {col}")

    texto_keywords = [" ".join(limpiar_keywords(kw)) for kw in df["palabra_clave"]]
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texto_keywords)

    num_clusters = min(6, len(df))
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X)
    df["cluster"] = clusters

    nuevas_keywords = []
    for i in range(num_clusters):
        subset = df[df["cluster"] == i]
        palabras = []
        for kw in subset["palabra_clave"]:
            palabras.extend(limpiar_keywords(kw))
        comunes = [k for k, v in Counter(palabras).most_common(5)]
        nuevas_keywords.append({"cluster": i, "sugerencias": comunes})

    return df, nuevas_keywords

# ---------- FASE 3: TÍTULOS Y CANALES ----------
def generar_sugerencias_contenido(nuevas_keywords, df):
    sugerencias = []

    for item in nuevas_keywords:
        cluster = item["cluster"]
        for kw in item["sugerencias"]:
            cluster_name = df[df["cluster"] == cluster]["cluster_nombre"].mode()[0] if "cluster_nombre" in df.columns else f"Cluster {cluster}"
            subcluster_name = df[df["cluster"] == cluster]["subcluster"].mode()[0] if "subcluster" in df.columns else "General"
            funnel = df[df["cluster"] == cluster]["etapa_del_funnel"].mode()[0] if "etapa_del_funnel" in df.columns else "No definido"

            if funnel == "TOFU":
                canales = ["Blog", "Chatbot con contenido SEO", "Secuencia automatizada en WhatsApp"]
            elif funnel == "MOFU":
                canales = ["Landing page / Lead magnet", "Email de nutrición", "Flujo en HubSpot con IA"]
            elif funnel == "BOFU":
                canales = ["Email de conversión", "WhatsApp con CTA", "Demo automatizada"]
            else:
                canales = ["Blog", "Email de nutrición", "Newsletter generado por IA"]

            canal = random.choice(canales)
            titulo = f"Estrategias para {kw} en tu organización"

            sugerencias.append({
                "Keyword": kw,
                "Título sugerido": titulo,
                "Canal": canal,
                "Cluster": cluster_name,
                "Subcluster": subcluster_name,
                "Etapa del funnel": funnel
            })

    return pd.DataFrame(sugerencias)
