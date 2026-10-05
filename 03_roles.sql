-- Ejecutar como propietario de las tablas o como administrador.
-- El rol de lectura no puede modificar lectura_demo.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'solar_ingesta') THEN
        CREATE ROLE solar_ingesta NOLOGIN;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'solar_lector') THEN
        CREATE ROLE solar_lector NOLOGIN;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'solar_admin') THEN
        CREATE ROLE solar_admin NOLOGIN;
    END IF;
END
$$;

REVOKE ALL ON TABLE lectura_demo FROM PUBLIC;
REVOKE ALL ON TABLE stg_lectura_raw FROM PUBLIC;
REVOKE ALL ON TABLE etl_log FROM PUBLIC;

GRANT USAGE ON SCHEMA public TO solar_ingesta, solar_lector, solar_admin;

GRANT INSERT, SELECT ON TABLE stg_lectura_raw TO solar_ingesta;
GRANT SELECT ON TABLE lectura_demo TO solar_lector;

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE lectura_demo TO solar_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE stg_lectura_raw TO solar_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE etl_log TO solar_admin;

-- Evita que el lector cree objetos en public.
REVOKE CREATE ON SCHEMA public FROM solar_lector;
