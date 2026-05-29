-- =========================================================
-- DATA MART PRESUPUESTAL
-- Arquitectura de Almacenamiento - SQL Server
-- Modelo Estrella Optimizado para OLAP (Metodología Kimball)
-- =========================================================

CREATE DATABASE DMT_PRESUPUESTO;
GO

USE DMT_PRESUPUESTO;
GO

-- =========================================================
-- CREACIÓN DEL ESQUEMA
-- =========================================================

CREATE SCHEMA dmt;
GO

-- =========================================================
-- DIMENSIÓN TIEMPO
-- Dimensión calendario mensual enriquecida
-- =========================================================

CREATE TABLE dmt.DIM_TIEMPO (
    id_tiempo INT IDENTITY(1,1) PRIMARY KEY,
    fecha_inicio_mes DATE NOT NULL,
    anio INT NOT NULL,
    mes INT NOT NULL,
    nombre_mes VARCHAR(20) NOT NULL,
    nombre_corto_mes VARCHAR(5) NOT NULL,
    trimestre VARCHAR(5) NOT NULL,
    semestre VARCHAR(5) NOT NULL,
    bimestre VARCHAR(5) NOT NULL
);
GO

-- =========================================================
-- DIMENSIÓN UBICACIÓN
-- Información geográfica reutilizable (1,895 UBIGEOs)
-- =========================================================

CREATE TABLE dmt.DIM_UBICACION (
    id_ubicacion INT IDENTITY(1,1) PRIMARY KEY,
    UBIGEO VARCHAR(10) NOT NULL,
    departamento VARCHAR(100),
    provincia VARCHAR(100),
    distrito VARCHAR(100)
);
GO

-- =========================================================
-- DIMENSIÓN ENTIDAD
-- Consolidación de ejecutora + nivel de gobierno + tipomuni
-- =========================================================

CREATE TABLE dmt.DIM_ENTIDAD (
    id_entidad INT IDENTITY(1,1) PRIMARY KEY,
    SEC_EJEC VARCHAR(20) NOT NULL,
    EJECUTORA INT,
    EJECUTORA_NOMBRE VARCHAR(255),
    NIVEL_GOBIERNO VARCHAR(50),
    NIVEL_GOBIERNO_NOMBRE VARCHAR(150),
    DEPARTAMENTO_EJECUTORA_NOMBRE VARCHAR(150),
    PROVINCIA_EJECUTORA_NOMBRE VARCHAR(150),
    DISTRITO_EJECUTORA_NOMBRE VARCHAR(150),
    Tipomuni FLOAT
);
GO

-- =========================================================
-- DIMENSIÓN FINANCIERA
-- Consolidación jerárquica de clasificadores económicos SIAF
-- =========================================================

CREATE TABLE dmt.DIM_FINANCIERA (
    id_financiera INT IDENTITY(1,1) PRIMARY KEY,
    FUENTE_FINANCIAMIENTO VARCHAR(50),
    FUENTE_FINANCIAMIENTO_NOMBRE VARCHAR(255),
    RUBRO VARCHAR(50),
    RUBRO_NOMBRE VARCHAR(255),
    GENERICA VARCHAR(50),
    GENERICA_NOMBRE VARCHAR(255),
    SUBGENERICA VARCHAR(50),
    SUBGENERICA_NOMBRE VARCHAR(255)
);
GO

-- =========================================================
-- INSERCIÓN DE REGISTROS POR DEFECTO (-1) PARA INTEGRIDAD DEL ETL
-- Evita caídas si el pipeline de Python encuentra un dato huérfano.
-- =========================================================

SET IDENTITY_INSERT dmt.DIM_TIEMPO ON;
INSERT INTO dmt.DIM_TIEMPO (id_tiempo, fecha_inicio_mes, anio, mes, nombre_mes, nombre_corto_mes, trimestre, semestre, bimestre) 
VALUES (-1, '1900-01-01', 0, 0, 'No Especificado', 'N/E', 'T0', 'S0', 'B0');
SET IDENTITY_INSERT dmt.DIM_TIEMPO OFF;

SET IDENTITY_INSERT dmt.DIM_UBICACION ON;
INSERT INTO dmt.DIM_UBICACION (id_ubicacion, UBIGEO, departamento, provincia, distrito) 
VALUES (-1, '000000', 'No Especificado', 'No Especificado', 'No Especificado');
SET IDENTITY_INSERT dmt.DIM_UBICACION OFF;

