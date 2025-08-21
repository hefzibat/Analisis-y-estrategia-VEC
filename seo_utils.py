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

# ---------- HOMOLOGACIÓN DE COLUMNAS CLAVE ----------
def homologar_columnas(df, posibles_nombres, nuevo_nombre):
    for col in df.columns:
        nombre_limpio = col.strip().lower().replace(" ", "").replace("_", "").replace("-", "").replace("ó", "o").replace("á", "a")
        for posible in posibles_nombres:
            posible_limpio = posible.strip().lower().replace(" ", "").replace("_", "").replace("-", "").replace("ó", "o").replace("á", "a")
            if nombre_limpio == posible_limpio:
                df.rename(columns={col: nuevo_nombre}, inplace=True)
                return
    # Si no se encuentra, deja pasar: lo controlamos más adelante

# ---------- FASE 1 ----------
def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    df_analisis.columns = df_analisis.columns.str.strip()
    df_auditoria.columns = df_auditoria.columns.str.strip()

    # Homologar columnas esperadas
    homologar_columnas(df_analisis, ["palabra clave", "keyword", "palabras clave"], "PALABRA CLAVE")
    homologar_columnas(df_analisis, ["url", "Url", "URL"], "URL")
    homologar_columnas(df_analisis, ["volumen", "volumen de búsqueda", "search volume"], "VOLUMEN")
    homologar_columnas(df_analisis, ["tráfico", "trafico", "tráfico orgánico"], "TRÁFICO")
    homologar_columnas(df_analisis, ["dificultad", "keyword difficulty", "nivel de dificultad"], "DIFICULTAD")
    homologar_columnas(df_analisis, ["leads", "leads 90 d", "conversiones", "genera leads"], "GENERA LEADS")

    requeridas = ["URL", "PALABRA CLAVE", "VOLUMEN", "TRÁFICO", "DIFICULTAD", "GENERA LEADS"]
    for col in requeridas:
        if col not in df_analisis.columns:
            raise KeyError(f"Falta la columna requerida en df_analisis: {col}")

    # Merge para conservar cluster y subcluster
    df = pd.merge(df_analisis, df_auditoria, on="URL", how="left")

    # Normalización
    df = df.dropna(subset=["VOLUMEN", "TRÁFICO", "DIFICULTAD"], how="any")
    df["LEADS_NORM"] = df["GENERA LEADS"].apply(lambda x: 1 if x else 0)
    df["VOLUMEN_NORM"] = (df["VOLUMEN"] - df["VOLUMEN"].min()) / (df["VOLUMEN"].max() - df["VOLUMEN"].min())
    df["TRÁFICO_NORM"] = (df["TRÁFICO"] - df["TRÁFICO"].min()) / (df["TRÁFICO"].max() - df["TRÁFICO"].min())
    df["DIFICULTAD_NORM"] = 1 - ((df["DIFICULTAD"] - df["DIFICULTAD"].min()) / (df["DIFICULTAD"].max() - df["DIFICULTAD"].min()))

    df["SCORE"] = df[["VOLUMEN_NORM", "TRÁFICO_NORM", "DIFICULTAD_NORM", "LEADS_NORM"]].mean(axis=1)
    df_ordenado = df.sort_values("SCORE", ascending=False)

    top_contenidos = df_ordenado.head(int(len(df_ordenado) * 0.45))

    return top_contenidos

# ---------- FASE 2 ----------
def generar_nuevas_keywords(df):
    if "PALABRA CLAVE" not in df.columns:
        raise KeyError("Falta la columna 'PALABRA CLAVE'")

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

# ---------- FASE 3 ----------
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
