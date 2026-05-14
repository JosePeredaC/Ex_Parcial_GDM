# Ex_Parcial_GDM
# Exámen parcial del curso de Gestión de Datos Masivos

## Descripción General

Este proyecto tiene como objetivo construir una arquitectura de datos tipo **Medallion** para analizar información relacionada con el presupuesto y la ejecución de ingresos municipales, incorporando datos del **SIAF**, **SISMEPRE** y **RENAMU**.

La arquitectura Medallion se organiza en tres capas principales:

| Capa | Propósito |
|---|---|
| **Bronze** | Almacenar los datos crudos descargados desde las fuentes oficiales. |
| **Silver** | Limpiar, estandarizar, validar y preparar los datos. |
| **Gold** | Construir tablas analíticas listas para visualización y toma de decisiones. |

En esta primera etapa se implementa la **capa Bronze**.

---

# 1. Construcción de la Capa Bronze

La primera etapa del proyecto consiste en implementar la capa **Bronze** dentro de la arquitectura Medallion.

La capa Bronze funciona como la **zona de aterrizaje de datos crudos**. Su objetivo es conservar una copia fiel de los archivos originales publicados por las fuentes oficiales, sin aplicar procesos de limpieza, transformación, homologación, eliminación de registros ni cálculo de indicadores.

Esta decisión permite mantener:

- **Trazabilidad** sobre el origen de los datos.
- **Reproducibilidad** del análisis.
- **Auditoría** de los archivos utilizados.
- **Historial de versiones** ante posibles actualizaciones de las fuentes oficiales.

---

## 1.1. Fuentes de Datos

Para esta primera versión se consideran tres fuentes oficiales:

| Fuente | Dataset | Descripción | Tipo de publicación |
|---|---|---|---|
| **MEF / SIAF** | Presupuesto y ejecución de ingreso | Información presupuestal y de ejecución de ingresos. | Archivos CSV divididos por año. |
| **MEF / SISMEPRE** | Seguimiento de la meta del impuesto predial | Información relacionada con preguntas, respuestas, formularios, estadísticas y diccionarios del seguimiento de la meta del impuesto predial. | Múltiples archivos CSV. |
| **INEI / RENAMU** | Registro Nacional de Municipalidades 2022 | Información del Registro Nacional de Municipalidades. | Archivo ZIP con data completa y diccionario. |

---

## 1.2. Estructura Base del Proyecto

La estructura inicial del proyecto es la siguiente:

```text
Ex_Parcial_Gestión_De_Datos_Masivos/
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── docs/
├── notebooks/
├── scripts/
│   └── 01_ingesta_bronze.py
├── .gitignore
└── README.md
```

### Descripción de Carpetas

| Carpeta | Propósito |
|---|---|
| `data/bronze/` | Almacena los archivos originales descargados desde las fuentes oficiales. |
| `data/silver/` | Almacenará los datos limpios, estandarizados y validados. |
| `data/gold/` | Almacenará las tablas finales listas para análisis y visualización. |
| `docs/` | Documentación complementaria del proyecto. |
| `notebooks/` | Notebooks exploratorios o de análisis. |
| `scripts/` | Scripts automatizados del pipeline de datos. |
| `logs/` | Carpeta generada automáticamente para registrar resúmenes de ejecución. |

---

## 1.3. Script Implementado

Se implementó el siguiente script para automatizar la ingesta de la capa Bronze:

```text
scripts/01_ingesta_bronze.py
```

Este script se encarga de descargar los archivos originales desde sus enlaces directos y almacenarlos en la estructura Bronze del proyecto.

---

## 1.4. Objetivo del Script

El script `01_ingesta_bronze.py` realiza las siguientes tareas:

1. Detecta automáticamente la carpeta raíz del proyecto.
2. Crea las carpetas necesarias para la capa Bronze y los logs de ejecución.
3. Define las fuentes y recursos descargables de SIAF, SISMEPRE y RENAMU.
4. Descarga los archivos originales desde las URLs oficiales.
5. Guarda los archivos sin modificarlos dentro de `data/bronze/`.
6. Genera un snapshot por cada ejecución.
7. Calcula un checksum SHA-256 para cada archivo descargado.
8. Genera metadata individual por cada recurso.
9. Genera metadata general por cada fuente.
10. Genera un resumen de ejecución dentro de la carpeta `logs/`.

