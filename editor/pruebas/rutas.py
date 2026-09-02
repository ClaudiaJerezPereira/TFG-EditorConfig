"""Rutas del proyecto, para que las pruebas funcionen desde cualquier carpeta.

Todas las pruebas empiezan importando este módulo: deja el paquete `editor_mapa`
al alcance de `import` y publica la ruta del XML de ejemplo.
"""
import sys
from pathlib import Path

PRUEBAS = Path(__file__).resolve().parent
EDITOR = PRUEBAS.parent

XML_EJEMPLO = EDITOR / "graficos" / "arbitraje.xml"
PAQUETE = EDITOR / "editor_mapa"

for carpeta in (EDITOR, PRUEBAS):
    if str(carpeta) not in sys.path:
        sys.path.insert(0, str(carpeta))
