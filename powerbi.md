# DATAMART PRESUPUESTAL MUNICIPAL

El modelo implementado corresponde a un **Data Mart Presupuestal Municipal** diseñado bajo arquitectura de **esquema estrella (Kimball)**, orientado al análisis financiero de gobiernos locales del Perú. Su objetivo principal es permitir el análisis eficiente de la ejecución presupuestal, recaudación e inversión municipal a nivel temporal, geográfico, institucional y financiero.

La tabla central del modelo es **FACT_PRESUPUESTO**, que almacena las métricas clave del negocio: `MONTO_PIA`, `MONTO_PIM`, `MONTO_RECAUDADO` y `TASA_EJECUCION`. Esta tabla concentra el volumen principal de datos y se conecta con las dimensiones mediante claves foráneas, permitiendo el análisis multidimensional del comportamiento financiero de las municipalidades.

La dimensión de tiempo (**DIM_TIEMPO**) permite analizar la información por año, mes, trimestre, semestre y bimestre, facilitando el estudio de tendencias y estacionalidad del gasto y la recaudación. La dimensión geográfica (**DIM_UBICACION**) organiza la información por UBIGEO, permitiendo análisis a nivel de departamento, provincia y distrito con alta granularidad territorial.

La dimensión institucional (**DIM_ENTIDAD**) describe a cada municipalidad o ejecutora, incluyendo su nivel de gobierno y el tipo de municipalidad (provincial = 1 o distrital = 2 mediante `Tipomuni`), lo que permite comparar la eficiencia entre tipos de gobiernos locales. Finalmente, la dimensión financiera (**DIM_FINANCIERA**) estructura la información presupuestal según la jerarquía del SIAF, desde la fuente de financiamiento hasta la subgenérica del ingreso.

En conjunto, el modelo permite análisis avanzados de desempeño municipal, comparaciones territoriales, evaluación de eficiencia presupuestal y detección de brechas de gestión.

---

# Dashboard 1: Resumen Ejecutivo Nacional

## Objetivo

Proporcionar una visión general del desempeño financiero de las municipalidades a nivel nacional, permitiendo evaluar rápidamente la ejecución presupuestal y la recaudación.

## Descripción

Este dashboard consolida los principales indicadores financieros del sistema municipal, utilizando métricas como `MONTO_PIA`, `MONTO_PIM`, `MONTO_RECAUDADO` y `TASA_EJECUCION`. Permite analizar la evolución anual del presupuesto y la eficiencia de ejecución mediante comparaciones temporales.

## Visualizaciones recomendadas

| Visual | Campos |
|---|---|
| KPI Cards | SUM(MONTO_PIA), SUM(MONTO_PIM), SUM(MONTO_RECAUDADO) |
| Medidor (Gauge) | Promedio de TASA_EJECUCION |
| Gráfico de líneas | anio vs MONTO_RECAUDADO |
| Gráfico de columnas | anio vs MONTO_PIM |
| Segmentadores | anio, departamento |
---

# Dashboard 2: Análisis Territorial Municipal

## Objetivo

Identificar la distribución geográfica del presupuesto municipal y detectar desigualdades en la asignación y ejecución de recursos a nivel nacional.

## Descripción

Este dashboard analiza el comportamiento financiero por ubicación geográfica utilizando la dimensión `DIM_UBICACION`. Permite observar qué departamentos, provincias y distritos concentran mayores niveles de recaudación y presupuesto.

## Visualizaciones recomendadas

| Visual | Campos |
|---|---|
| Mapa geográfico | departamento o provincia vs MONTO_RECAUDADO |
| Gráfico de barras | departamento vs MONTO_PIM |
| Tabla dinámica | departamento, provincia, distrito |
| Heatmap | departamento vs TASA_EJECUCION |
| Segmentadores | departamento, provincia, distrito |

---

# Dashboard 3: Eficiencia Institucional Municipal

## Objetivo

Comparar el desempeño financiero de las municipalidades según su tipo y nivel de gestión institucional.

## Descripción

Este dashboard utiliza la dimensión `DIM_ENTIDAD` y el campo `Tipomuni` para analizar diferencias entre municipalidades provinciales y distritales. Evalúa indicadores financieros para identificar niveles de eficiencia y capacidad de gestión presupuestal.

## Visualizaciones recomendadas

| Visual | Campos |
|---|---|
| Gráfico de barras | EJECUTORA_NOMBRE vs TASA_EJECUCION |
| Gráfico circular | Tipomuni |
| Tabla ranking | Municipalidades con mayor ejecución |
| KPI Cards | Promedio TASA_EJECUCION |
| Segmentadores | Tipomuni, departamento |

---

# Dashboard 4: Ingresos y Financiamiento Municipal

## Objetivo

Analizar la composición de los ingresos municipales según fuentes de financiamiento y estructura presupuestal del SIAF.

## Descripción

Este dashboard se basa en la dimensión `DIM_FINANCIERA` para descomponer los ingresos por fuente de financiamiento, rubro, genérica y subgenérica. Permite identificar la dependencia de recursos y analizar la estructura financiera municipal.

## Visualizaciones recomendadas

| Visual | Campos |
|---|---|
| Treemap | FUENTE_FINANCIAMIENTO_NOMBRE vs MONTO_RECAUDADO |
| Gráfico de barras apiladas | RUBRO_NOMBRE vs MONTO_RECAUDADO |
| Tabla dinámica | FUENTE_FINANCIAMIENTO, RUBRO, GENERICA |
| Gráfico circular | Participación por fuente de financiamiento |
| Segmentadores | fuente financiamiento, rubro |

---

# Dashboard 5: Tendencias y Estacionalidad

## Objetivo

Identificar patrones temporales y estacionales en la recaudación y ejecución del presupuesto municipal.

## Descripción

Este dashboard utiliza la dimensión `DIM_TIEMPO` para analizar la evolución mensual, trimestral y anual de la recaudación y ejecución presupuestal. Permite detectar periodos de mayor actividad financiera y realizar comparaciones interanuales.

## Visualizaciones recomendadas

| Visual | Campos |
|---|---|
| Gráfico de líneas | nombre_mes vs MONTO_RECAUDADO |
| Gráfico de áreas | trimestre vs MONTO_PIM |
| KPI Cards | Promedio TASA_EJECUCION |
| Tabla temporal | anio, trimestre, semestre |
| Segmentadores | anio, trimestre |

---

# Dashboard 6: Riesgo y Alertas Presupuestales

## Objetivo

Detectar municipalidades con baja eficiencia en la ejecución del presupuesto y posibles brechas en la gestión financiera.

## Descripción

Este dashboard combina variables de todas las dimensiones para identificar casos críticos donde existe alto presupuesto pero baja ejecución presupuestal. Permite visualizar alertas de gestión y rankings de municipalidades con menor desempeño financiero.

## Visualizaciones recomendadas

| Visual | Campos |
|---|---|
| Scatter plot | MONTO_PIM vs TASA_EJECUCION |
| Tabla ranking | Municipalidades con menor ejecución |
| KPI Cards | Total municipalidades críticas |
| Gráfico de barras | departamento vs TASA_EJECUCION |
| Segmentadores | departamento, Tipomuni |