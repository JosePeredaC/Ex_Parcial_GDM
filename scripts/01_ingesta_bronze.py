"""
Script: 01_ingesta_bronze.py

Objetivo:
    Construir la capa Bronze del proyecto de análisis de ingresos municipales.

Este script está pensado para una estructura de proyecto como esta:

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

Fuentes consideradas:
    1. SIAF / MEF:
       Presupuesto y ejecución de ingresos, dividido por años.

    2. SISMEPRE / MEF:
       Seguimiento de la meta del impuesto predial, dividido en archivos
       de datos y archivos de diccionario.

    3. RENAMU / INEI:
       Registro Nacional de Municipalidades 2022, publicado como archivo ZIP.

Principio de diseño:
    La capa Bronze es inmutable.

    Eso significa que:
        - Cada ejecución genera un snapshot nuevo.
        - No se sobrescriben archivos anteriores.
        - No se limpian datos.
        - No se transforman columnas.
        - No se eliminan registros.
        - Los archivos se guardan tal como vienen de la fuente.

Resultado esperado:
    data/bronze/<fuente>/fecha_descarga=YYYY-MM-DD_HHMMSS/
"""

from pathlib import Path
from datetime import datetime
import hashlib
import json
import requests


# ============================================================
# 1. CONFIGURACIÓN GENERAL DEL PROYECTO
# ============================================================

"""
Como este script está dentro de la carpeta scripts/, usamos:

    Path(__file__).resolve().parents[1]

para obtener la carpeta raíz del proyecto.

Ejemplo:
    Si el script está en:

        C:/.../Ex_Parcial_Gestión_De_Datos_Masivos/scripts/01_ingesta_bronze.py

    entonces PROJECT_DIR será:

        C:/.../Ex_Parcial_Gestión_De_Datos_Masivos

Esto evita crear carpetas duplicadas por error.
"""

PROJECT_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_DIR / "data"
BRONZE_DIR = DATA_DIR / "bronze"
LOG_DIR = PROJECT_DIR / "logs"


# ============================================================
# 2. DEFINICIÓN DE FUENTES Y RECURSOS
# ============================================================

"""
La configuración está dividida por fuente.

Cada fuente contiene una lista de recursos.
Un recurso representa un archivo descargable.

Campos principales:
    - nombre_recurso:
        Nombre lógico del archivo dentro del proyecto.

    - url:
        Link directo de descarga.

    - archivo_salida:
        Nombre con el que se guardará el archivo en Bronze.

    - categoria:
        Carpeta interna donde se almacenará el recurso.
        Ejemplos:
            anio=2022
            datos
            diccionarios
            data_completa

    - tipo_recurso:
        Sirve para diferenciar data, diccionario, zip, data_mensual, etc.

    - formato:
        csv, zip, xlsx, etc.
"""

