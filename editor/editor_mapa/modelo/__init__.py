"""Modelo: los datos del mapa de arbitraje y las reglas que los gobiernan.

Ningun modulo de este paquete importa tkinter ni PIL: el modelo se puede usar
(y probar) sin interfaz grafica.

Aqui solo se reexporta lo que se usa desde fuera del paquete. Las constantes del
dominio se importan de su modulo (`from ..modelo.constantes import ...`), que es
lo que hacen la vista, la persistencia y el controlador.
"""
from .catalogos import color_lado
from .mapa import ModeloMapa

__all__ = ["ModeloMapa", "color_lado"]