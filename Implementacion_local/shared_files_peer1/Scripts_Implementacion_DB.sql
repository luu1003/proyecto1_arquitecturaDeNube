-- =====================================================================================================================
-- SISTEMA DE GESTIÓN DE CONTRATACIÓN PÚBLICA - SECOP
-- =====================================================================================================================
--
-- PROYECTO:    Base de Datos para Análisis de Contratación Pública SECOP
-- AUTOR:       Juan Jose Tamayo Ospina
-- ID:          000193632
-- UNIVERSIDAD: Universidad Pontificia Bolivariana
-- FECHA:       Agosto 2025
-- VERSION:     1.0
--
-- DESCRIPCIÓN:
-- Este script implementa una base de datos relacional en PostgreSQL para la gestión y análisis 
-- de información del sistema de contratación pública SECOP. El modelo permite almacenar y 
-- analizar datos de procesos de contratación, entidades públicas, modalidades y estadísticas.
--
-- FUENTE DE DATOS:
-- Sistema Electrónico de Contratación Pública - SECOP
-- Período: [Especificar período de datos]
-- URL: https://www.datos.gov.co/
--
-- CARACTERÍSTICAS DEL MODELO:
-- - Normalización en Tercera Forma Normal (3FN)
-- - Integridad referencial garantizada
-- - Optimización para consultas analíticas
-- - Separación de datos originales y normalizados en esquemas diferentes
-- - Índices para optimización de rendimiento
--
-- =====================================================================================================================

-- =====================================================================================================================
-- SECCIÓN 0: CONFIGURACIÓN INICIAL - USUARIO, ESQUEMA Y PRIVILEGIOS
-- =====================================================================================================================
--
-- Esta sección configura el entorno de base de datos necesario para el proyecto, incluyendo:
-- - Creación de usuario dedicado para la aplicación
-- - Creación de esquemas específicos para organización de objetos
-- - Asignación de privilegios mínimos necesarios para seguridad
-- - Configuración de parámetros de conexión y sesión
--
-- NOTA: Los comandos de esta sección requieren privilegios de superusuario (postgres)
-- =====================================================================================================================

CREATE DATABASE secop_db;

\c secop_db;

CREATE USER secop_usr WITH ENCRYPTED PASSWORD '********';

CREATE SCHEMA inicial;
CREATE SCHEMA corregido;

GRANT CONNECT ON DATABASE secop_db TO secop_usr;

GRANT TEMPORARY ON DATABASE secop_db TO secop_usr;

GRANT CREATE ON SCHEMA corregido TO secop_usr;
GRANT CREATE ON SCHEMA inicial TO secop_usr;

GRANT USAGE ON SCHEMA corregido TO secop_usr;
GRANT USAGE ON SCHEMA inicial TO secop_usr;

GRANT SELECT, INSERT, UPDATE, DELETE, ON ALL TABLES IN SCHEMA corregido TO secop_usr;
GRANT SELECT, INSERT, UPDATE, DELETE, ON ALL TABLES IN SCHEMA inicial TO secop_usr;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA corregido TO secop_usr;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA inicial TO secop_usr;

GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA corregido TO secop_usr;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA inicial TO secop_usr;

GRANT EXECUTE ON ALL PROCEDURES IN SCHEMA corregido TO secop_usr;
GRANT EXECUTE ON ALL PROCEDURES IN SCHEMA inicial TO secop_usr;

ALTER DEFAULT PRIVILEGES IN SCHEMA corregido GRANT SELECT, INSERT, UPDATE, DELETE, TRIGGER ON TABLES TO secop_usr;
ALTER DEFAULT PRIVILEGES IN SCHEMA inicial GRANT SELECT, INSERT, UPDATE, DELETE, TRIGGER ON TABLES TO secop_usr;

ALTER DEFAULT PRIVILEGES IN SCHEMA corregido GRANT SELECT ON TABLES TO secop_usr;
ALTER DEFAULT PRIVILEGES IN SCHEMA inicial GRANT SELECT ON TABLES TO secop_usr;

ALTER DEFAULT PRIVILEGES IN SCHEMA corregido GRANT USAGE, SELECT ON SEQUENCES TO secop_usr;
ALTER DEFAULT PRIVILEGES IN SCHEMA inicial GRANT USAGE, SELECT ON SEQUENCES TO secop_usr;

