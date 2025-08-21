import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def normalizar_columnas(df):
    df.columns = df.columns.str.strip().str.upper().str.replace(" ", "_").str.replace("-", "_")
    return df

def encontrar_columna(df, posibles_nombres):
    for nombre in posibles_nombres:
        for col in df.columns:
            if nombre.upper() == col.upper().replace(" ", "_").replace("-", "_"):
                return col
    return None

def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    df_analisis = normalizar_columnas(df_analisis)
    df_auditoria = normalizar_columnas(df_auditoria)

    col_url = encontrar_columna(df_analisis, ["URL"])
    col_kw = encontrar_columna(df_analisis, ["PALABRA_CLAVE", "KEYWORD"])
    col_pos = encontrar_columna(df_analisis, ["POSICION"])
    col_vol = encontrar_columna(df_analisis, ["VOLUMEN"])
    col_dif = encontrar_columna(df_analisis, ["DIFICULTAD"])
    col_tra = encontrar_columna(df_analisis, ["TRAFICO"])

    if None in [col_url, col_kw, col_pos, col_vol, col_dif, col_tra]:
        raise ValueError("Falta alguna de las columnas requeridas en df_analisis.")

    col_leads = encontrar_columna(df_auditoria, ["LEADS"])
    col_funnel = encontrar_columna(df_auditoria, ["ETAPA_DEL_FUNNEL"])
    col_cluster = encontrar_columna(df_auditoria, ["CLUSTER"])
    col_subcluster = encontrar_columna(df_auditoria, ["SUBCLUSTER"])

    if None in [col_leads, col_funnel, col_cluster, col_subcluster]:
        raise ValueError("Faltan columnas requeridas en df_auditoria.")

    df_analisis = df_analisis.rename(columns={
        col_url: "URL",
        col_kw: "PALABRA_CLAVE",
        col_pos: "POSICION",
        col_vol: "VOLUMEN",
        col_dif: "DIFICULTAD",
        col_tra: "TRAFICO"
    })

    df_auditoria = df_auditoria.rename(columns={
        col_url: "URL",
        col_leads: "LEADS",
        col_funnel: "ETAPA_DEL_FUNNEL",
        col_cluster: "CLUSTER",
        col_subcluster: "SUBCLUSTER"
    })

    df = pd.merge(df_analisis, df_auditoria, on="URL", how="inner")

    df["PUNTAJE"] = (
        df["VOLUMEN"].fillna(0) * 0.3 +
        df["TRAFICO"].fillna(0) * 0.3 +
        (100 - df["POSICION"].fillna(100)) * 0.2 +
        (100 - df["DIFICULTAD"].fillna(100)) * 0.2
    )

    df_filtrados = df[df["PUNTAJE"] > df["PUNTAJE"].median()].copy()
    df_filtrados = df_filtrados.sort_values(by="PUNTAJE", ascending=False)

    return df_filtrados

def generar_nuevas_keywords(df):
    agrupado = df.groupby("CLUSTER")["PALABRA_CLAVE"].apply(lambda x: " ".join(x.dropna().astype(str))).reset_index()
    agrupado["KEYWORDS_SUGERIDAS"] = agrupado["PALABRA_CLAVE"].apply(lambda texto: _cluster_keywords(texto))
    return agrupado[["CLUSTER", "KEYWORDS_SUGERIDAS"]]

def _cluster_keywords(texto, n_clusters=5):
    vectorizer = TfidfVectorizer(stop_words='spanish')
    X = vectorizer.fit_transform([texto])
    if X.shape[1] < n_clusters:
        return ", ".join(vectorizer.get_feature_names_out())
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    km.fit(X.T)
    orden = km.cluster_centers_.sum(axis=1).argsort()[::-1]
    palabras = vectorizer.get_feature_names_out()
    clusters = {i: [] for i in range(n_clusters)}
    for i, label in enumerate(km.labels_):
        clusters[label].append(palabras[i])
    return ", ".join([" / ".join(clusters[i][:3]) for i in orden])

def generar_sugerencias_contenido(df):
    df["TITULO_PROPUESTO"] = df["KEYWORDS_SUGERIDAS"].apply(lambda k: f"Estrategias para {k.split(',')[0]}")
    df["CANAL_SUGERIDO"] = df["KEYWORDS_SUGERIDAS"].apply(lambda k: "Blog" if len(k) < 60 else "Video")
    return df[["CLUSTER", "KEYWORDS_SUGERIDAS", "TITULO_PROPUESTO", "CANAL_SUGERIDO"]]