SET IDENTITY_INSERT dmt.DIM_ENTIDAD ON;
INSERT INTO dmt.DIM_ENTIDAD (id_entidad, SEC_EJEC, EJECUTORA_NOMBRE, NIVEL_GOBIERNO_NOMBRE) 
VALUES (-1, '0000', 'No Especificado', 'No Especificado');
SET IDENTITY_INSERT dmt.DIM_ENTIDAD OFF;

SET IDENTITY_INSERT dmt.DIM_FINANCIERA ON;
INSERT INTO dmt.DIM_FINANCIERA (id_financiera, FUENTE_FINANCIAMIENTO_NOMBRE, RUBRO_NOMBRE, GENERICA_NOMBRE, SUBGENERICA_NOMBRE) 
VALUES (-1, 'No Especificado', 'No Especificado', 'No Especificado', 'No Especificado');
SET IDENTITY_INSERT dmt.DIM_FINANCIERA OFF;
GO

-- =========================================================
-- TABLA DE HECHOS CENTRAL
-- =========================================================

CREATE TABLE dmt.FACT_PRESUPUESTO (

    id_fact_presupuesto BIGINT IDENTITY(1,1),

    id_tiempo INT NOT NULL,
    id_ubicacion INT NOT NULL,
    id_entidad INT NOT NULL,
    id_financiera INT NOT NULL,

    MONTO_PIA DECIMAL(38,2),
    MONTO_PIM DECIMAL(38,2),
    MONTO_RECAUDADO DECIMAL(38,2),
    TASA_EJECUCION FLOAT,

    CONSTRAINT PK_FACT_PRESUPUESTO
    PRIMARY KEY NONCLUSTERED (id_fact_presupuesto),

    CONSTRAINT FK_FACT_TIEMPO
        FOREIGN KEY (id_tiempo)
        REFERENCES dmt.DIM_TIEMPO(id_tiempo),

    CONSTRAINT FK_FACT_UBICACION
        FOREIGN KEY (id_ubicacion)
        REFERENCES dmt.DIM_UBICACION(id_ubicacion),

    CONSTRAINT FK_FACT_ENTIDAD
        FOREIGN KEY (id_entidad)
        REFERENCES dmt.DIM_ENTIDAD(id_entidad),

    CONSTRAINT FK_FACT_FINANCIERA
        FOREIGN KEY (id_financiera)
        REFERENCES dmt.DIM_FINANCIERA(id_financiera)
);
GO

-- =========================================================
-- INDEXACIÓN ANALÍTICA DE ALTO RENDIMIENTO (OLAP)
-- =========================================================

-- Reemplazamos los índices estándar tradicionales por un Columnstore Clúster.
-- SQL Server indexará y comprimirá las 2.85 millones de filas por columnas nativamente.
CREATE CLUSTERED COLUMNSTORE INDEX IX_FACT_PRESUPUESTO_COLUMNSTORE
ON dmt.FACT_PRESUPUESTO;
GO

-- =========================================================
-- RESTRICCIONES DE CALIDAD DE DATOS (REGLAS DE NEGOCIO)
-- =========================================================

ALTER TABLE dmt.DIM_TIEMPO
ADD CONSTRAINT CHK_MES
CHECK (mes = 0 OR (mes BETWEEN 1 AND 12));
GO

ALTER TABLE dmt.FACT_PRESUPUESTO
ADD CONSTRAINT CHK_MONTO_PIA
CHECK (MONTO_PIA >= 0);
GO

ALTER TABLE dmt.FACT_PRESUPUESTO
ADD CONSTRAINT CHK_MONTO_PIM
CHECK (MONTO_PIM >= 0);
GO

ALTER TABLE dmt.FACT_PRESUPUESTO
ADD CONSTRAINT CHK_MONTO_RECAUDADO
CHECK (MONTO_RECAUDADO >= 0);
GO

-- =========================================================
-- DOCUMENTACIÓN DE LA EXCLUSIÓN (SUSTENTACIÓN)
-- =========================================================
/*
COLUMNAS EXCLUIDAS DEL DATASET GOLD (100% NULOS):
- SISMEPRE_DECIMAL_PROM
- SISMEPRE_ENTERO_PROM
- SISMEPRE_ESTADO_MODA
- SISMEPRE_RESPUESTAS

La exclusión permite maximizar la tasa de compresión del índice 
Columnstore y eliminar el almacenamiento estéril en disco.
*/
-- =========================================================
-- FIN DEL SCRIPT FISICO
-- =========================================================