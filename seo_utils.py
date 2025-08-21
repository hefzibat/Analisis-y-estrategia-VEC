import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from collections import Counter
import re
import random

# ---------- FUNCIÓN PARA HOMOLOGAR COLUMNAS ----------
def homologar_columnas(df, tipo="analisis"):
    renombres = {
        "url": "URL",
        "palabra clave": "PALABRA CLAVE",
        "palabras clave": "PALABRA CLAVE",
        "keyword": "PALABRA CLAVE",
        "keywords": "PALABRA CLAVE",
        "volumen": "VOLUMEN",
        "volumen de búsqueda": "VOLUMEN",
        "trafico": "TRÁFICO",
        "tráfico": "TRÁFICO",
        "tráfico orgánico": "TRÁFICO",
        "dificultad": "DIFICULTAD",
        "leads 90 d": "GENERA LEADS",
        "leads": "GENERA LEADS",
        "genera leads": "GENERA LEADS"
    }

    columnas = df.columns.str.strip().str.lower()
    columnas_nuevas = []
    for col in columnas:
        col_nueva = renombres.get(col, col.upper())
        columnas_nuevas.append(col_nueva)

    df.columns = columnas_nuevas
    return df

# ---------- FUNCIÓN AUXILIAR ----------
def limpiar_keywords(keywords):
    if pd.isna(keywords):
        return []
    if isinstance(keywords, str):
        return [k.strip().lower() for k in re.split(r",|\||;", keywords) if k.strip()]
    return []

# ---------- FASE 1: FILTRAR CONTENIDOS CON POTENCIAL ----------
def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    df_analisis = homologar_columnas(df_analisis)
    df_auditoria = homologar_columnas(df_auditoria)

    columnas_necesarias = ["URL", "PALABRA CLAVE", "VOLUMEN", "TRÁFICO", "GENERA LEADS"]
    for col in columnas_necesarias:
        if col not in df_analisis.columns:
            raise KeyError(f"Falta la columna requerida en df_analisis: {col}")

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

    top_contenidos = df_ordenado.head(int(len(df_ordenado) * 0.45))

    return top_contenidos

# ---------- FASE 2: NUEVAS PALABRAS CLAVE Y CLUSTER ----------
def generar_nuevas_keywords(df):
    for col in ["PALABRA CLAVE"]:
        if col not in df.columns:
            raise KeyError(f"Falta la columna requerida para clustering: {col}")

    texto_keywords = [" ".join(limpiar_keywords(kw)) for kw in df["PALABRA CLAVE"]]
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texto_keywords)

    num_clusters = min(6, len(df))
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X)
    df["CLUSTER"] = clusters

    nuevas_keywords = []
    for i in range(num_clusters):
        subset = df[df["CLUSTER"] == i]
        palabras = []
        for kw in subset["PALABRA CLAVE"]:
            palabras.extend(limpiar_keywords(kw))
        comunes = [k for k, v in Counter(palabras).most_common(5)]
        nuevas_keywords.append({"cluster": i, "sugerencias": comunes})

    return df, nuevas_keywords

# ---------- FASE 3: GENERACIÓN DE SUGERENCIAS DE CONTENIDO ----------
def generar_sugerencias_contenido(nuevas_keywords, df):
    sugerencias = []

    for item in nuevas_keywords:
        cluster = item["cluster"]
        for kw in item["sugerencias"]:
            cluster_name = df[df["CLUSTER"] == cluster]["CLUSTER NOMBRE"].mode()[0] if "CLUSTER NOMBRE" in df.columns else f"Cluster {cluster}"
            subcluster_name = df[df["CLUSTER"] == cluster]["SUBCLUSTER"].mode()[0] if "SUBCLUSTER" in df.columns else "General"
            funnel = df[df["CLUSTER"] == cluster]["ETAPA DEL FUNNEL"].mode()[0] if "ETAPA DEL FUNNEL" in df.columns else "No definido"

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
