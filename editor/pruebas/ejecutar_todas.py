#!/usr/bin/env python3
"""Ejecuta todas las pruebas del editor y resume el resultado.

    python3 pruebas/ejecutar_todas.py

Cada prueba se lanza en su propio proceso, porque algunas sustituyen tkinter y
PIL por dobles y no deben contaminar a las demás.
"""
import subprocess
import sys

from rutas import PAQUETE, PRUEBAS

PRUEBAS_A_EJECUTAR = [
    ("prueba_estructura.py", [],
     "Los módulos se importan y el modelo no depende de la interfaz"),
    ("prueba_modelo.py", [],
     "Guías, grupos, simetría, totales y guardado en XML"),
    ("prueba_sql.py", [],
     "Generación del SQL y validación de lo que produce"),
    ("prueba_seleccion.py", [],
     "Reparto de responsabilidades entre modelo, vista y controlador"),
    ("comprobar_nombres.py", [str(PAQUETE)],
     "No hay nombres usados sin definir"),
    ("comprobar_atributos.py", [],
     "El controlador solo llama a métodos que existen"),
]


def main():
    fallos = []
    for archivo, args, descripcion in PRUEBAS_A_EJECUTAR:
        print(f"\n{'=' * 70}\n{archivo}: {descripcion}\n{'=' * 70}")
        r = subprocess.run([sys.executable, str(PRUEBAS / archivo)] + args)
        if r.returncode:
            fallos.append(archivo)

    print(f"\n{'=' * 70}")
    if fallos:
        print(f"FALLAN {len(fallos)} de {len(PRUEBAS_A_EJECUTAR)}: "
              f"{', '.join(fallos)}")
        return 1
    print(f"Las {len(PRUEBAS_A_EJECUTAR)} pruebas han pasado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
