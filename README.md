# SolarDB – Gobernanza, ETL e IoT

**Curso:** Bases de Datos I (SD1006)  
**Grupo:** 811  
**Docente:** Ramiro Grisales Montoya  
**Semestre:** 2026-II

## Integrantes

- Sebastián Ceballos Garzón
- [NOMBRE COMPLETO DEL SEGUNDO INTEGRANTE]

## Descripción

Este repositorio contiene la consulta y práctica guiada sobre gobernanza de datos, automatización ETL e IoT aplicada a SolarDB Pascual.

Se implementa un flujo reproducible en PostgreSQL 15 o superior en el que:

1. `etl/simulador.py` genera telemetría JSONL de dos inversores.
2. Los mensajes se cargan a `stg_lectura_raw`.
3. SQL extrae atributos del `JSONB` y los carga a `lectura_demo`.
4. La clave primaria `(dispositivo_id, ts)` y `ON CONFLICT DO NOTHING` hacen que la carga sea idempotente.
5. `etl_log` registra cada ejecución.
6. `sql/03_roles.sql` crea roles de ingesta, lectura y administración.
7. `solar_lector` tiene únicamente permiso de `SELECT` sobre `lectura_demo`.

> No se almacenan contraseñas ni cadenas de conexión en el repositorio.

## Estructura

```text
solardb-apellido1-apellido2/
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
├── docs/
│   └── [PDF final de la consulta]
├── data/
│   └── lecturas.jsonl
├── etl/
│   ├── simulador.py
│   └── run_etl.py
└── sql/
    ├── 01_tablas.sql
    ├── 02_carga.sql
    └── 03_roles.sql
```

## Requisitos

- PostgreSQL 15 o superior.
- Python 3.10 o superior.
- `psycopg2-binary`.
- Una base de datos llamada `solardb` o el nombre configurado mediante variables de entorno.

## Configuración

Crear una base de datos, por ejemplo:

```sql
CREATE DATABASE solardb;
```

Copiar `.env.example` a `.env` y colocar las credenciales localmente. El archivo `.env` está excluido por `.gitignore`.

En la terminal:

```bash
pip install -r requirements.txt
```

Configurar las variables de entorno de PostgreSQL. En Windows PowerShell, por ejemplo:

```powershell
$env:PGHOST="localhost"
$env:PGPORT="5432"
$env:PGDATABASE="solardb"
$env:PGUSER="postgres"
$env:PGPASSWORD="SU_CLAVE_LOCAL"
```

## Ejecución

Desde la raíz del repositorio:

```bash
python etl/run_etl.py
```

El comando genera el archivo JSONL, crea las tablas si no existen, carga el staging, transforma los datos y registra la ejecución.

Para crear los roles:

```bash
psql -U postgres -d solardb -f sql/03_roles.sql
```

## Prueba de idempotencia

Ejecutar dos veces:

```bash
python etl/run_etl.py
```

Luego:

```sql
SELECT COUNT(*) FROM lectura_demo;
```

Resultado esperado:

- Primera ejecución: `288` filas.
- Segunda ejecución con los mismos identificadores de dispositivo y tiempo: `288` filas.

La segunda ejecución no duplica registros porque la clave primaria es `(dispositivo_id, ts)` y la inserción usa:

```sql
ON CONFLICT (dispositivo_id, ts) DO NOTHING;
```

## Prueba del rol de solo lectura

Con el rol `solar_lector`:

```sql
SELECT * FROM lectura_demo LIMIT 5;
```

Debe funcionar.

En cambio:

```sql
INSERT INTO lectura_demo
(dispositivo_id, ts, p_ac, irradiancia, temp_modulo)
VALUES (99, now(), 1.000, 500.0, 30.0);
```

Debe ser rechazado por falta de privilegio `INSERT`.

## Automatización

En Linux/macOS, una expresión cron que ejecuta el flujo cada hora es:

```cron
0 * * * * cd /ruta/al/repositorio && /usr/bin/python3 etl/run_etl.py >> etl/etl.log 2>&1
```

En Windows se puede crear una tarea en el Programador de tareas con periodicidad de una hora que ejecute:

```text
python C:\ruta\al\repositorio\etl\run_etl.py
```

## Participación

| Integrante | Actividades |
|---|---|
| Sebastián Ceballos Garzón | Consulta de gobernanza, SQL, simulador y documentación del pipeline |
| [SEGUNDO INTEGRANTE] | Consulta ETL/IoT, pruebas, evidencias y apoyo en documentación |

## Frase del trabajo

> An idempotent ETL pipeline that loads simulated IoT telemetry into a governed PostgreSQL repository, versioned on GitHub.
