CREATE TABLE IF NOT EXISTS stg_lectura_raw (
    id BIGSERIAL PRIMARY KEY,
    payload JSONB NOT NULL,
    cargado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS lectura_demo (
    dispositivo_id INT NOT NULL,
    ts TIMESTAMPTZ NOT NULL,
    p_ac NUMERIC(10,3) CHECK (p_ac >= 0),
    irradiancia NUMERIC(8,1) CHECK (irradiancia BETWEEN 0 AND 1500),
    temp_modulo NUMERIC(5,1),
    payload JSONB,
    PRIMARY KEY (dispositivo_id, ts)
);

CREATE TABLE IF NOT EXISTS etl_log (
    id BIGSERIAL PRIMARY KEY,
    inicio TIMESTAMPTZ NOT NULL,
    fin TIMESTAMPTZ,
    filas_leidas INT NOT NULL DEFAULT 0,
    filas_cargadas INT NOT NULL DEFAULT 0,
    filas_rechazadas INT NOT NULL DEFAULT 0,
    estado VARCHAR(20) NOT NULL,
    error TEXT
);