---

## 1.5. Principio de Inmutabilidad

La capa Bronze fue diseñada bajo un principio de **inmutabilidad**.

Esto significa que los archivos descargados no se sobrescriben. Cada ejecución del script genera una nueva carpeta de snapshot identificada con fecha y hora.

El formato del snapshot es:

```text
fecha_descarga=YYYY-MM-DD_HHMMSS
```

Ejemplo:

```text
fecha_descarga=2026-05-13_204500
```

Este enfoque permite conservar diferentes versiones de los archivos en caso las fuentes oficiales se actualicen.

---

## 1.6. Estrategia de Organización en Bronze

La organización de los archivos en Bronze respeta la estructura natural de cada fuente.

No se fuerza a todas las fuentes a tener el mismo formato, porque cada una publica sus datos de manera distinta.

---

### 1.6.1. Organización de SIAF

Los archivos del SIAF se publican por año. Por ello, dentro de Bronze se organizan en carpetas anuales.

```text
data/bronze/siaf_ingresos/
└── fecha_descarga=YYYY-MM-DD_HHMMSS/
    ├── anio=2019/
    │   ├── 2019-Ingreso.csv
    │   └── metadata_2019-Ingreso.json
    ├── anio=2020/
    │   ├── 2020-Ingreso.csv
    │   └── metadata_2020-Ingreso.json
    ├── anio=2021/
    │   ├── 2021-Ingreso.csv
    │   └── metadata_2021-Ingreso.json
    ├── anio=2022/
    │   ├── 2022-Ingreso.csv
    │   └── metadata_2022-Ingreso.json
    ├── anio=2023/
    │   ├── 2023-Ingreso.csv
    │   └── metadata_2023-Ingreso.json
    ├── anio=2024/
    │   ├── 2024-Ingreso.csv
    │   └── metadata_2024-Ingreso.json
    ├── anio=2025/
    │   ├── 2025-Ingreso-Mensual.csv
    │   └── metadata_2025-Ingreso-Mensual.json
    ├── anio=2026/
    │   ├── 2026-Ingreso-Mensual.csv
    │   └── metadata_2026-Ingreso-Mensual.json
    └── metadata_fuente.json
```

#### Recursos SIAF considerados

| Año | Archivo | Tipo |
|---:|---|---|
| 2019 | `2019-Ingreso.csv` | Data anual |
| 2020 | `2020-Ingreso.csv` | Data anual |
| 2021 | `2021-Ingreso.csv` | Data anual |
| 2022 | `2022-Ingreso.csv` | Data anual |
| 2023 | `2023-Ingreso.csv` | Data anual |
| 2024 | `2024-Ingreso.csv` | Data anual |
| 2025 | `2025-Ingreso-Mensual.csv` | Data mensual |
| 2026 | `2026-Ingreso-Mensual.csv` | Data mensual |

---

### 1.6.2. Organización de SISMEPRE

SISMEPRE publica varios archivos CSV. Algunos corresponden a datos operativos y otros a diccionarios de datos.

Por ello, dentro de Bronze se separan en dos carpetas:

- `datos/`
- `diccionarios/`

