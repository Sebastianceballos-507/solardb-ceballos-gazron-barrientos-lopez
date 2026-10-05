# -*- Coding: utf-8 -*-
"""
Created on Sun Oct  4 17:39:07 2026

@author: sebas
"""

import json
import os
import random
from datetime import datetime, timedelta, timezone

# Zona horaria de Colombia
TZ = timezone(timedelta(hours=-5))

# Fecha y hora inicial
inicio = datetime(2026, 10, 5, 6, 0, tzinfo=TZ)

# Crear carpeta data si no existe
os.makedirs("data", exist_ok=True)

# Archivo de salida
archivo = "data/lecturas.jsonl"

with open(archivo, "w", encoding="utf-8") as f:

    # 2 dispositivos, 144 lecturas cada uno
    for device_id in [1, 2]:

        for i in range(144):

            msg = {
                "device_id": device_id,
                "ts": (inicio + timedelta(minutes=5 * i)).isoformat(),
                "p_ac": round(random.uniform(0, 5.0), 3),
                "irradiancia": round(random.uniform(0, 1000), 1),
                "temp_modulo": round(random.uniform(18, 60), 1),
                "frecuencia_hz": round(random.uniform(59.5, 60.5), 2)
            }

            # Aproximadamente 3% de las lecturas tendrán alarma
            if random.random() < 0.03:
                msg["alarma"] = "GRID_FAULT"

            f.write(json.dumps(msg) + "\n")

print("Simulación terminada.")
print("Archivo generado:", archivo)
print("Total de lecturas:", 288)
