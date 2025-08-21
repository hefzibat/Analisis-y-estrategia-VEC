import pandas as pd

def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    # Usar nombres reales de columnas en minúsculas
    columnas_requeridas_analisis = [
        'url', 'palabra_clave', 'posición_promedio',
        'volumen_de_búsqueda', 'dificultad', 'tráfico_estimado'
    ]
    columnas_requeridas_auditoria = ['url', 'cluster', 'sub-cluster (si aplica)', 'leads 90 d']

    for col in columnas_requeridas_analisis:
        if col not in df_analisis.columns:
            raise ValueError(f"Falta la columna requerida en df_analisis: {col}")
    for col in columnas_requeridas_auditoria:
        if col not in df_auditoria.columns:
            raise ValueError(f"Falta la columna requerida en df_auditoria: {col}")

    df = df_analisis.merge(
        df_auditoria,
        on='url',
        how='left',
        suffixes=('', '_auditoria')
    )

    # Crear score simple con ponderación de tráfico, volumen y dificultad invertida
    df['score'] = (
        df['tráfico_estimado'].fillna(0) * 0.4 +
        df['volumen_de_búsqueda'].fillna(0) * 0.4 +
        (100 - df['dificultad'].fillna(100)) * 0.2
    )

    # Rellenar leads faltantes con 0
    df['leads 90 d'] = df['leads 90 d'].fillna(0)

    # Renombrar para mostrar en tabla final
    df['Cluster'] = df['cluster']
    df['Subcluster'] = df['sub-cluster (si aplica)']
    df['Palabra clave'] = df['palabra_clave']
    df['Volumen'] = df['volumen_de_búsqueda']
    df['Tráfico'] = df['tráfico_estimado']
    df['Dificultad'] = df['dificultad']
    df['Genera Leads'] = df['leads 90 d']
    df['URL'] = df['url'].str.strip()

    columnas_finales = [
        'URL', 'Palabra clave', 'Cluster', 'Subcluster',
        'Volumen', 'Tráfico', 'Dificultad', 'Genera Leads', 'score'
    ]
    df_resultado = df[columnas_finales].sort_values(by='score', ascending=False)

    return df_resultado
