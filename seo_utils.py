import pandas as pd


def filtrar_contenidos_con_potencial(df_keywords, df_auditoria):
    try:
        # Aseguramos tipos numéricos
        df_keywords["posición_promedio"] = pd.to_numeric(df_keywords["posición_promedio"], errors="coerce")
        df_keywords["volumen_de_búsqueda"] = pd.to_numeric(df_keywords["volumen_de_búsqueda"], errors="coerce")
        df_keywords["tráfico_estimado"] = pd.to_numeric(df_keywords["tráfico_estimado"], errors="coerce")
        df_keywords["dificultad"] = pd.to_numeric(df_keywords["dificultad"], errors="coerce")

        df_keywords = df_keywords.dropna(subset=["posición_promedio", "volumen_de_búsqueda", "tráfico_estimado", "dificultad"])

        # Unión por URL
        df_merged = pd.merge(
            df_keywords,
            df_auditoria,
            left_on="url",
            right_on="URL",
            how="inner"
        )

        # Normalización de leads
        df_merged["genera_leads"] = pd.to_numeric(df_merged["Leads 90 d"], errors="coerce").fillna(0)

        df_filtrado = df_merged[
            (df_merged["posición_promedio"] > 6) &
            (df_merged["posición_promedio"] <= 20) &
            (df_merged["volumen_de_búsqueda"] > 100) &
            (df_merged["tráfico_estimado"] > 0) &
            (df_merged["dificultad"] < 70)
        ]

        return df_filtrado[[
            "url", "palabra_clave", "posición_promedio", "volumen_de_búsqueda", "tráfico_estimado",
            "dificultad", "tipo_de_contenido", "Cluster", "Sub-cluster (si aplica)",
            "Vigencia del contenido", "genera_leads", "Etapa del funnel"
        ]]

    except Exception as e:
        raise RuntimeError(f"Error en filtrado: {e}")


def generar_palabras_clave_sugeridas(df_filtrado):
    try:
        combinaciones = df_filtrado.groupby(["Cluster", "Sub-cluster (si aplica)", "Etapa del funnel"])["palabra_clave"].apply(list).reset_index()
        combinaciones.rename(columns={"palabra_clave": "palabras_clave_sugeridas"}, inplace=True)
        return combinaciones
    except Exception as e:
        raise RuntimeError(f"Error al generar palabras clave sugeridas: {e}")


def generar_sugerencias_titulos_y_canales(df_palabras_sugeridas):
    try:
        df_palabras_sugeridas["sugerencias_titulo"] = df_palabras_sugeridas["palabras_clave_sugeridas"].apply(
            lambda x: [f"Estrategias para {palabra}" for palabra in x]
        )
        df_palabras_sugeridas["canales_recomendados"] = "Blog, SEO, LinkedIn"
        return df_palabras_sugeridas
    except Exception as e:
        raise RuntimeError(f"Error al generar sugerencias: {e}")
