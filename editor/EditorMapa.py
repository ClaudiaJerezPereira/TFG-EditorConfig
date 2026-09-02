#!/usr/bin/env python3
"""Editor de mapas de arbitraje (Eurobot) - punto de entrada.

Todo el codigo esta en el paquete `editor_mapa`, organizado en Modelo, Vista y
Controlador. Este archivo solo arranca la aplicacion:

    python3 EditorMapa.py

El modelo (`editor_mapa.modelo`) y la persistencia (`editor_mapa.persistencia`)
no dependen de tkinter, asi que pueden usarse y probarse sin interfaz grafica.
"""
from editor_mapa import main

if __name__ == "__main__":
    main()