FUENTES = {
    "siaf_ingresos": {
        "fuente": "MEF/SIAF",
        "dataset": "Presupuesto y ejecución de ingreso",
        "pagina_dataset": "https://datosabiertos.mef.gob.pe/dataset/presupuesto-y-ejecucion-de-ingreso",
        "descripcion": "Datos de presupuesto y ejecución de ingresos publicados por el MEF.",
        "recursos": [
            {
                "nombre_recurso": "2019-Ingreso",
                "anio": 2019,
                "categoria": "anio=2019",
                "tipo_recurso": "data_anual",
                "formato": "csv",
                "url": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/2019-Ingreso.csv",
                "archivo_salida": "2019-Ingreso.csv"
            },
            {
                "nombre_recurso": "2020-Ingreso",
                "anio": 2020,
                "categoria": "anio=2020",
                "tipo_recurso": "data_anual",
                "formato": "csv",
                "url": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/2020-Ingreso.csv",
                "archivo_salida": "2020-Ingreso.csv"
            },
            {
                "nombre_recurso": "2021-Ingreso",
                "anio": 2021,
                "categoria": "anio=2021",
                "tipo_recurso": "data_anual",
                "formato": "csv",
                "url": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/2021-Ingreso.csv",
                "archivo_salida": "2021-Ingreso.csv"
            },
            {
                "nombre_recurso": "2022-Ingreso",
                "anio": 2022,
                "categoria": "anio=2022",
                "tipo_recurso": "data_anual",
                "formato": "csv",
                "url": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/2022-Ingreso.csv",
                "archivo_salida": "2022-Ingreso.csv"
            },
            {
                "nombre_recurso": "2023-Ingreso",
                "anio": 2023,
                "categoria": "anio=2023",
                "tipo_recurso": "data_anual",
                "formato": "csv",
                "url": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/2023-Ingreso.csv",
                "archivo_salida": "2023-Ingreso.csv"
            },
            {
                "nombre_recurso": "2024-Ingreso",
                "anio": 2024,
                "categoria": "anio=2024",
                "tipo_recurso": "data_anual",
                "formato": "csv",
                "url": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/2024-Ingreso.csv",
                "archivo_salida": "2024-Ingreso.csv"
            },
            {
                "nombre_recurso": "2025-Ingreso-Mensual",
                "anio": 2025,
                "categoria": "anio=2025",
                "tipo_recurso": "data_mensual",
                "formato": "csv",
                "url": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/2025-Ingreso-Mensual.csv",
                "archivo_salida": "2025-Ingreso-Mensual.csv"
            },
            {
                "nombre_recurso": "2026-Ingreso-Mensual",
                "anio": 2026,
                "categoria": "anio=2026",
                "tipo_recurso": "data_mensual",
                "formato": "csv",
                "url": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/2026-Ingreso-Mensual.csv",
                "archivo_salida": "2026-Ingreso-Mensual.csv"
            }
        ]
    },

    "sismepre_predial": {
        "fuente": "MEF/SISMEPRE",
        "dataset": "Seguimiento de la meta del impuesto predial",
        "pagina_dataset": "https://datosabiertos.mef.gob.pe/dataset/seguimiento-de-la-meta-del-impuesto-predial",
        "descripcion": "Archivos relacionados con el seguimiento de la meta del impuesto predial.",
        "recursos": [
            {
                "nombre_recurso": "rentas_preguntas",
                "categoria": "datos",
                "tipo_recurso": "data",
                "formato": "csv",
                "url": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/rentas_preguntas.csv",
                "archivo_salida": "rentas_preguntas.csv"
            },
            {
                "nombre_recurso": "rentas_estadistica",
                "categoria": "datos",
                "tipo_recurso": "data",
                "formato": "csv",
                "url": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/rentas_estadistica.csv",
                "archivo_salida": "rentas_estadistica.csv"
            },
            {
                "nombre_recurso": "rentas_formulario",
                "categoria": "datos",
                "tipo_recurso": "data",
                "formato": "csv",
                "url": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/rentas_formulario.csv",
                "archivo_salida": "rentas_formulario.csv"
            },
            {
                "nombre_recurso": "rentas_esat_estadistica_atm",
                "categoria": "datos",
                "tipo_recurso": "data",
                "formato": "csv",
                "url": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/rentas_esat_estadistica_atm.csv",
                "archivo_salida": "rentas_esat_estadistica_atm.csv"
            },
            {
                "nombre_recurso": "rentas_respuestas",
                "categoria": "datos",
                "tipo_recurso": "data",
                "formato": "csv",
                "url": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/rentas_respuestas.csv",
                "archivo_salida": "rentas_respuestas.csv"
            },
            {
                "nombre_recurso": "rentas_ano_aplicacion",
                "categoria": "datos",
                "tipo_recurso": "data",
                "formato": "csv",
                "url": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/rentas_ano_aplicacion.csv",
                "archivo_salida": "rentas_ano_aplicacion.csv"
            },
            {
                "nombre_recurso": "rentas_entidad_estado",
                "categoria": "datos",
                "tipo_recurso": "data",
                "formato": "csv",
                "url": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/rentas_entidad_estado.csv",
                "archivo_salida": "rentas_entidad_estado.csv"
            },

            {
                "nombre_recurso": "rentas_ano_aplicacion_diccionario",
                "categoria": "diccionarios",
                "tipo_recurso": "diccionario",
                "formato": "csv",
                "url": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/rentas_ano_aplicacion_diccionario.csv",
                "archivo_salida": "rentas_ano_aplicacion_diccionario.csv"
            },
            {
                "nombre_recurso": "rentas_preguntas_diccionario",
                "categoria": "diccionarios",
                "tipo_recurso": "diccionario",
                "formato": "csv",
                "url": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/rentas_preguntas_diccionario.csv",
                "archivo_salida": "rentas_preguntas_diccionario.csv"
            },
            {
                "nombre_recurso": "rentas_estadistica_diccionario",
                "categoria": "diccionarios",
                "tipo_recurso": "diccionario",
                "formato": "csv",
                "url": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/rentas_estadistica_diccionario.csv",
                "archivo_salida": "rentas_estadistica_diccionario.csv"
            },
            {
                "nombre_recurso": "rentas_entidad_estado_diccionario",
                "categoria": "diccionarios",
                "tipo_recurso": "diccionario",
                "formato": "csv",
                "url": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/rentas_entidad_estado_diccionario.csv",
                "archivo_salida": "rentas_entidad_estado_diccionario.csv"
            },
            {
                "nombre_recurso": "rentas_formulario_diccionario",
                "categoria": "diccionarios",
                "tipo_recurso": "diccionario",
                "formato": "csv",
                "url": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/rentas_formulario_diccionario.csv",
                "archivo_salida": "rentas_formulario_diccionario.csv"
            },
            {
                "nombre_recurso": "rentas_esat_estadistica_atm_diccionario",
                "categoria": "diccionarios",
                "tipo_recurso": "diccionario",
                "formato": "csv",
                "url": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/rentas_esat_estadistica_atm_diccionario.csv",
                "archivo_salida": "rentas_esat_estadistica_atm_diccionario.csv"
            },
            {
                "nombre_recurso": "rentas_respuestas_diccionario",
                "categoria": "diccionarios",
                "tipo_recurso": "diccionario",
                "formato": "csv",
                "url": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/rentas_respuestas_diccionario.csv",
                "archivo_salida": "rentas_respuestas_diccionario.csv"
            }
        ]
    },

    "renamu_2022": {
        "fuente": "INEI/RENAMU",
        "dataset": "Registro Nacional de Municipalidades RENAMU 2022",
        "pagina_dataset": "https://www.datosabiertos.gob.pe/dataset/registro-nacional-de-municipalidades-renamu-2022-instituto-nacional-de-estad%C3%ADstica-e",
        "descripcion": "Archivo ZIP de RENAMU 2022. Incluye data completa y diccionario de datos.",
        "recursos": [
            {
                "nombre_recurso": "renamu_2022_zip",
                "categoria": "data_completa",
                "tipo_recurso": "zip",
                "formato": "zip",
                "url": "https://www.inei.gob.pe/media/DATOS_ABIERTOS/RENAMU/DATA/2022.zip",
                "archivo_salida": "2022.zip"
            }
        ]
    }
}