-- =====================================================================================================================
-- SECCIÓN 1: TABLA TEMPORAL PARA IMPORTACIÓN DE DATOS
-- =====================================================================================================================
--
-- Esta tabla temporal replica la estructura original de los datos CSV de SECOP para facilitar 
-- la importación inicial sin transformaciones. Posteriormente se normaliza en el esquema corregido.
-- =====================================================================================================================

-- ---------------------------------------------------------------------------------------------------------------------
-- TABLA TEMPORAL: inicial.tabla_sin_corregir
-- PROPÓSITO: Recepción inicial de datos CSV sin transformaciones
-- CARACTERÍSTICAS: Estructura que replica exactamente el formato del archivo CSV original
-- ESQUEMA: inicial (datos sin procesar)
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE inicial.tabla_sin_corregir (
    nit_entidad            VARCHAR(50),
    departamento_entidad   VARCHAR(100),
    ciudad_entidad         VARCHAR(100),
    orden_entidad          VARCHAR(50),
    entidad_centralizada   VARCHAR(50),
    id_proceso             VARCHAR(100),
    fecha_proceso          VARCHAR(50),
    precio_base            VARCHAR(100),
    modalidad_contratacion VARCHAR(200),
    duracion               VARCHAR(50),
    unidad_duracion        VARCHAR(50),
    tipo_contrato          VARCHAR(200)
);

COMMENT ON TABLE inicial.tabla_sin_corregir IS 'Tabla temporal para importación de datos originales de SECOP sin procesar';
COMMENT ON COLUMN inicial.tabla_sin_corregir.nit_entidad IS 'Número de Identificación Tributaria de la entidad contratante';
COMMENT ON COLUMN inicial.tabla_sin_corregir.departamento_entidad IS 'Departamento donde se ubica la entidad contratante';
COMMENT ON COLUMN inicial.tabla_sin_corregir.ciudad_entidad IS 'Ciudad donde se ubica la entidad contratante';
COMMENT ON COLUMN inicial.tabla_sin_corregir.orden_entidad IS 'Orden administrativo de la entidad (nacional, territorial, etc.)';
COMMENT ON COLUMN inicial.tabla_sin_corregir.entidad_centralizada IS 'Tipo de entidad: centralizada o descentralizada';
COMMENT ON COLUMN inicial.tabla_sin_corregir.id_proceso IS 'Identificador único del proceso de contratación';
COMMENT ON COLUMN inicial.tabla_sin_corregir.fecha_proceso IS 'Fecha del proceso de contratación en formato texto';
COMMENT ON COLUMN inicial.tabla_sin_corregir.precio_base IS 'Valor base del contrato en formato texto';
COMMENT ON COLUMN inicial.tabla_sin_corregir.modalidad_contratacion IS 'Modalidad de contratación utilizada';
COMMENT ON COLUMN inicial.tabla_sin_corregir.duracion IS 'Duración del contrato en formato texto';
COMMENT ON COLUMN inicial.tabla_sin_corregir.unidad_duracion IS 'Unidad de medida de la duración (días, meses, años)';
COMMENT ON COLUMN inicial.tabla_sin_corregir.tipo_contrato IS 'Clasificación del tipo de contrato';


-- =====================================================================================================================
-- SECCIÓN 2: CREACIÓN DE TABLAS NORMALIZADAS
-- =====================================================================================================================
--
-- Las siguientes tablas conforman el modelo de datos normalizado en el esquema 'corregido', 
-- diseñado para eliminar redundancias y garantizar la integridad de la información. Cada tabla 
-- representa una entidad específica del dominio de contratación pública.
-- =====================================================================================================================

-- ---------------------------------------------------------------------------------------------------------------------
-- TABLA: corregido.Ciudades
-- PROPÓSITO: Catálogo de ciudades donde se ubican las entidades contratantes
-- RELACIONES: Relacionada con Entidades
-- CARACTERÍSTICAS: Catálogo maestro con restricción de unicidad en descripción
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE corregido.Ciudades (
                                    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                                    descripcion VARCHAR(50) NOT NULL,
                                    CONSTRAINT uq_ciudad UNIQUE (descripcion)

);

