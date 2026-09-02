"""Comprueba que el controlador solo usa metodos y atributos que existen.

No basta con dir(clase): la mayoria de los atributos se crean en __init__, asi que
tambien se recogen las asignaciones "self.X = ..." del codigo fuente de cada clase.
"""
import ast, inspect, sys

import rutas   # noqa: F401  (deja el paquete importable)
import prueba_estructura as pe

pe.preparar_dobles()

from editor_mapa.controlador.principal import Controlador
from editor_mapa.modelo import ModeloMapa
from editor_mapa.persistencia import sql_io, xml_io
from editor_mapa.vista.lienzo import VistaLienzo
from editor_mapa.vista.ventana import VentanaPrincipal


def miembros(cls):
    nombres = set(dir(cls))
    for base in cls.__mro__:
        try:
            arbol = ast.parse(inspect.getsource(base))
        except (OSError, TypeError):
            continue
        for n in ast.walk(arbol):
            if (isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
                    and n.value.id == "self" and isinstance(n.ctx, ast.Store)):
                nombres.add(n.attr)
    return nombres


objetivos = {"modelo": ModeloMapa, "vista": VentanaPrincipal, "lienzo": VistaLienzo}
disponibles = {k: miembros(v) for k, v in objetivos.items()}
modulos = {"xml_io": xml_io, "sql_io": sql_io}

arbol = ast.parse(inspect.getsource(Controlador))
fallos, usos = [], 0
for n in ast.walk(arbol):
    if isinstance(n, ast.Attribute):
        v = n.value
        if (isinstance(v, ast.Attribute) and isinstance(v.value, ast.Name)
                and v.value.id == "self" and v.attr in objetivos):
            usos += 1
            if n.attr not in disponibles[v.attr]:
                fallos.append(f"línea {n.lineno}: self.{v.attr}.{n.attr} no existe en "
                              f"{objetivos[v.attr].__name__}")
        elif isinstance(v, ast.Name) and v.id in modulos:
            usos += 1
            if not hasattr(modulos[v.id], n.attr):
                fallos.append(f"línea {n.lineno}: {v.id}.{n.attr} no existe")

print(f"{usos} accesos del controlador al modelo, la vista y la persistencia.")
for f in fallos:
    print("  ", f)
print("Todos existen." if not fallos else f"{len(fallos)} fallo(s).")
sys.exit(1 if fallos else 0)
