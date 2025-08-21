import pandas as pd
import random

def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    # Limpiar nombres de columnas
    df_analisis.columns = df_analisis.columns.str.strip()
    df_auditoria.columns = df_auditoria.columns.str.strip()

    # Validar columnas necesarias
    columnas_analisis = [
        "url", "palabra_clave", "posición_promedio", "volumen_de_búsqueda",
        "dificultad", "tráfico_estimado", "tipo_de_contenido"
    ]
    columnas_auditoria = [
        "URL", "Cluster", "Sub-cluster (si aplica)", "Leads 90 d"
    ]
    for col in columnas_analisis:
        if col not in df_analisis.columns:
            raise ValueError(f"Falta la columna requerida en df_analisis: {col}")
    for col in columnas_auditoria:
        if col not in df_auditoria.columns:
            raise ValueError(f"Falta la columna requerida en df_auditoria: {col}")

    # Homologar URLs
    df_analisis["url"] = df_analisis["url"].str.lower().str.strip()
    df_auditoria["URL"] = df_auditoria["URL"].str.lower().str.strip()

    # Renombrar columnas para merge
    df_auditoria = df_auditoria.rename(columns={
        "URL": "url",
        "Leads 90 d": "genera_leads"
    })

    # Conservar columnas útiles
    columnas_utiles = ["url", "Cluster", "Sub-cluster (si aplica)", "genera_leads"]
    df_auditoria = df_auditoria[columnas_utiles]

    # Hacer merge
    df = pd.merge(df_analisis, df_auditoria, on="url", how="inner")

    # Convertir a numérico
    for col in ["posición_promedio", "volumen_de_búsqueda", "dificultad", "tráfico_estimado"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["genera_leads"] = pd.to_numeric(df["genera_leads"], errors="coerce").fillna(0)

    # Calcular score
    df["score"] = (
        (1 / (df["posición_promedio"] + 1)) * 0.3 +
        (df["volumen_de_búsqueda"] / df["volumen_de_búsqueda"].max()) * 0.3 +
        (df["tráfico_estimado"] / df["tráfico_estimado"].max()) * 0.2 +
        (1 - df["dificultad"] / 100) * 0.1 +
        (df["genera_leads"] > 0).astype(int) * 0.1
    )

    df_resultado = df.sort_values(by="score", ascending=False).head(45)

    # Renombrar columnas solo para visualización
    df_resultado = df_resultado.rename(columns={
        "palabra_clave": "Palabra Clave",
        "volumen_de_búsqueda": "Volumen",
        "tráfico_estimado": "Tráfico",
        "dificultad": "Dificultad",
        "genera_leads": "Genera Leads",
        "score": "Score"
    })

    # Seleccionar columnas a mostrar
    columnas_finales = [
        "url", "Palabra Clave", "Cluster", "Sub-cluster (si aplica)",
        "Volumen", "Tráfico", "Dificultad", "Genera Leads", "Score"
    ]
    return df_resultado[columnas_finales]
    
def generar_ideas_con_keywords_externas(df_analisis, df_auditoria, df_keywords_externas):
    # Normalizar y unificar columnas
    contenidos_existentes = pd.concat([df_analisis['palabra_clave'], df_auditoria['Título']], axis=0).astype(str).str.lower().unique()
    nuevas_keywords = df_keywords_externas['palabra_clave'].dropna().astype(str).str.lower().unique()

    # Filtrar solo las que no están ya usadas
    keywords_nuevas = [kw for kw in nuevas_keywords if not any(kw in contenido for contenido in contenidos_existentes)]

    # Plantillas variadas para generar títulos
    plantillas = [
        "Cómo lograr {kw} en 5 pasos",
        "Errores comunes al intentar {kw} y cómo evitarlos",
        "¿Vale la pena enfocarse en {kw}? Descúbrelo aquí",
        "Estrategias efectivas para {kw} que sí funcionan",
        "Domina el arte de {kw} sin complicarte",
        "Qué es {kw} y por qué deberías saberlo hoy",
        "Guía práctica para empezar con {kw}",
        "Los secretos de {kw} que nadie te cuenta"
    ]

    # Función para sugerir canal según el tipo de keyword
    def sugerir_canal(kw):
        if any(palabra in kw for palabra in ["qué es", "cómo", "guía", "pasos", "estrategia"]):
            return "Blog"
        elif any(palabra in kw for palabra in ["errores", "evitar", "mitos"]):
            return "Carrusel Instagram / LinkedIn"
        elif any(palabra in kw for palabra in ["secreto", "truco", "consejo"]):
            return "Reel / YouTube Shorts"
        elif any(palabra in kw for palabra in ["domina", "aprende", "mejorar"]):
            return "Video educativo largo"
        else:
            return "Blog o Carrusel"

    resultados = []
    for kw in keywords_nuevas:
        plantilla = random.choice(plantillas)
        titulo = plantilla.format(kw=kw)
        canal = sugerir_canal(kw)
        resultados.append({
            "Palabra clave": kw,
            "Título sugerido": titulo,
            "Canal sugerido": canal
        })

    return pd.DataFrame(resultados)