COMMENT ON TABLE corregido.Ciudades IS 'Catálogo de ciudades donde se ubican las entidades contratantes del sistema SECOP';
COMMENT ON COLUMN corregido.Ciudades.id IS 'Identificador único de la ciudad';
COMMENT ON COLUMN corregido.Ciudades.descripcion IS 'Nombre oficial de la ciudad o municipio';

CREATE TABLE corregido.Ordenes (
                                   id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                                   descripcion VARCHAR(50) NOT NULL UNIQUE
);

COMMENT ON TABLE corregido.Ordenes IS 'Catálogo de órdenes administrativos de las entidades públicas';
COMMENT ON COLUMN corregido.Ordenes.id IS 'Identificador único del orden administrativo';
COMMENT ON COLUMN corregido.Ordenes.descripcion IS 'Descripción del orden administrativo de la entidad';

CREATE TABLE corregido.Modalidades_contratos (
                                                 id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                                                 descripcion VARCHAR(100) NOT NULL UNIQUE
);

COMMENT ON TABLE corregido.Modalidades_contratos IS 'Catálogo de modalidades de contratación pública según normativa vigente';
COMMENT ON COLUMN corregido.Modalidades_contratos.id IS 'Identificador único de la modalidad de contratación';
COMMENT ON COLUMN corregido.Modalidades_contratos.descripcion IS 'Descripción de la modalidad de contratación';


CREATE TABLE corregido.Tipos_contratos (
                                           id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                                           descripcion VARCHAR(50) NOT NULL UNIQUE
);

COMMENT ON TABLE corregido.Tipos_contratos IS 'Catálogo de tipos de contratos según su objeto y naturaleza jurídica';
COMMENT ON COLUMN corregido.Tipos_contratos.id IS 'Identificador único del tipo de contrato';
COMMENT ON COLUMN corregido.Tipos_contratos.descripcion IS 'Descripción del tipo de contrato según su clasificación';

CREATE TABLE corregido.Entidades (
                                     nit_entidad BIGINT PRIMARY KEY,  -- mejor BIGINT para soportar NITs largos
                                     ciudad_id INT NOT NULL,
                                     orden_id INT NOT NULL,
                                     centralizada CHAR(1) CHECK (centralizada IN ('S','N')),
                                     CONSTRAINT fk_entidad_ciudad FOREIGN KEY (ciudad_id)
                                         REFERENCES corregido.Ciudades(id),
                                     CONSTRAINT fk_entidad_orden FOREIGN KEY (orden_id)
                                         REFERENCES corregido.Ordenes(id)
);


COMMENT ON TABLE corregido.Entidades IS 'Registro de entidades públicas contratantes en el sistema SECOP';
COMMENT ON COLUMN corregido.Entidades.nit_entidad IS 'Número de Identificación Tributaria de la entidad (clave primaria)';
COMMENT ON COLUMN corregido.Entidades.ciudad_id IS 'Referencia a la ciudad donde se ubica la entidad';
COMMENT ON COLUMN corregido.Entidades.orden_id IS 'Referencia al orden administrativo de la entidad';
COMMENT ON COLUMN corregido.Entidades.centralizada IS 'Indica si la entidad es centralizada (S) o descentralizada (N)';


CREATE TABLE corregido.Procesos (
                                    id VARCHAR(50) PRIMARY KEY,
                                    fecha DATE NOT NULL,
                                    precio_base NUMERIC(15,2),
                                    id_modalidad INT NOT NULL,
                                    duracion INT NOT NULL, -- en días
                                    id_tipo_contrato INT NOT NULL,
                                    nit_entidad BIGINT NOT NULL,
                                    CONSTRAINT fk_proceso_modalidad FOREIGN KEY (id_modalidad)
                                        REFERENCES corregido.Modalidades_contratos(id),
                                    CONSTRAINT fk_proceso_tipo FOREIGN KEY (id_tipo_contrato)
                                        REFERENCES corregido.Tipos_contratos(id),
                                    CONSTRAINT fk_proceso_entidad FOREIGN KEY (nit_entidad)
                                        REFERENCES corregido.Entidades(nit_entidad)
);

