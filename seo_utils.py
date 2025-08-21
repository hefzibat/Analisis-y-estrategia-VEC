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

def generar_ideas_con_keywords_externas(df_analisis, df_auditoria, df_keywords_externas):
    import random
    import pandas as pd

    # 1. Unificar y limpiar keywords existentes
    contenidos_existentes = pd.concat([
        df_analisis['palabra_clave'].astype(str).str.lower(),
        df_auditoria['Título'].astype(str).str.lower()
    ], axis=0).unique()

    nuevas_keywords = df_keywords_externas['palabra_clave'].dropna().astype(str).str.lower().unique()
    keywords_nuevas = [kw for kw in nuevas_keywords if not any(kw in contenido for contenido in contenidos_existentes)]

    if not keywords_nuevas:
        return pd.DataFrame(columns=["Palabra clave", "Título sugerido", "Funnel", "Canal sugerido", "Cluster", "Subcluster"])

    # 2. Plantillas variadas
    plantillas = [
        "Cómo implementar {kw} en tu empresa",
        "Guía esencial para entender {kw}",
        "Qué es {kw} y cómo usarlo con éxito",
        "Tácticas efectivas para aplicar {kw}",
        "Estrategia práctica para dominar {kw}",
        "Checklist para mejorar en {kw}",
        "Errores comunes al aplicar {kw} (y cómo evitarlos)",
        "Cómo usar {kw} para impulsar tus resultados",
        "¿Estás aprovechando {kw} como deberías?",
        "Claves para optimizar {kw} en tu negocio"
    ]

    # 3. Clasificar etapa del funnel
    def clasificar_funnel(kw):
        kw = kw.lower()
        if any(x in kw for x in ["qué es", "cómo funciona", "tendencias", "ideas", "ejemplos", "importancia"]):
            return "TOFU"
        elif any(x in kw for x in ["guía", "formato", "template", "comparativa", "tipos", "checklist", "beneficios", "ventajas"]):
            return "MOFU"
        elif any(x in kw for x in ["proveedor", "cotización", "demo", "caso de éxito", "contratar", "cliente", "precio"]):
            return "BOFU"
        else:
            return random.choices(["TOFU", "MOFU", "BOFU"], weights=[50, 30, 20])[0]

    # 4. Canal sugerido según funnel y tipo de keyword
    def sugerir_canal(kw, funnel):
        kw = kw.lower()

        if funnel == "TOFU":
            if any(x in kw for x in ["herramienta", "plantilla", "generador", "automatiza"]):
                return "Herramienta con IA"
            elif any(x in kw for x in ["blog", "tendencias", "qué es", "cómo funciona", "ejemplos"]):
                return "Blog"
            else:
                return random.choices(["Blog", "Herramienta con IA"], weights=[80, 20])[0]

        elif funnel == "MOFU":
            if any(x in kw for x in ["descargable", "ebook", "guía", "checklist", "manual", "formato", "template", "caso de éxito"]):
                return "Lead Magnet"
            else:
                return random.choices(["Lead Magnet", "Blog", "Email"], weights=[60, 30, 10])[0]

        elif funnel == "BOFU":
            if any(x in kw for x in ["email", "newsletter", "suscriptores", "correos", "embudo"]):
                return "Email"
            elif any(x in kw for x in ["caso de éxito", "cliente", "testimonio"]):
                return "Caso de éxito"
            elif any(x in kw for x in ["demo", "webinar", "cotización", "proveedor"]):
                return "Webinar"
            else:
                return random.choices(["Email", "Caso de éxito", "Webinar"], weights=[50, 30, 20])[0]

    # 5. Mapeo de clusters por coincidencia textual
    def clasificar_cluster(kw):
        for _, row in df_auditoria.iterrows():
            if isinstance(row['Cluster'], str) and isinstance(row['Sub-cluster (si aplica)'], str):
                if row['Cluster'].lower() in kw or row['Sub-cluster (si aplica)'].lower() in kw:
                    return row['Cluster'], row['Sub-cluster (si aplica)']
        return "Otros", "Otros"

    # 6. Resultados
    resultados = []
    for kw in keywords_nuevas:
        plantilla = random.choice(plantillas)
        titulo = plantilla.format(kw=kw)
        funnel = clasificar_funnel(kw)
        canal = sugerir_canal(kw, funnel)
        cluster, subcluster = clasificar_cluster(kw)

        resultados.append({
            "Palabra clave": kw,
            "Título sugerido": titulo,
            "Funnel": funnel,
            "Canal sugerido": canal,
            "Cluster": cluster,
            "Subcluster": subcluster
        })

    return pd.DataFrame(resultados)
