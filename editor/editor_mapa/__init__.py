"""Editor de mapas de arbitraje (Eurobot).

Organizado en Modelo - Vista - Controlador:

    modelo/       los datos del mapa y sus reglas. Sin tkinter ni PIL.
    persistencia/ leer y escribir XML, y volcar los catalogos a SQL. Sin interfaz.
    vista/        todo lo que se ve: lienzo, barra de herramientas y dialogos.
    controlador/  traduce las acciones del usuario en cambios del modelo.

El punto de entrada es la funcion `main` de este mismo paquete. La version del
editor se declara en pyproject.toml.
"""


def main():
    import tkinter as tk

    from .controlador import Controlador

    root = tk.Tk()
    Controlador(root)
    root.mainloop()