import pandas as pd
from sqlalchemy import create_engine, text
import urllib

# =========================================================
# 1. CONFIGURACIÓN SQL SERVER (CONEXIÓN DE ALTO RENDIMIENTO)
# =========================================================
SERVER = 'localhost'
DATABASE = 'DMT_PRESUPUESTO'

CONNECTION_STRING = (
    f"mssql+pyodbc://@{SERVER}/{DATABASE}"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes"
)

# fast_executemany=True es vital para subir millones de filas en segundos
engine = create_engine(CONNECTION_STRING, fast_executemany=True)

# =========================================================
# 2. CARGAR Y LIMPIAR DATASET GOLD
# =========================================================
print("=" * 60)
print("      1. CARGA Y LIMPIEZA DEL DATASET GOLD")
print("=" * 60)

# Reemplaza por 'gold_municipalidades.parquet' o el nombre exacto de tu archivo
df = pd.read_parquet('gold_municipalidades.parquet')

print(f"✅ Registros totales detectados : {len(df):,}")

# Remover columnas SISMEPRE nulas de la capa Gold para liberar memoria
columnas_sismepre = ['SISMEPRE_DECIMAL_PROM', 'SISMEPRE_ENTERO_PROM', 'SISMEPRE_ESTADO_MODA', 'SISMEPRE_RESPUESTAS']
df = df.drop(columns=[c for c in columnas_sismepre if c in df.columns], errors='ignore')

# Tratamiento estricto del 0.3% de nulos geográficos y limpieza de textos
print("Normalizando textos y mitigando registros nulos...")
columnas_texto = [
    'UBIGEO', 'Departamento', 'Provincia', 'Distrito',
    'SEC_EJEC', 'EJECUTORA_NOMBRE', 'NIVEL_GOBIERNO', 'NIVEL_GOBIERNO_NOMBRE',
    'DEPARTAMENTO_EJECUTORA_NOMBRE', 'PROVINCIA_EJECUTORA_NOMBRE', 'DISTRITO_EJECUTORA_NOMBRE',
    'FUENTE_FINANCIAMIENTO', 'FUENTE_FINANCIAMIENTO_NOMBRE',
    'RUBRO', 'RUBRO_NOMBRE', 'GENERICA', 'GENERICA_NOMBRE', 'SUBGENERICA', 'SUBGENERICA_NOMBRE'
]

for col in columnas_texto:
    if col in df.columns:
        df[col] = df[col].fillna('No Especificado').astype(str).str.strip()

# Asegurar limpieza y tipos nativos en métricas financieras
df['EJECUTORA'] = pd.to_numeric(df['EJECUTORA'], errors='coerce').fillna(0).astype(int)
df['Tipomuni'] = pd.to_numeric(df['Tipomuni'], errors='coerce').fillna(0.0).astype(float)
df['MONTO_PIA'] = pd.to_numeric(df['MONTO_PIA'], errors='coerce').fillna(0.0).astype(float)
df['MONTO_PIM'] = pd.to_numeric(df['MONTO_PIM'], errors='coerce').fillna(0.0).astype(float)
df['MONTO_RECAUDADO'] = pd.to_numeric(df['MONTO_RECAUDADO'], errors='coerce').fillna(0.0).astype(float)
df['TASA_EJECUCION'] = pd.to_numeric(df['TASA_EJECUCION'], errors='coerce').fillna(0.0).astype(float)

# Crear la columna de fecha obligatoria para acoplar la dimensión temporal
df['fecha_inicio_mes'] = pd.to_datetime(
    df['ANO_DOC'].astype(str) + '-' + df['MES_DOC'].astype(str) + '-01',
    errors='coerce'
)

