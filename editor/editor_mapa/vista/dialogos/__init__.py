"""Dialogos modales del editor, uno por tabla de la base de datos."""
from .accion import DialogoAccion
from .catalogo import DialogoCatalogo
from .contenido import DialogoContenido
from .grupo import DialogoGrupo
from .total import DialogoTotal
from .zona import DialogoZona

__all__ = ["DialogoAccion", "DialogoCatalogo", "DialogoContenido",
           "DialogoGrupo", "DialogoTotal", "DialogoZona"]