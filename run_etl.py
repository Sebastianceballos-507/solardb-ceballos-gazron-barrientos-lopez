import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import psycopg2

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "lecturas.jsonl"
TABLAS_SQL = ROOT / "sql" / "01_tablas.sql"

def conexion():
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "solardb"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", "")
    )

def ejecutar_sql(cur, ruta):
    cur.execute(Path(ruta).read_text(encoding="utf-8"))

def main():
    inicio = datetime.now(timezone.utc)

    # Genera/reemplaza el archivo con los mismos dispositivos y marcas de tiempo.
    subprocess.run(
        ["python", str(ROOT / "etl" / "simulador.py")],
        check=True,
        cwd=ROOT
    )

    conn = conexion()
    cur = conn.cursor()

    try:
        ejecutar_sql(cur, TABLAS_SQL)
        conn.commit()

        cur.execute("SELECT COALESCE(MAX(id), 0) FROM stg_lectura_raw")
        ultimo_id = cur.fetchone()[0]

        with DATA_FILE.open("r", encoding="utf-8") as f:
            mensajes = [json.loads(line) for line in f if line.strip()]

        filas_leidas = len(mensajes)

        for mensaje in mensajes:
            cur.execute(
                "INSERT INTO stg_lectura_raw (payload) VALUES (%s::jsonb)",
                (json.dumps(mensaje),)
            )

        cur.execute(
            """
            INSERT INTO lectura_demo (
                dispositivo_id, ts, p_ac, irradiancia, temp_modulo, payload
            )
            SELECT
                (payload ->> 'device_id')::INT,
                (payload ->> 'ts')::TIMESTAMPTZ,
                (payload ->> 'p_ac')::NUMERIC(10,3),
                (payload ->> 'irradiancia')::NUMERIC(8,1),
                (payload ->> 'temp_modulo')::NUMERIC(5,1),
                payload
            FROM stg_lectura_raw
            WHERE id > %s
            ON CONFLICT (dispositivo_id, ts) DO NOTHING
            """,
            (ultimo_id,)
        )

        filas_cargadas = cur.rowcount
        filas_rechazadas = filas_leidas - filas_cargadas
        estado = "OK"
        error = None

        fin = datetime.now(timezone.utc)

        cur.execute(
            """
            INSERT INTO etl_log
            (inicio, fin, filas_leidas, filas_cargadas, filas_rechazadas, estado, error)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (inicio, fin, filas_leidas, filas_cargadas, filas_rechazadas, estado, error)
        )

        conn.commit()

        cur.execute("SELECT COUNT(*) FROM lectura_demo")
        total = cur.fetchone()[0]

        print("ETL finalizado correctamente.")
        print(f"Filas leídas: {filas_leidas}")
        print(f"Filas cargadas: {filas_cargadas}")
        print(f"Filas rechazadas/conflictivas: {filas_rechazadas}")
        print(f"Total en lectura_demo: {total}")

    except Exception as exc:
        conn.rollback()
        fin = datetime.now(timezone.utc)

        cur.execute(
            """
            INSERT INTO etl_log
            (inicio, fin, filas_leidas, filas_cargadas, filas_rechazadas, estado, error)
            VALUES (%s, %s, 0, 0, 0, %s, %s)
            """,
            (inicio, fin, "ERROR", str(exc))
        )
        conn.commit()
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
