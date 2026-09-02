"""Persistencia: llevar el modelo a un archivo y traerlo de vuelta.

    xml_io   -> formato de trabajo del editor (y fuente del generador de SQL)
    sql_io   -> piezas comunes del SQL (catalogos y ayudantes de formato)
    sql_mapa -> volcado del mapa completo (grupos, guias, controles y parciales)

Tampoco depende de la interfaz.
"""
from . import sql_io, sql_mapa, xml_io

__all__ = ["xml_io", "sql_io", "sql_mapa"]