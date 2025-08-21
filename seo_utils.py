import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter

def _normalize_col(col):
    return col.strip().lower().replace(" ", "").replace("_", "").replace("-", "")

def find_column(df, possible_names):
    cols_map = {_normalize_col(c): c for c in df.columns}
    for name in possible_names:
        norm = _normalize_col(name)
        if norm in cols_map:
            return cols_map[norm]
    return None

def filtrar_contenidos_con_potencial(df_ana, df_aud):
    # Encontrar columnas clave
    col_url_ana = find_column(df_ana, ["url"])
    col_url_aud = find_column(df_aud, ["url"])
    col_kw = find_column(df_ana, ["palabra clave", "keyword"])
    col_vol = find_column(df_ana, ["volumen", "search volume"])
    col_pos = find_column(df_ana, ["posición", "position", "posicion promedio"])
    col_dif = find_column(df_ana, ["dificultad", "difficulty"])
    col_tra = find_column(df_ana, ["tráfico", "trafico", "trafico estimado"])
    col_cluster = find_column(df_aud, ["cluster", "categoría", "categoria"])
    col_sub = find_column(df_aud, ["subcluster", "categoríasugerida", "sub categoría"])

    missing = [n for n, c in [("URL análisis", col_url_ana), ("URL auditoría", col_url_aud), ("Palabra clave", col_kw),
                              ("Volumen", col_vol), ("Posición", col_pos), ("Dificultad", col_dif), ("Tráfico", col_tra)]
               if c is None]
    if missing:
        raise KeyError(f"Faltan columnas requeridas en df_analisis: {missing}")

    # Normalizar URL y hacer merge
    df_ana[col_url_ana] = df_ana[col_url_ana].astype(str).str.strip().str.lower()
    df_aud[col_url_aud] = df_aud[col_url_aud].astype(str).str.strip().str.lower()
    df = pd.merge(df_ana, df_aud[[col_url_aud, col_cluster, col_sub]], left_on=col_url_ana, right_on=col_url_aud, how="left")

    # Calcular SCORE
    df["score"] = (
        (1 / (df[col_pos] + 1)) * 0.4 +
        (df[col_vol] / (df[col_vol].max() + 1)) * 0.2 +
        (1 - df[col_dif] / 100) * 0.2 +
        (df[col_tra] / (df[col_tra].max() + 1)) * 0.2
    )
    df_sorted = df.sort_values("score", ascending=False).head(45)

    # Mostrar columnas clave
    to_show = {
        "URL": col_url_ana,
        "Palabra clave": col_kw,
        "Posición": col_pos,
        "Volumen": col_vol,
        "Dificultad": col_dif,
        "Tráfico": col_tra,
    }
    for name, col in list(to_show.items()):
        if col not in df_sorted.columns:
            to_show.pop(name)

    cols_final = list(to_show.values()) + [col_cluster, col_sub, "score"]
    return df_sorted[cols_final].rename(columns={col: name for name, col in to_show.items()})

def generar_nuevas_keywords(df):
    col_kw = find_column(df, ["palabra clave", "keyword"])
    if col_kw is None:
        raise KeyError("No se encontró la columna de palabra clave para clustering.")

    textos = df[col_kw].fillna("").astype(str).tolist()
    X = TfidfVectorizer(stop_words='spanish').fit_transform(textos)
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10).fit(X)
    df["keyword_cluster"] = kmeans.labels_

    keywords_by_cluster = {}
    for cl in df["keyword_cluster"].unique():
        kw_list = df[df["keyword_cluster"] == cl][col_kw].tolist()
        keywords_by_cluster[f"Cluster {cl}"] = kw_list[:5]  # top 5
    return df, keywords_by_cluster

def generar_sugerencias_contenido(df):
    col_kw = find_column(df, ["palabra clave", "keyword"])
    col_cluster = find_column(df, ["cluster"])
    col_sub = find_column(df, ["subcluster"])
    col_etapa = find_column(df, ["etapa del funnel", "etapa"])

    if any(c is None for c in [col_kw, col_cluster]):
        raise KeyError("Faltan columnas clave para generar sugerencias.")

    suggestions = []
    for _, row in df.iterrows():
        kw = row[col_kw]
        cluster = row.get(col_cluster, "")
        subcluster = row.get(col_sub, "")
        etapa = row.get(col_etapa, "TOFU")
        canal = "Blog" if etapa == "TOFU" else "Landing Page"
        titulo = f"Domina {kw} para {subcluster or cluster}"

        suggestions.append({
            "Keyword base": kw,
            "Cluster": cluster,
            "Subcluster": subcluster,
            "Etapa del funnel": etapa,
            "Título sugerido": titulo,
            "Canal sugerido": canal
        })
    return pd.DataFrame(suggestions)