```text
data/bronze/sismepre_predial/
└── fecha_descarga=YYYY-MM-DD_HHMMSS/
    ├── datos/
    │   ├── rentas_preguntas.csv
    │   ├── metadata_rentas_preguntas.json
    │   ├── rentas_estadistica.csv
    │   ├── metadata_rentas_estadistica.json
    │   ├── rentas_formulario.csv
    │   ├── metadata_rentas_formulario.json
    │   ├── rentas_esat_estadistica_atm.csv
    │   ├── metadata_rentas_esat_estadistica_atm.json
    │   ├── rentas_respuestas.csv
    │   ├── metadata_rentas_respuestas.json
    │   ├── rentas_ano_aplicacion.csv
    │   ├── metadata_rentas_ano_aplicacion.json
    │   ├── rentas_entidad_estado.csv
    │   └── metadata_rentas_entidad_estado.json
    ├── diccionarios/
    │   ├── rentas_ano_aplicacion_diccionario.csv
    │   ├── metadata_rentas_ano_aplicacion_diccionario.json
    │   ├── rentas_preguntas_diccionario.csv
    │   ├── metadata_rentas_preguntas_diccionario.json
    │   ├── rentas_estadistica_diccionario.csv
    │   ├── metadata_rentas_estadistica_diccionario.json
    │   ├── rentas_entidad_estado_diccionario.csv
    │   ├── metadata_rentas_entidad_estado_diccionario.json
    │   ├── rentas_formulario_diccionario.csv
    │   ├── metadata_rentas_formulario_diccionario.json
    │   ├── rentas_esat_estadistica_atm_diccionario.csv
    │   ├── metadata_rentas_esat_estadistica_atm_diccionario.json
    │   ├── rentas_respuestas_diccionario.csv
    │   └── metadata_rentas_respuestas_diccionario.json
    └── metadata_fuente.json
```

#### Recursos SISMEPRE considerados

##### Archivos de datos

| Archivo | Categoría | Tipo |
|---|---|---|
| `rentas_preguntas.csv` | `datos` | Data |
| `rentas_estadistica.csv` | `datos` | Data |
| `rentas_formulario.csv` | `datos` | Data |
| `rentas_esat_estadistica_atm.csv` | `datos` | Data |
| `rentas_respuestas.csv` | `datos` | Data |
| `rentas_ano_aplicacion.csv` | `datos` | Data |
| `rentas_entidad_estado.csv` | `datos` | Data |

##### Archivos de diccionario

| Archivo | Categoría | Tipo |
|---|---|---|
| `rentas_ano_aplicacion_diccionario.csv` | `diccionarios` | Diccionario |
| `rentas_preguntas_diccionario.csv` | `diccionarios` | Diccionario |
| `rentas_estadistica_diccionario.csv` | `diccionarios` | Diccionario |
| `rentas_entidad_estado_diccionario.csv` | `diccionarios` | Diccionario |
| `rentas_formulario_diccionario.csv` | `diccionarios` | Diccionario |
| `rentas_esat_estadistica_atm_diccionario.csv` | `diccionarios` | Diccionario |
| `rentas_respuestas_diccionario.csv` | `diccionarios` | Diccionario |

---

### 1.6.3. Organización de RENAMU

RENAMU 2022 se publica como un archivo ZIP. Este archivo se conserva completo en Bronze, sin descomprimir ni alterar su contenido.

```text
data/bronze/renamu_2022/
└── fecha_descarga=YYYY-MM-DD_HHMMSS/
    ├── data_completa/
    │   ├── 2022.zip
    │   └── metadata_renamu_2022_zip.json
    └── metadata_fuente.json
```

#### Recurso RENAMU considerado

| Archivo | Categoría | Tipo |
|---|---|---|
| `2022.zip` | `data_completa` | ZIP |

---

## 1.7. Metadata Generada

El proceso genera metadata en dos niveles:

1. **Metadata por recurso**
2. **Metadata por fuente**

---

### 1.7.1. Metadata por Recurso

Por cada archivo descargado se genera un archivo JSON con información de trazabilidad.

Ejemplo:

```text
metadata_2026-Ingreso-Mensual.json
```

La metadata por recurso incluye:

| Campo | Descripción |
|---|---|
| `nombre_recurso` | Nombre lógico del recurso descargado. |
| `categoria` | Carpeta o partición donde se almacena el recurso. |
| `tipo_recurso` | Tipo de archivo o rol dentro de la fuente. |
| `formato` | Formato del archivo descargado. |
| `anio` | Año asociado al recurso, cuando corresponde. |
| `url_descarga` | URL directa desde la cual se descargó el archivo. |
| `archivo_bronze` | Ruta local donde se guardó el archivo. |
| `snapshot_id` | Identificador del snapshot de descarga. |
| `fecha_descarga` | Fecha y hora en que se descargó el recurso. |
| `capa` | Capa de la arquitectura Medallion. |
| `tratamiento` | Descripción del tratamiento aplicado al archivo. |
| `descarga` | Estado técnico de la descarga. |
| `checksum_sha256` | Hash SHA-256 del archivo descargado. |

