-- Transformación y carga idempotente desde staging hacia la tabla relacional.
-- ->> extrae cada Atributo como texto y los casteamos al tipo destino.

INSERT INTO lectura_demo (
    dispositivo_id,
    ts,
    p_ac,
    irradiancia,
    temp_modulo,
    payload
)
SELECT
    (payload ->> 'device_id')::INT,
    (payload ->> 'ts')::TIMESTAMPTZ,
    (payload ->> 'p_ac')::NUMERIC(10,3),
    (payload ->> 'irradiancia')::NUMERIC(8,1),
    (payload ->> 'temp_modulo')::NUMERIC(5,1),
    payload
FROM stg_lectura_raw
ON CONFLICT (dispositivo_id, ts) DO NOTHING;
