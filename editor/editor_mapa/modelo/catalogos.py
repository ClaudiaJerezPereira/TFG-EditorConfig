"""Catalogos: las tablas de referencia de la base de datos.

    totales  -> General_Resultado
    lados    -> Partido_Lado
    arbitros -> Arbitraje_ListaArbitros
    estilos  -> Arbitraje_EstiloFuente

Los cuatro se vuelcan al exportar el SQL (CATALOGOS_VOLCADOS).

Modulo del MODELO: no importa tkinter ni nada de la interfaz.
"""
import colorsys

from .constantes import CATALOGOS_VOLCADOS, ID_MINIMO, ID_MINIMO_CATALOGO

# Punto de partida de Partido_Lado: el tono y la saturacion se dan en 0..1 (matiz
# HSV), no en grados. El 0 es el lado "comun" (acciones que puntuan a los dos
# equipos) y el 1 y el 2 son los dos equipos del partido: ese convenio lo da por
# hecho la aplicacion de arbitraje, asi que estos tres IDs no se renumeran.
LADOS_DEFECTO = [
    {"id": 0, "nombre": "Común",    "color_h": 0.100, "color_s": 0.100},
    {"id": 1, "nombre": "Amarillo", "color_h": 0.122, "color_s": 0.919},
    {"id": 2, "nombre": "Azul",     "color_h": 0.559, "color_s": 0.519},
]

# General_Resultado: los totales generales del partido. Comparten numeracion con
# Arbitraje_GrupoAcciones y ocupan siempre las primeras posiciones (1..N, sin
# huecos); los grupos que dibuja el usuario empiezan en N+1. Puede haber los que
# hagan falta: si se anade uno, los grupos se corren un puesto.
TOTALES_DEFECTO = [
    {"id": 1, "nombre": "TOTAL PUNTOS"},
    {"id": 2, "nombre": "Total robot"},
]

ARBITROS_DEFECTO = []   # el usuario los anade segun la competicion

# El ID empieza en 1: es la clave primaria de Arbitraje_EstiloFuente y el editor no
# admite ni el 0 ni los negativos (ver ID_MINIMO en constantes).
ESTILOS_DEFECTO = [
    {"id": 1, "descripcion": "Normal", "nombre_fuente": "Arial",
     "estilo_fuente": "bold", "tamano_fuente": 20, "color_fuente": "#000000"},
]


def color_lado(lado, color_v=255):
    """Color de fondo de un control: HSV con el tono y la saturacion del lado
    (Partido_Lado) y el valor que indique color_v (0-255), como en la aplicacion
    de arbitraje. Sin lado, devuelve None y quien dibuje usara un color de respaldo."""
    if not lado:
        return None
    try:
        h = float(lado.get("color_h", 0))
        s = float(lado.get("color_s", 0))
    except (TypeError, ValueError):
        return None
    # En la base de datos el tono va en 0..1; se admiten grados por compatibilidad.
    if h > 1.0:
        h = (h % 360.0) / 360.0
    v = max(0.0, min(255.0, float(color_v))) / 255.0
    r, g, b = colorsys.hsv_to_rgb(h, max(0.0, min(1.0, s)), v)
    return "#%02x%02x%02x" % (int(r * 255 + 0.5), int(g * 255 + 0.5), int(b * 255 + 0.5))


class Catalogos:
    """Las tres tablas de referencia, con sus busquedas por identificador."""

    def __init__(self):
        self.totales = [dict(t) for t in TOTALES_DEFECTO]
        self.lados = [dict(l) for l in LADOS_DEFECTO]
        self.arbitros = [dict(a) for a in ARBITROS_DEFECTO]
        self.estilos = [dict(e) for e in ESTILOS_DEFECTO]
        # Cuales se vuelcan a la base de datos al exportar el SQL.
        self.volcar = list(CATALOGOS_VOLCADOS)

    def reiniciar(self):
        self.__init__()

    # --- Busquedas ---
    def renumerar_totales(self):
        """Deja los totales en 1..N sin huecos, respetando su orden en la lista.
        Su ID no es un dato libre: es el hueco que reservan en
        Arbitraje_GrupoAcciones."""
        for n, t in enumerate(self.totales, ID_MINIMO_CATALOGO):
            t["id"] = n
        return self.totales

    def primer_grupo(self):
        """Primer ID_GRUPO_ACCIONES libre para los grupos que dibuja el usuario: los
        totales ocupan 1..N, asi que los grupos empiezan en N+1."""
        return len(self.totales) + ID_MINIMO_CATALOGO

    def lado(self, ident):
        return next((l for l in self.lados if l["id"] == ident), None)

    def estilo(self, ident):
        est = next((e for e in self.estilos if e["id"] == ident), None)
        if est is not None:
            return est
        return self.estilos[0] if self.estilos else None

    def estilo_defecto(self):
        # Sin catalogo se devuelve el minimo, no 0: un 0 seria un ID invalido y la
        # base de datos rechazaria la clave ajena.
        return self.estilos[0]["id"] if self.estilos else ID_MINIMO_CATALOGO

    def color(self, id_lado, color_v=255):
        return color_lado(self.lado(id_lado), color_v)

    # --- Comprobacion de los identificadores ---
    def ids_invalidos(self):
        """Filas cuyo ID no llega al minimo de su catalogo.

        Devuelve una lista de textos ya redactados, para poder avisar igual al abrir
        un XML antiguo y al exportar el SQL."""
        avisos = []
        for cual, nombre in (("totales", "total general"), ("lados", "lado"),
                             ("arbitros", "árbitro"),
                             ("estilos", "estilo de fuente")):
            minimo = ID_MINIMO[cual]
            for fila in getattr(self, cual):
                try:
                    ident = int(fila.get("id"))
                except (TypeError, ValueError):
                    avisos.append(f"Hay un {nombre} sin ID numérico.")
                    continue
                if ident < minimo:
                    avisos.append(
                        f"El {nombre} con ID {ident} no es válido: el ID es la clave "
                        f"primaria de la tabla y en este catálogo tiene que ser "
                        f"{minimo} o mayor.")
        return avisos