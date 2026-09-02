"""Vista: todo lo que se ve y todo lo que sabe de tkinter.

    apariencia -> colores, textos y tamanos
    fuentes    -> medidas de texto (hay que preguntarle a Tk)
    imagenes   -> carga y cacheo de iconos
    lienzo     -> dibujo del mapa
    ventana    -> barra de herramientas, lienzo y barra de estado
    dialogos   -> un dialogo por tabla de la base de datos
"""
from .lienzo import VistaLienzo
from .ventana import VentanaPrincipal

__all__ = ["VistaLienzo", "VentanaPrincipal"]
