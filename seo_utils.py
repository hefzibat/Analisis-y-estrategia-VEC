import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


def normalizar_columna(df, nombres_posibles):
    for nombre in nombres_posibles:
        if nombre in df.columns:
            return df[nombre]
    raise KeyError(f"Ninguna de las siguientes columnas fue encontrada: {nombres_posibles}")


def estandarizar_columnas(df):
    df.columns = [col.lower().strip().replace(" ", "_").replace("-", "_") for col in df.columns]
    return df


def combinar_datasets(df_analisis, df_auditoria):
    df_analisis = estandarizar_columnas(df_analisis)
    df_auditoria = estandarizar_columnas(df_auditoria)

    df_analisis = df_analisis.rename(columns={
        "url": "url",
        "palabra_clave": "palabra_clave",
        "posición_promedio": "posicion",
        "volumen_de_búsqueda": "volumen",
        "tráfico_estimado": "trafico",
        "dificultad": "dificultad",
        "tipo_de_contenido": "tipo_contenido"
    })

    df_auditoria = df_auditoria.rename(columns={
        "url": "url",
        "categoría": "cluster",
        "categoría_sugerida": "subcluster"
    })

    df_combinado = pd.merge(df_analisis, df_auditoria, on="url", how="left")
    return df_combinado


def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    df = combinar_datasets(df_analisis, df_auditoria)
    df = df.dropna(subset=["posicion", "volumen", "trafico", "dificultad"], how="any")
    df = df[(df["posicion"] > 10) & (df["posicion"] < 30)]
    df["score"] = (df["volumen"] * 0.4 + df["trafico"] * 0.3 + (100 - df["dificultad"]) * 0.3)
    df = df.sort_values(by="score", ascending=False).head(45)
    return df


def generar_nuevas_keywords(df_combinado):
    df = df_combinado.dropna(subset=["palabra_clave"])
    vectorizer = TfidfVectorizer(stop_words='spanish')
    X = vectorizer.fit_transform(df["palabra_clave"])

    kmeans = KMeans(n_clusters=5, random_state=42, n_init='auto')
    df["keyword_cluster"] = kmeans.fit_predict(X)

    nuevas_keywords = []
    for cluster_id in df["keyword_cluster"].unique():
        top_keywords = df[df["keyword_cluster"] == cluster_id]["palabra_clave"].head(3).tolist()
        nuevas_keywords.extend(top_keywords)
    return nuevas_keywords


def generar_sugerencias_contenido(df):
    sugerencias = []
    for _, row in df.iterrows():
        cluster = row.get("cluster", "General")
        subcluster = row.get("subcluster", "")
        palabra = row["palabra_clave"]

        canal = "Blog" if row["posicion"] > 15 else "Guía" if row["volumen"] > 1000 else "Newsletter"
        titulo = f"Estrategias para posicionar '{palabra}' en {cluster}/{subcluster}"

        sugerencias.append({
            "palabra_clave": palabra,
            "titulo": titulo,
            "canal": canal,
            "cluster": cluster,
            "subcluster": subcluster
        })
    return pd.DataFrame(sugerencias)
