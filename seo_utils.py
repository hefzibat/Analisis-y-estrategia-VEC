import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from unidecode import unidecode

def normalizar_columnas(df):
    df.columns = [unidecode(col.lower().strip()) for col in df.columns]
    return df

def validar_columnas(df, columnas_requeridas, nombre_df):
    faltantes = [col for col in columnas_requeridas if col not in df.columns]
    if faltantes:
        raise ValueError(f"Falta la columna requerida en {nombre_df}: {faltantes[0]}")

def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    df_analisis = normalizar_columnas(df_analisis)
    df_auditoria = normalizar_columnas(df_auditoria)

    columnas_requeridas_analisis = ['url', 'palabra clave', 'volumen', 'dificultad', 'trafico']
    columnas_requeridas_auditoria = ['url', 'cluster', 'subcluster', 'etapa del funnel', 'genera leads']

    validar_columnas(df_analisis, columnas_requeridas_analisis, "df_analisis")
    validar_columnas(df_auditoria, columnas_requeridas_auditoria, "df_auditoria")

    df_analisis = df_analisis.copy()
    df_analisis[['volumen', 'dificultad', 'trafico']] = df_analisis[['volumen', 'dificultad', 'trafico']].apply(pd.to_numeric, errors='coerce').fillna(0)

    df_combinado = pd.merge(df_analisis, df_auditoria, on="url", how="left")

    df_combinado["genera leads"] = df_combinado["genera leads"].fillna("NO")
    df_combinado["genera leads_bin"] = df_combinado["genera leads"].apply(lambda x: 1 if str(x).strip().upper() == "SI" else 0)

    df_combinado["score"] = (
        df_combinado["trafico"] * 0.4 +
        df_combinado["volumen"] * 0.3 +
        (100 - df_combinado["dificultad"]) * 0.2 +
        df_combinado["genera leads_bin"] * 0.1
    )

    df_filtrado = df_combinado[df_combinado["score"] > 0].copy()
    df_filtrado.sort_values("score", ascending=False, inplace=True)

    return df_filtrado

def generar_nuevas_keywords(df_filtrado):
    keywords = df_filtrado["palabra clave"].dropna().astype(str).tolist()

    if len(keywords) < 2:
        df_filtrado["cluster"] = "Sin asignar"
        return df_filtrado, []

    vectorizer = TfidfVectorizer(stop_words="spanish")
    X = vectorizer.fit_transform(keywords)

    num_clusters = min(5, len(keywords))
    kmeans = KMeans(n_clusters=num_clusters, random_state=0, n_init=10)
    clusters = kmeans.fit_predict(X)

    df_filtrado["cluster"] = [f"Cluster {i+1}" for i in clusters]

    nuevas_keywords = []
    terms = vectorizer.get_feature_names_out()
    for i in range(num_clusters):
        indices = (clusters == i)
        cluster_texts = X[indices]
        scores = cluster_texts.sum(axis=0).A1
        top_indices = scores.argsort()[-5:][::-1]
        nuevas_keywords.extend([terms[j] for j in top_indices])

    return df_filtrado, list(set(nuevas_keywords))

def generar_sugerencias_contenido(nuevas_keywords, df_filtrado):
    sugerencias = []

    for kw in nuevas_keywords:
        posibles_urls = df_filtrado[df_filtrado["palabra clave"].str.contains(kw, case=False, na=False)]
        if not posibles_urls.empty:
            cluster = posibles_urls["cluster"].iloc[0]
        else:
            cluster = "Sin asignar"
        sugerencias.append({
            "Keyword sugerida": kw,
            "Cluster relacionado": cluster,
            "Título sugerido": f"Estrategias para {kw}",
            "Canal sugerido": "Blog"
        })

    return pd.DataFrame(sugerencias)
