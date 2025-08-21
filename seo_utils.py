import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

def filtrar_contenidos_con_potencial(df_analisis, df_auditoria):
    df = df_analisis.copy()

    df = df.rename(columns={
        'url': 'URL',
        'palabra_clave': 'palabra_clave',
        'posición_promedio': 'posición',
        'volumen_de_búsqueda': 'volumen',
        'dificultad': 'dificultad',
        'tráfico_estimado': 'tráfico',
        'tipo_de_contenido': 'tipo_de_contenido'
    })

    df = df.merge(
        df_auditoria[['URL', 'Cluster', 'Sub-cluster (si aplica)', 'Leads 90 d *(esta se usará como \'genera_leads\')']],
        on='URL',
        how='left'
    )

    df['Cluster'] = df['Cluster'].fillna('Sin cluster')
    df['Sub-cluster (si aplica)'] = df['Sub-cluster (si aplica)'].fillna('Sin subcluster')

    df['genera_leads'] = df['Leads 90 d *(esta se usará como \'genera_leads\')'].fillna(0)

    scaler = MinMaxScaler()
    df[['posición_norm', 'volumen_norm', 'tráfico_norm']] = scaler.fit_transform(df[['posición', 'volumen', 'tráfico']])

    df['score_optimizacion'] = (
        (1 - df['posición_norm']) * 0.4 +
        df['volumen_norm'] * 0.3 +
        df['tráfico_norm'] * 0.3 +
        df['genera_leads'] * 0.1
    )

    df = df.sort_values(by='score_optimizacion', ascending=False)

    columnas_resultado = ['palabra_clave', 'URL', 'Cluster', 'Sub-cluster (si aplica)', 'posición', 'volumen', 'tráfico', 'genera_leads', 'score_optimizacion']
    return df[columnas_resultado].head(45)

def generar_keywords_por_cluster(df_analisis, df_auditoria, df_keywords_externas=None):
    df = df_analisis.copy()
    df_aud = df_auditoria.copy()

    df.rename(columns={'palabra_clave': 'palabra_clave'}, inplace=True)
    df_aud.rename(columns={'URL': 'URL', 'Cluster': 'cluster', 'Sub-cluster (si aplica)': 'subcluster'}, inplace=True)

    df = df.merge(df_aud[['URL', 'cluster', 'subcluster']], on='URL', how='left')

    if df_keywords_externas is not None:
        df_ext = df_keywords_externas.copy()
        df_ext.columns = [col.lower().strip() for col in df_ext.columns]

        col_kw = [col for col in df_ext.columns if 'keyword' in col or 'palabra' in col or 'search' in col]
        if not col_kw:
            raise ValueError("No se encontró una columna de palabras clave válida en el archivo externo.")

        df_ext.rename(columns={col_kw[0]: 'palabra_clave'}, inplace=True)
        df_ext = df_ext[['palabra_clave'] + [col for col in df_ext.columns if col != 'palabra_clave']]

        df_ext['cluster'] = None
        df_ext['subcluster'] = None

        for i, ext_kw in df_ext.iterrows():
            matches = df[df['palabra_clave'].str.contains(ext_kw['palabra_clave'], case=False, na=False)]
            if not matches.empty:
                df_ext.at[i, 'cluster'] = matches['cluster'].mode()[0]
                df_ext.at[i, 'subcluster'] = matches['subcluster'].mode()[0]

        df_comb = pd.concat([df[['palabra_clave', 'cluster', 'subcluster']], df_ext], ignore_index=True)
    else:
        df_comb = df[['palabra_clave', 'cluster', 'subcluster']]

    df_comb = df_comb.dropna(subset=['palabra_clave'])
    df_comb['palabra_clave'] = df_comb['palabra_clave'].astype(str)

    resultados = []

    for (cluster, subcluster), grupo in df_comb.groupby(['cluster', 'subcluster']):
        vectorizer = TfidfVectorizer()
        try:
            X = vectorizer.fit_transform(grupo['palabra_clave'])
        except ValueError:
            continue
        if X.shape[0] < 2:
            continue
        kmeans = KMeans(n_clusters=min(2, X.shape[0]), random_state=42, n_init='auto')
        kmeans.fit(X)
        grupo['grupo_keywords'] = kmeans.labels_
        for grupo_id, palabras in grupo.groupby('grupo_keywords'):
            resultado = {
                'cluster': cluster,
                'subcluster': subcluster,
                'grupo_keywords': grupo_id,
                'keywords': ', '.join(palabras['palabra_clave'].tolist())
            }
            resultados.append(resultado)

    return pd.DataFrame(resultados)