El tratamiento aplicado a los recursos de Bronze es:

```text
Archivo original descargado y guardado sin modificaciones.
```

---

### 1.7.2. Metadata por Fuente

Además de la metadata individual por recurso, se genera un archivo general por cada fuente:

```text
metadata_fuente.json
```

Este archivo resume la información de la fuente completa, incluyendo:

- Nombre de la fuente.
- Dataset.
- Página del dataset.
- Descripción.
- Snapshot asociado.
- Fecha de descarga.
- Lista de recursos descargados.
- Metadata técnica de cada recurso.

---

## 1.8. Checksum SHA-256

El script calcula un checksum **SHA-256** para cada archivo descargado correctamente.

Este valor permite:

- Verificar la integridad del archivo.
- Comparar si un archivo cambió entre dos descargas.
- Detectar diferencias entre snapshots.
- Evitar depender únicamente del nombre del archivo.

Ejemplo de campo en metadata:

```json
{
  "checksum_sha256": "valor_hash_del_archivo"
}
```

---

## 1.9. Logs de Ejecución

El script genera un resumen general de cada ejecución dentro de la carpeta:

```text
logs/
```

El archivo generado tiene un nombre similar a:

```text
resumen_ingesta_bronze_fecha_descarga=YYYY-MM-DD_HHMMSS.json
```

Este resumen permite revisar:

- Snapshot ejecutado.
- Fecha de inicio.
- Fecha de fin.
- Duración total.
- Fuentes procesadas.
- Cantidad de recursos descargados correctamente.
- Cantidad de recursos con error.
- Ruta de cada archivo descargado.
- Ruta de cada metadata generada.
- Checksum de cada recurso.

---

## 1.10. Ejecución del Script

El script debe ejecutarse desde la raíz del proyecto:

```powershell
python .\scripts\01_ingesta_bronze.py
```

También puede ejecutarse desde otra ubicación, ya que el script detecta automáticamente la raíz del proyecto a partir de su propia ubicación.

---

## 1.11. Resultado Esperado

Después de ejecutar el script, la estructura del proyecto debería verse de forma similar a la siguiente:

```text
Ex_Parcial_Gestión_De_Datos_Masivos/
├── data/
│   ├── bronze/
│   │   ├── siaf_ingresos/
│   │   │   └── fecha_descarga=YYYY-MM-DD_HHMMSS/
│   │   │       ├── anio=2019/
│   │   │       ├── anio=2020/
│   │   │       ├── anio=2021/
│   │   │       ├── anio=2022/
│   │   │       ├── anio=2023/
│   │   │       ├── anio=2024/
│   │   │       ├── anio=2025/
│   │   │       ├── anio=2026/
│   │   │       └── metadata_fuente.json
│   │   ├── sismepre_predial/
│   │   │   └── fecha_descarga=YYYY-MM-DD_HHMMSS/
│   │   │       ├── datos/
│   │   │       ├── diccionarios/
│   │   │       └── metadata_fuente.json
│   │   └── renamu_2022/
│   │       └── fecha_descarga=YYYY-MM-DD_HHMMSS/
│   │           ├── data_completa/
│   │           └── metadata_fuente.json
│   ├── silver/
│   └── gold/
├── docs/
├── logs/
│   └── resumen_ingesta_bronze_fecha_descarga=YYYY-MM-DD_HHMMSS.json
├── notebooks/
├── scripts/
│   └── 01_ingesta_bronze.py
├── .gitignore
└── README.md
```

---

## 1.12. Decisiones de Diseño