# ============================================================
# 3. FUNCIONES AUXILIARES
# ============================================================

def crear_directorios_base():
    """
    Crea las carpetas base que necesita el proceso.

    En tu estructura ya existen data/bronze, data/silver y data/gold,
    pero usar mkdir con exist_ok=True no hace daño.

    No borra nada.
    No sobrescribe nada.
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def generar_id_snapshot():
    """
    Genera un identificador único para la ejecución actual.

    Ejemplo:
        fecha_descarga=2026-05-13_204500

    Este ID se usará como carpeta para guardar todos los archivos
    descargados en una misma corrida del script.
    """

    return datetime.now().strftime("fecha_descarga=%Y-%m-%d_%H%M%S")


def calcular_checksum_sha256(ruta_archivo):
    """
    Calcula el hash SHA-256 de un archivo.

    ¿Para qué sirve?
        - Para verificar integridad.
        - Para saber si una fuente cambió entre dos descargas.
        - Para comparar snapshots.
        - Para detectar archivos iguales aunque estén en carpetas distintas.

    En Bronze no abrimos ni transformamos el CSV.
    Solo calculamos el hash leyendo bytes.
    """

    sha256 = hashlib.sha256()

    with open(ruta_archivo, "rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            sha256.update(bloque)

    return sha256.hexdigest()


def descargar_archivo(url, ruta_salida):
    """
    Descarga un archivo desde una URL directa.

    Importante:
        Esta función NO interpreta el contenido.
        No lee el CSV con pandas.
        No cambia codificación.
        No cambia separadores.
        No limpia columnas.
        Solo descarga bytes y los guarda.

    Eso es lo correcto para una capa Bronze.
    """

    try:
        response = requests.get(url, stream=True, timeout=180)
        response.raise_for_status()

        tamanio_bytes = 0

        with open(ruta_salida, "wb") as archivo:
            for bloque in response.iter_content(chunk_size=1024 * 1024):
                if bloque:
                    archivo.write(bloque)
                    tamanio_bytes += len(bloque)

        return {
            "estado": "ok",
            "descargado": True,
            "mensaje": "Archivo descargado correctamente.",
            "codigo_http": response.status_code,
            "tamanio_bytes": tamanio_bytes
        }

    except requests.exceptions.RequestException as error:
        return {
            "estado": "error",
            "descargado": False,
            "mensaje": str(error),
            "codigo_http": None,
            "tamanio_bytes": None
        }


def guardar_json(data, ruta_salida):
    """
    Guarda información en formato JSON.

    Se usa para:
        - Metadata de cada recurso.
        - Metadata general de cada fuente.
        - Resumen completo de la ejecución.
    """

    with open(ruta_salida, "w", encoding="utf-8") as archivo:
        json.dump(data, archivo, indent=4, ensure_ascii=False)


def construir_ruta_recurso(carpeta_snapshot_fuente, recurso):
    """
    Construye la ruta final donde se guardará un recurso.

    Ejemplos:

    SIAF:
        data/bronze/siaf_ingresos/
        └── fecha_descarga=2026-05-13_204500/
            └── anio=2024/
                └── 2024-Ingreso.csv

    SISMEPRE:
        data/bronze/sismepre_predial/
        └── fecha_descarga=2026-05-13_204500/
            └── datos/
                └── rentas_estadistica.csv

    RENAMU:
        data/bronze/renamu_2022/
        └── fecha_descarga=2026-05-13_204500/
            └── data_completa/
                └── 2022.zip
    """

    carpeta_recurso = carpeta_snapshot_fuente / recurso["categoria"]
    carpeta_recurso.mkdir(parents=True, exist_ok=True)

    return carpeta_recurso / recurso["archivo_salida"]


# ============================================================
# 4. PROCESO PRINCIPAL DE INGESTA BRONZE
# ============================================================

def ejecutar_ingesta_bronze():
    """
    Ejecuta la ingesta Bronze para todas las fuentes configuradas.

    Flujo:
        1. Crear carpetas base.
        2. Crear un snapshot común para la ejecución.
        3. Recorrer cada fuente.
        4. Recorrer cada recurso de la fuente.
        5. Descargar el archivo original.
        6. Calcular checksum si la descarga fue exitosa.
        7. Guardar metadata por recurso.
        8. Guardar metadata por fuente.
        9. Guardar resumen general en logs.
    """

    crear_directorios_base()

    snapshot_id = generar_id_snapshot()
    fecha_inicio = datetime.now()

    resumen_ejecucion = {
        "proyecto": PROJECT_DIR.name,
        "ruta_proyecto": str(PROJECT_DIR),
        "capa": "bronze",
        "snapshot_id": snapshot_id,
        "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d %H:%M:%S"),
        "principio": "Snapshot inmutable. Los archivos se guardan sin transformación.",
        "fuentes": []
    }

    print("====================================================")
    print("INICIO DE INGESTA BRONZE")
    print(f"Proyecto: {PROJECT_DIR}")
    print(f"Snapshot: {snapshot_id}")
    print("====================================================")

    for nombre_fuente, config_fuente in FUENTES.items():

        print(f"\nFuente: {nombre_fuente}")

        carpeta_snapshot_fuente = BRONZE_DIR / nombre_fuente / snapshot_id
        carpeta_snapshot_fuente.mkdir(parents=True, exist_ok=True)

        metadata_fuente = {
            "nombre_fuente": nombre_fuente,
            "fuente": config_fuente["fuente"],
            "dataset": config_fuente["dataset"],
            "pagina_dataset": config_fuente["pagina_dataset"],
            "descripcion": config_fuente["descripcion"],
            "snapshot_id": snapshot_id,
            "fecha_descarga": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "capa": "bronze",
            "tratamiento": "Archivos originales guardados sin limpieza, sin transformación y sin eliminación de registros.",
            "recursos": []
        }

        resumen_fuente = {
            "nombre_fuente": nombre_fuente,
            "dataset": config_fuente["dataset"],
            "total_recursos": len(config_fuente["recursos"]),
            "recursos_ok": 0,
            "recursos_error": 0,
            "recursos": []
        }

        for recurso in config_fuente["recursos"]:

            print(f"  Descargando recurso: {recurso['nombre_recurso']}")

            ruta_archivo = construir_ruta_recurso(
                carpeta_snapshot_fuente=carpeta_snapshot_fuente,
                recurso=recurso
            )

            resultado_descarga = descargar_archivo(
                url=recurso["url"],
                ruta_salida=ruta_archivo
            )

            checksum = None

            if resultado_descarga["descargado"]:
                checksum = calcular_checksum_sha256(ruta_archivo)
                resumen_fuente["recursos_ok"] += 1
            else:
                resumen_fuente["recursos_error"] += 1

            metadata_recurso = {
                "nombre_recurso": recurso["nombre_recurso"],
                "categoria": recurso["categoria"],
                "tipo_recurso": recurso["tipo_recurso"],
                "formato": recurso["formato"],
                "anio": recurso.get("anio"),
                "url_descarga": recurso["url"],
                "archivo_bronze": str(ruta_archivo),
                "snapshot_id": snapshot_id,
                "fecha_descarga": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "capa": "bronze",
                "tratamiento": "Archivo original descargado y guardado sin modificaciones.",
                "descarga": resultado_descarga,
                "checksum_sha256": checksum
            }

            ruta_metadata_recurso = (
                ruta_archivo.parent / f"metadata_{recurso['nombre_recurso']}.json"
            )

            guardar_json(metadata_recurso, ruta_metadata_recurso)

            metadata_fuente["recursos"].append(metadata_recurso)

            resumen_fuente["recursos"].append({
                "nombre_recurso": recurso["nombre_recurso"],
                "estado": resultado_descarga["estado"],
                "descargado": resultado_descarga["descargado"],
                "archivo_bronze": str(ruta_archivo),
                "metadata": str(ruta_metadata_recurso),
                "checksum_sha256": checksum
            })

            print(f"    Estado: {resultado_descarga['estado']}")
            print(f"    Mensaje: {resultado_descarga['mensaje']}")

        ruta_metadata_fuente = carpeta_snapshot_fuente / "metadata_fuente.json"
        guardar_json(metadata_fuente, ruta_metadata_fuente)

        resumen_fuente["metadata_fuente"] = str(ruta_metadata_fuente)

        resumen_ejecucion["fuentes"].append(resumen_fuente)

    fecha_fin = datetime.now()

    resumen_ejecucion["fecha_fin"] = fecha_fin.strftime("%Y-%m-%d %H:%M:%S")
    resumen_ejecucion["duracion_segundos"] = round(
        (fecha_fin - fecha_inicio).total_seconds(),
        2
    )

    ruta_resumen = LOG_DIR / f"resumen_ingesta_bronze_{snapshot_id}.json"
    guardar_json(resumen_ejecucion, ruta_resumen)

    print("\n====================================================")
    print("FIN DE INGESTA BRONZE")
    print(f"Resumen guardado en: {ruta_resumen}")
    print("====================================================")


# ============================================================
# 5. PUNTO DE ENTRADA DEL SCRIPT
# ============================================================

if __name__ == "__main__":
    ejecutar_ingesta_bronze()
