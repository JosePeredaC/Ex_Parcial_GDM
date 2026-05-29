# Capa Bronze (Raw Data)

Esta carpeta contiene los datos crudos e inalterados del proyecto, tal como se extraen de las fuentes de origen. El objetivo de esta capa es mantener un histórico de la ingesta sin aplicar transformaciones ni limpiezas.

##  ¿Cómo se generan estos datos?

Los archivos de esta carpeta **no deben modificarse ni añadirse manualmente**. Se generan automáticamente mediante la ejecución del pipeline de ingesta.

Para actualizar o descargar los datos de esta capa, se debe de  ejecutar el script correspondiente desde la raíz del proyecto:

```bash
python scripts/01_ingesta_bronze.py