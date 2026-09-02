"""Controlador: une el modelo con la vista.

Es el unico que conoce las dos capas. Aqui viven el modo de trabajo, la seleccion
y el arrastre, que son estado de la edicion y no del documento.
"""
from .principal import Controlador

__all__ = ["Controlador"]