COMMENT ON TABLE corregido.Procesos IS 'Registro principal de procesos de contratación pública del sistema SECOP';
COMMENT ON COLUMN corregido.Procesos.id IS 'Identificador único del proceso de contratación';
COMMENT ON COLUMN corregido.Procesos.fecha IS 'Fecha del proceso de contratación';
COMMENT ON COLUMN corregido.Procesos.precio_base IS 'Valor base del contrato en pesos colombianos';
COMMENT ON COLUMN corregido.Procesos.id_modalidad IS 'Referencia a la modalidad de contratación utilizada';
COMMENT ON COLUMN corregido.Procesos.duracion IS 'Duración del contrato expresada en días';
COMMENT ON COLUMN corregido.Procesos.id_tipo_contrato IS 'Referencia al tipo de contrato según su clasificación';
COMMENT ON COLUMN corregido.Procesos.nit_entidad IS 'Referencia a la entidad contratante';

-- =====================================================================================================================
-- SECCIÓN 3: CARGA DE DATOS MAESTROS
-- =====================================================================================================================
--
-- Esta sección pobla las tablas de catálogos extrayendo valores únicos de los datos temporales. 
-- Utiliza la cláusula WHERE para filtrar valores nulos y garantizar la calidad de los datos.
-- =====================================================================================================================

-- ---------------------------------------------------------------------------------------------------------------------
-- CARGA: Ciudades únicas
-- PROPÓSITO: Extrae y normaliza las ciudades únicas de los datos originales
-- CARACTERÍSTICAS: Utiliza TRIM para limpiar espacios y filtra valores nulos
-- ---------------------------------------------------------------------------------------------------------------------

INSERT INTO corregido.Ciudades (descripcion)
SELECT DISTINCT TRIM(s.ciudad_entidad)
FROM inicial.tabla_sin_corregir s
WHERE s.ciudad_entidad IS NOT NULL;


-- ---------------------------------------------------------------------------------------------------------------------
-- CARGA: Órdenes administrativos únicos
-- PROPÓSITO: Extrae los diferentes órdenes administrativos de las entidades
-- CARACTERÍSTICAS: Normalización de clasificaciones administrativas
-- ---------------------------------------------------------------------------------------------------------------------

INSERT INTO corregido.Ordenes (descripcion)
SELECT DISTINCT TRIM(orden_entidad)
FROM inicial.tabla_sin_corregir
WHERE orden_entidad IS NOT NULL;

-- ---------------------------------------------------------------------------------------------------------------------
-- CARGA: Modalidades de contratación únicas
-- PROPÓSITO: Extrae las diferentes modalidades de contratación utilizadas
-- CARACTERÍSTICAS: Catálogo de modalidades según normativa de contratación pública
-- ---------------------------------------------------------------------------------------------------------------------

INSERT INTO corregido.Modalidades_contratos (descripcion)
SELECT DISTINCT TRIM(modalidad_contratacion)
FROM inicial.tabla_sin_corregir
WHERE modalidad_contratacion IS NOT NULL;

-- ---------------------------------------------------------------------------------------------------------------------
-- CARGA: Tipos de contratos únicos
-- PROPÓSITO: Extrae los diferentes tipos de contratos según su clasificación
-- CARACTERÍSTICAS: Taxonomía de contratos públicos
-- ---------------------------------------------------------------------------------------------------------------------

INSERT INTO corregido.Tipos_contratos (descripcion)
SELECT DISTINCT TRIM(tipo_contrato)
FROM inicial.tabla_sin_corregir
WHERE tipo_contrato IS NOT NULL;

-- =====================================================================================================================
-- SECCIÓN 4: CARGA DE DATOS TRANSACCIONALES
-- =====================================================================================================================
--
-- Inserción de los registros principales relacionando todas las entidades mediante JOINs 
-- con las tablas de catálogos previamente pobladas. Incluye transformaciones de datos 
-- para garantizar tipos correctos.
-- =====================================================================================================================

-- ---------------------------------------------------------------------------------------------------------------------
-- CARGA: Entidades con sus relaciones geográficas y administrativas
-- PROPÓSITO: Registra las entidades únicas con sus características
-- CARACTERÍSTICAS: Agrupa por NIT para evitar duplicados, transforma el campo centralizada
-- ---------------------------------------------------------------------------------------------------------------------


