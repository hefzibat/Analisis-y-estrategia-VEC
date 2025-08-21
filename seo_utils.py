import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def normalizar_nombre_columna(col):
    col = col.strip().lower()
    col = col.replace(" ", "").replace("_", "").replace("-", "")
    return col

def encontrar_columna(df, nombres_posibles):
    cols_norm = {normalizar_nombre_columna(c): c for c in df.columns}
    for nombre in nombres_posibles:
        norm = normalizar_nombre_columna(nombre)
        if norm in cols_norm:
            return cols_norm[norm]
    return None

def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    nombres_posibles_url = ["url"]
    nombres_posibles_cluster = ["cluster"]
    nombres_posibles_subcluster = ["subcluster"]

    col_url_analisis = encontrar_columna(df_analisis, nombres_posibles_url)
    col_url_auditoria = encontrar_columna(df_auditoria, nombres_posibles_url)

    if col_url_analisis is None or col_url_auditoria is None:
        raise KeyError("Falta la columna URL en uno de los archivos.")

    df_analisis[col_url_analisis] = df_analisis[col_url_analisis].str.strip().str.lower()
    df_auditoria[col_url_auditoria] = df_auditoria[col_url_auditoria].str.strip().str.lower()

    df_analisis = df_analisis.drop_duplicates(subset=col_url_analisis)

    df_merge = pd.merge(df_analisis, df_auditoria, left_on=col_url_analisis, right_on=col_url_auditoria, suffixes=('_ana', '_aud'))

    posibles_palabra_clave = ["palabra clave", "keyword"]
    posibles_posicion = ["posición", "posición promedio", "position"]
    posibles_volumen = ["volumen", "volumen de búsqueda", "search volume"]
    posibles_dificultad = ["dificultad", "keyword difficulty"]
    posibles_trafico = ["tráfico", "trafico"]
    posibles_etapa = ["etapa", "etapa del funnel"]

    col_keyword = encontrar_columna(df_merge, posibles_palabra_clave)
    col_posicion = encontrar_columna(df_merge, posibles_posicion)
    col_volumen = encontrar_columna(df_merge, posibles_volumen)
    col_dificultad = encontrar_columna(df_merge, posibles_dificultad)
    col_trafico = encontrar_columna(df_merge, posibles_trafico)
    col_etapa = encontrar_columna(df_merge, posibles_etapa)
    col_cluster = encontrar_columna(df_merge, nombres_posibles_cluster)
    col_subcluster = encontrar_columna(df_merge, nombres_posibles_subcluster)

    columnas_requeridas = [col_keyword, col_posicion, col_volumen, col_dificultad, col_trafico, col_url_analisis]
    if any(col is None for col in columnas_requeridas):
        raise KeyError("Falta alguna de las columnas requeridas en df_analisis.")

    df_merge["score"] = (
        (1 / (df_merge[col_posicion] + 1)) * 0.4 +
        (df_merge[col_volumen] / (df_merge[col_volumen].max() + 1)) * 0.2 +
        (1 - df_merge[col_dificultad] / 100) * 0.2 +
        (df_merge[col_trafico] / (df_merge[col_trafico].max() + 1)) * 0.2
    )

    df_top = df_merge.sort_values("score", ascending=False).head(45)

    columnas_a_mostrar = [col_url_analisis, col_keyword, col_posicion, col_volumen, col_dificultad, col_trafico, col_etapa, col_cluster, col_subcluster, "score"]
    df_resultado = df_top[[col for col in columnas_a_mostrar if col in df_top.columns]].copy()
    df_resultado = df_resultado.rename(columns={col_url_analisis: "URL"})

    return df_resultado

def generar_nuevas_keywords(df):
    col_keyword = encontrar_columna(df, ["palabra clave", "keyword"])
    if col_keyword is None:
        raise KeyError("No se encontró la columna de palabra clave para clusterizar.")

    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(df[col_keyword].astype(str))

    kmeans = KMeans(n_clusters=5, random_state=0, n_init=10)
    df['Cluster_KW'] = kmeans.fit_predict(X)

    return df

def sugerir_contenidos(df):
    col_cluster = encontrar_columna(df, ["cluster"])
    col_subcluster = encontrar_columna(df, ["subcluster"])
    col_keyword = encontrar_columna(df, ["palabra clave", "keyword"])

    if None in [col_cluster, col_subcluster, col_keyword]:
        raise KeyError("Faltan columnas clave para generar sugerencias.")

    sugerencias = []
    for _, fila in df.iterrows():
        cluster = fila[col_cluster]
        subcluster = fila[col_subcluster]
        kw = fila[col_keyword]
        sugerencias.append({
            "Cluster": cluster,
            "Subcluster": subcluster,
            "Keyword base": kw,
            "Título sugerido": f"Todo lo que debes saber sobre {kw} en {subcluster}",
            "Canal sugerido": "Blog + SEO"
        })
    return pd.DataFrame(sugerencias)
