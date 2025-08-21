
# SEO VEC Estrategia

Esta app de Streamlit permite analizar contenidos existentes para identificar oportunidades de optimización SEO, agruparlos por clústeres y subclústeres, y sugerir una estrategia de generación de nuevas keywords, basada en dos fuentes de datos principales.

## 🔧 Funcionalidades principales

1. **Análisis de contenidos existentes**
   - Detecta qué contenidos vale la pena optimizar.
   - Usa datos como posición, volumen, tráfico, dificultad y leads generados.
   - Muestra clúster y subclúster por contenido.
   - Clasifica los contenidos por etapa del funnel (TOFU, MOFU, BOFU).

2. **Visualización por clúster y subclúster**
   - Representación visual de cómo se distribuyen los contenidos.
   - Enlaces activos para facilitar auditoría.

3. **Sugerencias de keywords para estrategia de contenido**
   - Genera nuevas keywords por clúster.
   - Propone canales recomendados: blog, email, redes sociales, webinars, etc.

---

## 📁 Estructura esperada de los archivos

La app requiere dos archivos de entrada:

### 1. **Resultado_Final_Keywords.xlsx**
Contiene los datos actuales de los contenidos publicados. Columnas requeridas:

- `URL`
- `PALABRA CLAVE`
- `POSICIÓN`
- `VOLUMEN`
- `DIFICULTAD`
- `TRÁFICO`

### 2. **VEC_ Auditoría.xlsx**
Contiene datos de auditoría interna. Columnas requeridas:

- `URL`
- `CLUSTER`
- `SUBCLUSTER`
- `LEADS 90 DÍAS`
- `ETAPA DEL FUNNEL`

Ambos archivos deben cargarse en la parte izquierda del sidebar de la app.

---

## 🛠️ Requisitos de instalación

### Python
Recomendado: Python 3.10+

### Instalación de dependencias

```bash
pip install -r requirements.txt