INSERT INTO corregido.Entidades (nit_entidad, ciudad_id, orden_id, centralizada)
SELECT nit_entidad, ciudad_id, orden_id, centralizada
FROM (
         SELECT CAST(s.nit_entidad AS BIGINT) AS nit_entidad,
                MIN(c.id) AS ciudad_id,
                MIN(o.id) AS orden_id,
                CASE
                    WHEN LOWER(TRIM(MAX(s.entidad_centralizada))) LIKE 'centralizada%' THEN 'S'
                    WHEN LOWER(TRIM(MAX(s.entidad_centralizada))) LIKE 'descentralizada%' THEN 'N'
                    ELSE NULL
                    END AS centralizada
         FROM inicial.tabla_sin_corregir s
                  JOIN corregido.Ciudades c
                       ON c.descripcion = TRIM(s.ciudad_entidad)
                  JOIN corregido.Ordenes o
                       ON o.descripcion = TRIM(s.orden_entidad)
         WHERE s.nit_entidad IS NOT NULL
         GROUP BY CAST(s.nit_entidad AS BIGINT)
     ) sub;

-- ---------------------------------------------------------------------------------------------------------------------
-- CARGA: Procesos de contratación con transformaciones de datos
-- PROPÓSITO: Registra los procesos únicos con conversiones de tipos de dato
-- CARACTERÍSTICAS: Convierte duraciones a días, limpia valores monetarios, transforma fechas
-- ---------------------------------------------------------------------------------------------------------------------

INSERT INTO corregido.Procesos (id, fecha, precio_base, id_modalidad, duracion,
                                id_tipo_contrato, nit_entidad)
SELECT id_proceso,
       TO_DATE(fecha_proceso, 'MM/DD/YYYY'),   -- ajusta formato según tu CSV
       CAST(REPLACE(precio_base, ',', '') AS NUMERIC),
       m.id,
       CASE
           WHEN LOWER(unidad_duracion) LIKE '%mes%'    THEN CAST(REPLACE(duracion, ',', '') AS INT) * 30
           WHEN LOWER(unidad_duracion) LIKE '%año%'    THEN CAST(REPLACE(duracion, ',', '') AS INT) * 365
           WHEN LOWER(unidad_duracion) LIKE '%semana%' THEN CAST(REPLACE(duracion, ',', '') AS INT) * 7
           ELSE CAST(REPLACE(duracion, ',', '') AS INT)
           END AS duracion_dias,
       t.id,
       CAST(s.nit_entidad AS BIGINT)
FROM (
         SELECT DISTINCT id_proceso, fecha_proceso, precio_base, modalidad_contratacion,
                         duracion, unidad_duracion, tipo_contrato, nit_entidad
         FROM inicial.tabla_sin_corregir
     ) s
         JOIN corregido.Modalidades_contratos m ON m.descripcion = TRIM(s.modalidad_contratacion)
         JOIN corregido.Tipos_contratos t ON t.descripcion = TRIM(s.tipo_contrato);

-- =====================================================================================================================
-- SECCIÓN 5: VERIFICACIÓN DE INTEGRIDAD DE DATOS
-- =====================================================================================================================
--
-- Consultas de verificación para validar que la carga de datos se realizó correctamente
-- y que las relaciones entre tablas están funcionando adecuadamente.
-- =====================================================================================================================

-- Verificación de conteos por tabla
SELECT 'Ciudades' as tabla, COUNT(*) as registros FROM corregido.Ciudades
UNION ALL
SELECT 'Ordenes', COUNT(*) FROM corregido.Ordenes
UNION ALL
SELECT 'Modalidades_contratos', COUNT(*) FROM corregido.Modalidades_contratos
UNION ALL
SELECT 'Tipos_contratos', COUNT(*) FROM corregido.Tipos_contratos
UNION ALL
SELECT 'Entidades', COUNT(*) FROM corregido.Entidades
UNION ALL
SELECT 'Procesos', COUNT(*) FROM corregido.Procesos;

-- =====================================================================================================================
-- FIN DEL SCRIPT DE IMPLEMENTACIÓN
-- =====================================================================================================================