| Decisión | Justificación |
|---|---|
| Usar una capa Bronze inmutable | Permite conservar versiones históricas de los archivos descargados. |
| Crear snapshots por ejecución | Facilita la trazabilidad cuando las fuentes oficiales se actualizan. |
| No sobrescribir archivos anteriores | Evita pérdida de evidencia y permite reproducir análisis anteriores. |
| Descargar archivos completos | Las fuentes se publican como archivos completos; no se asumió carga incremental. |
| Separar recursos por fuente | Cada fuente tiene una estructura de publicación distinta. |
| Organizar SIAF por año | El dataset se publica en archivos anuales o mensuales por año. |
| Separar datos y diccionarios en SISMEPRE | Facilita la interpretación posterior en Silver. |
| Conservar RENAMU como ZIP original | Mantiene intacta la fuente publicada por INEI. |
| Generar metadata por recurso | Permite auditar cada archivo descargado individualmente. |
| Generar metadata por fuente | Permite tener una vista consolidada de cada dataset. |
| Calcular checksum SHA-256 | Permite detectar cambios entre versiones descargadas. |
| Crear logs de ejecución | Facilita la revisión de errores y resultados del proceso. |

---

## 1.13. Alcance de la Capa Bronze

En esta etapa únicamente se realiza la ingesta y almacenamiento de archivos crudos.

No se realizan las siguientes actividades:

- Limpieza de columnas.
- Renombramiento de campos.
- Conversión de tipos de datos.
- Estandarización de nombres de municipalidades.
- Homologación de ubigeos.
- Eliminación de duplicados.
- Tratamiento de valores nulos.
- Unión entre fuentes.
- Cálculo de indicadores.
- Modelado dimensional.
- Construcción de dashboards.

Estas actividades corresponden a las capas **Silver** y **Gold**.

---

## 1.14. Próximos Pasos

Los siguientes pasos del proyecto serán:

1. Inspeccionar la estructura y calidad de los archivos descargados.
2. Identificar las columnas clave de cada fuente.
3. Definir las reglas de limpieza para la capa Silver.
4. Estandarizar campos como año, entidad, municipalidad y ubigeo.
5. Seleccionar los archivos relevantes de SISMEPRE para el análisis.
6. Extraer y preparar la información útil de RENAMU.
7. Construir tablas limpias en Silver.
8. Diseñar tablas analíticas en Gold para alimentar Power BI.

---

# 2. Estado Actual del Proyecto

Hasta el momento se ha avanzado en la construcción de la capa Bronze.

## Componentes implementados

| Componente | Estado |
|---|---|
| Estructura base del proyecto | Implementado |
| Carpeta `data/bronze/` | Implementado |
| Carpeta `data/silver/` | Creada, pendiente de implementación |
| Carpeta `data/gold/` | Creada, pendiente de implementación |
| Script de ingesta Bronze | Implementado |
| Descarga automatizada de SIAF | Implementado en script |
| Descarga automatizada de SISMEPRE | Implementado en script |
| Descarga automatizada de RENAMU | Implementado en script |
| Generación de metadata | Implementado |
| Generación de logs | Implementado |
| Cálculo de checksum SHA-256 | Implementado |
| Procesamiento Silver | Pendiente |
| Procesamiento Gold | Pendiente |
| Dashboard Power BI | Pendiente |

---

# 3. Comando Principal

Para ejecutar la ingesta Bronze:

```powershell
python .\scripts\01_ingesta_bronze.py
```

---

# 4. Consideraciones Importantes

La capa Bronze no debe confundirse con una capa de limpieza.

Una mala práctica sería descargar los archivos y modificarlos directamente dentro de Bronze. Por ejemplo:

```text
Descargar datos → limpiar columnas → eliminar nulos → guardar en Bronze
```

Ese flujo no corresponde a Bronze.

El flujo correcto es:

```text
Descargar datos → guardar archivo original → registrar metadata → conservar snapshot
```

La limpieza, estandarización y transformación deben realizarse recién en la capa Silver.

---

# 5. Flujo General de la Arquitectura

```text
Fuentes Oficiales
MEF/SIAF | MEF/SISMEPRE | INEI/RENAMU
        ↓
Ingesta Automatizada
scripts/01_ingesta_bronze.py
        ↓
Capa Bronze
Archivos originales + metadata + logs
        ↓
Capa Silver
Datos limpios, validados y estandarizados
        ↓
Capa Gold
Tablas analíticas e indicadores
        ↓
Power BI
Dashboard de análisis municipal
```