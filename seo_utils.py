import pandas as pd

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
def generar_ideas_con_keywords_externas(df_auditoria, df_keywords_externas, df_contenidos_potenciales):
    import numpy as np

    # Preprocesamiento de palabras clave externas
    df_keywords_externas = df_keywords_externas.dropna()
    df_keywords_externas.columns = [col.lower().strip() for col in df_keywords_externas.columns]
    col_keywords = [col for col in df_keywords_externas.columns if 'keyword' in col][0]
    df_keywords_externas = df_keywords_externas.rename(columns={col_keywords: 'palabra_clave'})
    df_keywords_externas['palabra_clave'] = df_keywords_externas['palabra_clave'].str.lower().str.strip()

    # Palabras ya usadas en contenidos actuales
    usadas = df_contenidos_potenciales['palabra_clave'].str.lower().str.strip().unique()

    # Filtramos las nuevas
    df_nuevas = df_keywords_externas[~df_keywords_externas['palabra_clave'].isin(usadas)].copy()

    # Unimos con auditoría por coincidencia parcial en palabra_clave con título o keywords
    df_auditoria['todo'] = df_auditoria[['Título', 'Cluster', 'Sub-cluster (si aplica)', 'Área temática']].fillna('').agg(' '.join, axis=1).str.lower()
    df_nuevas['Cluster'] = ''
    df_nuevas['Subcluster'] = ''

    for i, row in df_nuevas.iterrows():
        match = df_auditoria[df_auditoria['todo'].str.contains(row['palabra_clave'])]
        if not match.empty:
            df_nuevas.at[i, 'Cluster'] = match.iloc[0]['Cluster']
            df_nuevas.at[i, 'Subcluster'] = match.iloc[0]['Sub-cluster (si aplica)']

    # Función para generar títulos posibles
    def generar_titulo(palabra):
        return f"Cómo aprovechar {palabra} en tu estrategia de contenido"

    df_nuevas['Título posible'] = df_nuevas['palabra_clave'].apply(generar_titulo)

    # Heurística para canal sugerido
    def sugerir_canal(palabra):
        palabra = palabra.lower()
        if any(w in palabra for w in ['automatiza', 'herramienta', 'bot', 'asistente', 'prompt']):
            return 'Herramienta de IA'
        elif any(w in palabra for w in ['funnel', 'embudo', 'convierte', 'cliente']):
            return 'Flujo'
        elif any(w in palabra for w in ['guía', 'template', 'formato', 'ejemplo']):
            return 'Lead magnet'
        elif any(w in palabra for w in ['email', 'newsletter', 'correos']):
            return 'Email'
        else:
            return 'Blog'

    df_nuevas['Canal sugerido'] = df_nuevas['palabra_clave'].apply(sugerir_canal)

    # Columnas finales
    columnas_finales = ['palabra_clave', 'Título posible', 'Cluster', 'Subcluster', 'Canal sugerido']
    df_resultado = df_nuevas[columnas_finales].copy()
    df_resultado.columns = ['Palabra clave', 'Título posible', 'Cluster', 'Subcluster', 'Canal sugerido']

    return df_resultado
