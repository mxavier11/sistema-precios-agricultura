-- =============================================
-- SCHEMA: SISTEMA DE PRECIOS PRODUCTOR
-- =============================================

-- ---------------------------------------------
-- Tabla: usuario_simulado
-- ---------------------------------------------
CREATE TABLE IF NOT EXISTS usuario_simulado (
    id SERIAL PRIMARY KEY,
    nombre TEXT UNIQUE NOT NULL
);

-- ---------------------------------------------
-- Tabla: producto
-- ---------------------------------------------
CREATE TABLE IF NOT EXISTS producto (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    unidad TEXT NOT NULL
);

CREATE INDEX idx_producto_nombre ON producto(nombre);

-- ---------------------------------------------
-- Tabla: precio_productor
-- ---------------------------------------------
CREATE TABLE IF NOT EXISTS precio_productor (
    id SERIAL PRIMARY KEY,
    anio INT NOT NULL,
    mes TEXT NOT NULL,
    producto_id INT REFERENCES producto(id),
    ponderado_usd NUMERIC,
    ponderado_usd_kg NUMERIC,
    UNIQUE(anio, mes, producto_id)
);

CREATE INDEX idx_precio_productor_producto_id ON precio_productor(producto_id);
CREATE INDEX idx_precio_anio_mes_producto ON precio_productor(anio, mes, producto_id);


-- ---------------------------------------------
-- Tabla: log_auditoria
-- ---------------------------------------------
CREATE TABLE IF NOT EXISTS log_auditoria (
    id SERIAL PRIMARY KEY,
    tabla_afectada TEXT NOT NULL,
    operacion TEXT NOT NULL,
    usuario_simulado TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    datos_antes JSONB,
    datos_despues JSONB
);


-- =============================================
-- FUNCION: insertar log de auditoría
-- =============================================
CREATE OR REPLACE FUNCTION registrar_auditoria(
    tabla_afectada TEXT,
    operacion TEXT,
    usuario_simulado TEXT,
    datos_antes JSONB,
    datos_despues JSONB
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO log_auditoria(tabla_afectada, operacion, usuario_simulado, datos_antes, datos_despues)
    VALUES (tabla_afectada, operacion, usuario_simulado, datos_antes, datos_despues);
END;
$$ LANGUAGE plpgsql;


-- =============================================
-- PROCEDIMIENTO: insertar producto
-- =============================================
CREATE OR REPLACE PROCEDURE insertar_producto(
    p_nombre TEXT,
    p_unidad TEXT,
    p_usuario_simulado TEXT
)
LANGUAGE plpgsql AS $$
DECLARE
    producto_existente_id INT;
BEGIN
    SELECT id INTO producto_existente_id FROM producto WHERE nombre = p_nombre;

    IF producto_existente_id IS NULL THEN
        INSERT INTO producto(nombre, unidad) VALUES (p_nombre, p_unidad);
        PERFORM registrar_auditoria(
            'producto',
            'INSERT',
            p_usuario_simulado,
            NULL,
            jsonb_build_object('nombre', p_nombre, 'unidad', p_unidad)
        );
    ELSE
        -- Si ya existe, no se inserta nada
        RAISE NOTICE 'Producto ya existe: %', p_nombre;
    END IF;
END;
$$;


-- =============================================
-- PROCEDIMIENTO: insertar precio productor
-- =============================================
CREATE OR REPLACE PROCEDURE insertar_precio_productor(
    p_anio INT,
    p_mes TEXT,
    p_nombre_producto TEXT,
    p_ponderado_usd NUMERIC,
    p_ponderado_usd_kg NUMERIC,
    p_usuario_simulado TEXT
)
LANGUAGE plpgsql AS $$
DECLARE
    producto_id INT;
    precio_existente RECORD;
BEGIN
    SELECT id INTO producto_id FROM producto WHERE nombre = p_nombre_producto;

    IF producto_id IS NULL THEN
        RAISE EXCEPTION 'El producto % no existe en la tabla producto', p_nombre_producto;
    END IF;

    SELECT * INTO precio_existente
    FROM precio_productor
    WHERE anio = p_anio AND mes = p_mes AND producto_id = producto_id;

    IF precio_existente IS NULL THEN
        INSERT INTO precio_productor(anio, mes, producto_id, ponderado_usd, ponderado_usd_kg)
        VALUES (p_anio, p_mes, producto_id, p_ponderado_usd, p_ponderado_usd_kg);

        PERFORM registrar_auditoria(
            'precio_productor',
            'INSERT',
            p_usuario_simulado,
            NULL,
            jsonb_build_object(
                'anio', p_anio,
                'mes', p_mes,
                'producto_id', producto_id,
                'ponderado_usd', p_ponderado_usd,
                'ponderado_usd_kg', p_ponderado_usd_kg
            )
        );

    ELSE
        -- Actualiza si ya existe
        UPDATE precio_productor
        SET
            ponderado_usd = p_ponderado_usd,
            ponderado_usd_kg = p_ponderado_usd_kg
        WHERE id = precio_existente.id;

        PERFORM registrar_auditoria(
            'precio_productor',
            'UPDATE',
            p_usuario_simulado,
            to_jsonb(precio_existente),
            jsonb_build_object(
                'anio', p_anio,
                'mes', p_mes,
                'producto_id', producto_id,
                'ponderado_usd', p_ponderado_usd,
                'ponderado_usd_kg', p_ponderado_usd_kg
            )
        );
    END IF;
END;
$$;


-- =============================================
-- TRIGGER FUNCTION: auditoría en DELETE
-- =============================================
CREATE OR REPLACE FUNCTION trigger_auditoria_delete()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM registrar_auditoria(
        TG_TABLE_NAME,
        'DELETE',
        current_setting('app.usuario_simulado', true),
        to_jsonb(OLD),
        NULL
    );
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- ASIGNAR TRIGGER a precio_productor
-- =============================================
CREATE TRIGGER auditoria_delete_precio
AFTER DELETE ON precio_productor
FOR EACH ROW
EXECUTE FUNCTION trigger_auditoria_delete();


-- =============================================
-- Consulta 1: Precio promedio anual por producto
-- =============================================
SELECT
    p.nombre,
    pp.anio,
    ROUND(AVG(pp.ponderado_usd), 2) AS promedio_usd
FROM
    precio_productor pp
JOIN producto p ON pp.producto_id = p.id
GROUP BY p.nombre, pp.anio
ORDER BY p.nombre, pp.anio;


-- =============================================
-- Consulta 2: Evolución histórica de precios por producto
-- =============================================
SELECT
    p.nombre,
    pp.anio,
    pp.mes,
    pp.ponderado_usd,
    pp.ponderado_usd_kg
FROM
    precio_productor pp
JOIN producto p ON pp.producto_id = p.id
ORDER BY p.nombre, pp.anio, pp.mes;


-- =============================================
-- Consulta 3: Productos con mayor variación de precio
-- =============================================
WITH stats AS (
    SELECT
        producto_id,
        MAX(ponderado_usd) - MIN(ponderado_usd) AS variacion
    FROM
        precio_productor
    GROUP BY producto_id
)
SELECT
    p.nombre,
    s.variacion
FROM
    stats s
JOIN producto p ON s.producto_id = p.id
ORDER BY s.variacion DESC;


-- =============================================
-- NOTA PARA EL EQUIPO:
-- Para auditar correctamente las acciones desde el backend,
-- recuerden ejecutar antes de llamar a procedimientos:
-- SET app.usuario_simulado = 'nombre_usuario';
-- =============================================