# =========================================================
# 3. TRUNCAR TABLAS (REINICIO LIMPIO DEL DATA MART)
# =========================================================
print("\n" + "=" * 60)
print("      2. REINICIANDO DESTINOS EN SQL SERVER")
print("=" * 60)
with engine.begin() as conn:
    conn.execute(text("DELETE FROM dmt.FACT_PRESUPUESTO"))
    conn.execute(text("DELETE FROM dmt.DIM_FINANCIERA"))
    conn.execute(text("DELETE FROM dmt.DIM_ENTIDAD"))
    conn.execute(text("DELETE FROM dmt.DIM_UBICACION"))
    conn.execute(text("DELETE FROM dmt.DIM_TIEMPO"))
print("✅ Base de datos lista para recibir la carga.")

# =========================================================
# 4. POBLAR DIMENSIONES (EXTRACCIÓN DE VALORES ÚNICOS)
# =========================================================
print("\n" + "=" * 60)
print("      3. POBLANDO TABLAS DE DIMENSIONES")
print("=" * 60)

# --- DIM_TIEMPO ---
dim_tiempo = df[['fecha_inicio_mes', 'ANO_DOC', 'MES_DOC']].drop_duplicates().dropna()
dim_tiempo['nombre_mes'] = dim_tiempo['fecha_inicio_mes'].dt.month_name(locale='Spanish')
dim_tiempo['nombre_corto_mes'] = dim_tiempo['nombre_mes'].str[:3]
dim_tiempo['trimestre'] = 'T' + (((dim_tiempo['MES_DOC'] - 1) // 3) + 1).astype(str)
dim_tiempo['semestre'] = 'S' + (((dim_tiempo['MES_DOC'] - 1) // 6) + 1).astype(str)
dim_tiempo['bimestre'] = 'B' + (((dim_tiempo['MES_DOC'] - 1) // 2) + 1).astype(str)

dim_tiempo.columns = ['fecha_inicio_mes', 'anio', 'mes', 'nombre_mes', 'nombre_corto_mes', 'trimestre', 'semestre', 'bimestre']
dim_tiempo.to_sql('DIM_TIEMPO', engine, schema='dmt', if_exists='append', index=False)
print(f"✅ dmt.DIM_TIEMPO poblada      : {len(dim_tiempo):,}")

# --- DIM_UBICACION ---
dim_ubicacion = df[['UBIGEO', 'Departamento', 'Provincia', 'Distrito']].copy()
# Garantizamos la unicidad estricta basándonos únicamente en la clave primaria lógica (UBIGEO)
dim_ubicacion = dim_ubicacion[dim_ubicacion['UBIGEO'] != ''].drop_duplicates(subset=['UBIGEO'])
dim_ubicacion.columns = ['UBIGEO', 'departamento', 'provincia', 'distrito']
dim_ubicacion.to_sql('DIM_UBICACION', engine, schema='dmt', if_exists='append', index=False)
print(f"✅ dmt.DIM_UBICACION poblada   : {len(dim_ubicacion):,}")

# --- DIM_ENTIDAD ---
dim_entidad = df[[
    'SEC_EJEC', 'EJECUTORA', 'EJECUTORA_NOMBRE', 'NIVEL_GOBIERNO', 'NIVEL_GOBIERNO_NOMBRE',
    'DEPARTAMENTO_EJECUTORA_NOMBRE', 'PROVINCIA_EJECUTORA_NOMBRE', 'DISTRITO_EJECUTORA_NOMBRE', 'Tipomuni'
]].copy()
dim_entidad = dim_entidad[dim_entidad['SEC_EJEC'] != ''].drop_duplicates(subset=['SEC_EJEC'])
dim_entidad.to_sql('DIM_ENTIDAD', engine, schema='dmt', if_exists='append', index=False)
print(f"✅ dmt.DIM_ENTIDAD poblada     : {len(dim_entidad):,}")

# --- DIM_FINANCIERA ---
dim_financiera = df[[
    'FUENTE_FINANCIAMIENTO', 'FUENTE_FINANCIAMIENTO_NOMBRE', 'RUBRO', 'RUBRO_NOMBRE',
    'GENERICA', 'GENERICA_NOMBRE', 'SUBGENERICA', 'SUBGENERICA_NOMBRE'
]].drop_duplicates(subset=['FUENTE_FINANCIAMIENTO', 'RUBRO', 'GENERICA', 'SUBGENERICA'])
dim_financiera.to_sql('DIM_FINANCIERA', engine, schema='dmt', if_exists='append', index=False)
print(f"✅ dmt.DIM_FINANCIERA poblada  : {len(dim_financiera):,}")

# =========================================================
# 5. FASE DE STAGING (SUBIDA MASIVA DE DATOS CRUDOS)
# =========================================================
print("\n" + "=" * 60)
print("      4. EJECUTANDO FASE DE STAGING EN SQL SERVER")
print("=" * 60)
print("🚀 Subiendo los 2.85 millones de registros crudos a dmt.STG_PRESUPUESTO...")

df_staging = df[[
    'fecha_inicio_mes', 'UBIGEO', 'SEC_EJEC', 
    'FUENTE_FINANCIAMIENTO', 'RUBRO', 'GENERICA', 'SUBGENERICA',
    'MONTO_PIA', 'MONTO_PIM', 'MONTO_RECAUDADO', 'TASA_EJECUCION'
]]

# Se sube en bloques controlados de 70,000 filas para optimizar el búfer de red
df_staging.to_sql(
    'STG_PRESUPUESTO', 
    con=engine, 
    schema='dmt', 
    if_exists='replace', 
    index=False, 
    chunksize=70000
)
print("✅ Carga cruda completada en la tabla Staging.")

# =========================================================
# 6. CONSOLIDACIÓN FINAL EN LA TABLA DE HECHOS MEDIANTE SQL
# =========================================================
print("\n" + "=" * 60)
print("      5. RESOLVIENDO LLAVES DENTRO DE SQL SERVER (MÉTODO OLAP)")
print("=" * 60)
print("⚡ Cruzando llaves y aplicando control de nulos automáticos...")

query_fact = """
INSERT INTO dmt.FACT_PRESUPUESTO (
    id_tiempo, id_ubicacion, id_entidad, id_financiera,
    MONTO_PIA, MONTO_PIM, MONTO_RECAUDADO, TASA_EJECUCION
)
SELECT 
    ISNULL(t.id_tiempo, -1) AS id_tiempo,
    ISNULL(u.id_ubicacion, -1) AS id_ubicacion,
    ISNULL(e.id_entidad, -1) AS id_entidad,
    ISNULL(f.id_financiera, -1) AS id_financiera,
    s.MONTO_PIA,
    s.MONTO_PIM,
    s.MONTO_RECAUDADO,
    s.TASA_EJECUCION
FROM dmt.STG_PRESUPUESTO s
LEFT JOIN dmt.DIM_TIEMPO t ON s.fecha_inicio_mes = t.fecha_inicio_mes
LEFT JOIN dmt.DIM_UBICACION u ON s.UBIGEO = u.UBIGEO
LEFT JOIN dmt.DIM_ENTIDAD e ON s.SEC_EJEC = e.SEC_EJEC
LEFT JOIN dmt.DIM_FINANCIERA f ON s.FUENTE_FINANCIAMIENTO = f.FUENTE_FINANCIAMIENTO
                               AND s.RUBRO = f.RUBRO
                               AND s.GENERICA = f.GENERICA
                               AND s.SUBGENERICA = f.SUBGENERICA;
"""

with engine.begin() as conn:
    # 1. SQL Server ejecuta el cruce masivo de indexación
    conn.execute(text(query_fact))
    print("Cruce exitoso. Destruyendo tabla intermedia dmt.STG_PRESUPUESTO...")
    # 2. Se destruye la tabla staging para dejar el Data Mart impecable
    conn.execute(text("DROP TABLE dmt.STG_PRESUPUESTO;"))

print("\n" + "=" * 60)
print("      ¡ETL DATA MART COMPLETADO EXITOSAMENTE!")
print("=" * 60)
