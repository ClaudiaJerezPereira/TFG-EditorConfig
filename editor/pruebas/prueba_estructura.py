"""Importa todos los modulos del paquete para detectar errores de import.

Este contenedor no tiene tkinter ni PIL, asi que se sustituyen por dobles. No
prueba la interfaz (eso hay que verlo a ojo), pero si que todos los modulos se
cargan, que las clases se definen y que no falta ningun import al haber partido
el archivo original en varios.
"""
import importlib
import sys
import types

import rutas   # noqa: F401  (deja el paquete importable)


class _Falso:
    """Objeto que acepta cualquier cosa: llamadas, atributos e indexacion."""

    def __init__(self, *a, **k):
        pass

    def __getattr__(self, nombre):
        return _Falso()

    def __call__(self, *a, **k):
        return _Falso()

    def __getitem__(self, k):
        return _Falso()

    def __setitem__(self, k, v):
        pass


def _modulo(nombre, **atributos):
    m = types.ModuleType(nombre)
    m.__getattr__ = lambda a: _Falso
    for k, v in atributos.items():
        setattr(m, k, v)
    sys.modules[nombre] = m
    return m


class _Font:
    def __init__(self, family=None, size=0, weight=None):
        self.px = abs(int(size))

    def measure(self, texto):
        return int(len(texto) * self.px * 0.6)

    def metrics(self, cual):
        return int(self.px * 1.2)


def preparar_dobles():
    try:
        import tkinter  # noqa
        return False
    except ImportError:
        pass
    tk = _modulo("tkinter")
    tk.Toplevel = type("Toplevel", (), {"__init__": lambda s, *a, **k: None})
    for sub in ("ttk", "filedialog", "messagebox", "simpledialog"):
        setattr(tk, sub, _modulo(f"tkinter.{sub}"))
    tk.font = _modulo("tkinter.font", Font=_Font)

    img = _modulo("PIL.Image", Resampling=types.SimpleNamespace(LANCZOS=1), LANCZOS=1)
    itk = _modulo("PIL.ImageTk", PhotoImage=_Falso)
    _modulo("PIL", Image=img, ImageTk=itk)
    return True


MODULOS = [
    "editor_mapa",
    "editor_mapa.modelo",
    "editor_mapa.modelo.constantes",
    "editor_mapa.modelo.catalogos",
    "editor_mapa.modelo.geometria",
    "editor_mapa.modelo.mapa",
    "editor_mapa.persistencia",
    "editor_mapa.persistencia.xml_io",
    "editor_mapa.persistencia.sql_io",
    "editor_mapa.vista.apariencia",
    "editor_mapa.vista.fuentes",
    "editor_mapa.vista.imagenes",
    "editor_mapa.vista.lienzo",
    "editor_mapa.vista.ventana",
    "editor_mapa.vista.dialogos",
    "editor_mapa.controlador",
    "editor_mapa.controlador.principal",
]

SIN_INTERFAZ = [m for m in MODULOS
                if ".modelo" in m or ".persistencia" in m or m == "editor_mapa"]


def main():
    # 1) El modelo y la persistencia deben cargar SIN que exista tkinter, asi que se
    #    importan ANTES de poner los dobles: si arrastraran la interfaz, apareceria
    #    en sys.modules.
    for nombre in SIN_INTERFAZ:
        importlib.import_module(nombre)
    intrusos = sorted(m for m in sys.modules if m.split(".")[0] in ("tkinter", "PIL"))
    print(f"Modelo y persistencia cargados. Interfaz arrastrada: {intrusos or 'ninguna'}")
    assert not intrusos, "el modelo no debe depender de tkinter ni de PIL"

    preparar_dobles()

    # 2) El resto, ya con los dobles puestos.
    for nombre in MODULOS:
        importlib.import_module(nombre)
    print(f"{len(MODULOS)} módulos importados sin errores.")

    # 3) Las clases principales existen.
    from editor_mapa.controlador import Controlador
    from editor_mapa.modelo import ModeloMapa
    from editor_mapa.vista.dialogos import (DialogoAccion, DialogoCatalogo,
                                            DialogoContenido, DialogoGrupo, DialogoZona)
    from editor_mapa.vista.lienzo import VistaLienzo
    from editor_mapa.vista.ventana import VentanaPrincipal
    for cls in (ModeloMapa, Controlador, VistaLienzo, VentanaPrincipal, DialogoAccion,
                DialogoCatalogo, DialogoContenido, DialogoGrupo, DialogoZona):
        assert isinstance(cls, type), cls
    print("Clases principales disponibles.")

    # 4) Todas las acciones de la barra tienen su metodo en el controlador.
    import inspect
    fuente = inspect.getsource(Controlador._acciones)
    claves = [l.split('"')[1] for l in fuente.split("\n") if l.strip().startswith('"')]
    from editor_mapa.vista import ventana as v
    usadas = {a for _, a in (v.BOTONES_ARCHIVO + v.BOTONES_GUIAS + v.BOTONES_EDICION)}
    usadas |= {"zoom", "catalogos", "simetria", "modo", "nuevo_grupo",
               "colocar_grupo", "elegir_grupo"}
    faltan = usadas - set(claves)
    print(f"Acciones declaradas: {len(claves)}; usadas por la vista: {len(usadas)}.")
    assert not faltan, f"la vista pide acciones que el controlador no ofrece: {faltan}"

    print("\nTodas las comprobaciones han pasado.")


if __name__ == "__main__":
    main()
