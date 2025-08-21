import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def filtrar_contenidos_con_potencial(df_keywords, df_auditoria):
    try:
        df_keywords["posición_promedio"] = pd.to_numeric(df_keywords["posición_promedio"], errors="coerce")
        df_keywords["volumen_de_búsqueda"] = pd.to_numeric(df_keywords["volumen_de_búsqueda"], errors="coerce")
        df_keywords["tráfico_estimado"] = pd.to_numeric(df_keywords["tráfico_estimado"], errors="coerce")
        df_keywords["dificultad"] = pd.to_numeric(df_keywords["dificultad"], errors="coerce")

        df_merged = pd.merge(df_keywords, df_auditoria, left_on="url", right_on="URL", how="inner")

        df_merged = df_merged.dropna(subset=["posición_promedio", "volumen_de_búsqueda", "tráfico_estimado", "dificultad"])

        df_merged["score"] = (
            (100 - df_merged["posición_promedio"]) * 0.25
            + df_merged["volumen_de_búsqueda"] * 0.25
            + df_merged["tráfico_estimado"] * 0.25
            + (100 - df_merged["dificultad"]) * 0.25
        )

        df_top = df_merged.sort_values("score", ascending=False).head(45)

        return df_top

    except Exception as e:
        raise ValueError(f"Error en filtrado: {e}")


def generar_keywords_por_cluster(df_top, df_auditoria):
    try:
        # Aseguramos que 'Cluster', 'Sub-cluster (si aplica)' y 'Etapa del funnel' están disponibles
        if not all(col in df_auditoria.columns for col in ["Cluster", "Sub-cluster (si aplica)", "Etapa del funnel"]):
            raise ValueError("Las columnas requeridas ('Cluster', 'Sub-cluster (si aplica)', 'Etapa del funnel') no se encuentran en el archivo de auditoría.")

        # Unimos con auditoría para obtener las columnas necesarias
        df_top = pd.merge(df_top, df_auditoria[["URL", "Cluster", "Sub-cluster (si aplica)", "Etapa del funnel"]],
                          left_on="url", right_on="URL", how="left")

        resultados = []

        for (cluster, subcluster, etapa), grupo in df_top.groupby(["Cluster", "Sub-cluster (si aplica)", "Etapa del funnel"]):
            vectorizer = TfidfVectorizer(stop_words='spanish', max_features=10)
            X = vectorizer.fit_transform(grupo["palabra_clave"])
            terms = vectorizer.get_feature_names_out()
            resultados.append({
                "Cluster": cluster,
                "Subcluster": subcluster,
                "Etapa del funnel": etapa,
                "Keywords sugeridas": ", ".join(terms)
            })

        return pd.DataFrame(resultados)

    except Exception as e:
        raise ValueError(f"Error en generación de keywords: {e}")
