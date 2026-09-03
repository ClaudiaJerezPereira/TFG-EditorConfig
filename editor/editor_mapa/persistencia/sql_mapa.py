"""Volcado del mapa completo a la base de datos.

Genera el script de datos de una edicion (el equivalente a los
eurobot_ACCIONES_<anio>.sql escritos a mano), con las tablas:

    Arbitraje_GrupoAcciones     los grupos
    Guia_GrupoX / Guia_GrupoY   guias de colocacion (absolutas)
    Guia_ControlX / ControlY    guias de control (relativas al grupo)
    Arbitraje_TotalGrupoAcciones  la etiqueta del total, una fila por grupo
    Arbitraje_TipoAcciones      los botones
    Arbitraje_ZonaAcciones      los parciales
    Arbitraje_Etiqueta          las etiquetas (posicion y contenido)

Modulo sin interfaz: se puede probar sin tkinter.
"""
import os

from ..modelo.constantes import MAX_ID_PARTIDO
from .sql_io import (SEPARADOR, insert_arbitros, insert_estilos, insert_lados,
                     insert_totales, texto_sql)

# Arbitraje_GrupoAcciones comparte identificadores con General_Resultado: los
# primeros son los totales generales ("TOTAL PUNTOS", "Total robot"...) y los grupos
# del editor van detras. Cuantos son ya no esta escrito aqui: lo dice el catalogo de
# totales (Catalogos.primer_grupo()), porque el usuario puede definir los que quiera y
# cada uno que anada corre los grupos un puesto.

# Arbitraje_TipoAccion: identificadores fijos de la base de datos.
ID_TIPO_ACCION = {"nulo": 0, "click": 1, "texto": 2, "bool": 3, "graf": 4}

# Arbitraje_Etiqueta lo define todo en una sola tabla: la posicion con guias del
# grupo (igual que las acciones), y el contenido con externa + tipo + valor. El
# ID_ETIQUETA lo elige el editor, porque la clave primaria es (ID_ETIQUETA,
# FK_GRUPO_ACCIONES) y para las externas el dato del partido se identifica por el
# campo valor, no por el identificador.


# Longitud maxima de las columnas de texto, tal y como estan declaradas en
# eurobot_ACCIONES.sql. Con el modo estricto de MariaDB (el de serie), pasarse de
# la longitud no trunca: da error y aborta la transaccion. Al ser CHARSET=utf16,
# el limite es en CARACTERES, asi que los acentos no cuentan doble.
LIMITES_TEXTO = {
    ("General_Resultado", "nombre"): 20,
    ("Partido_Lado", "nombre"): 9,
    ("Arbitraje_GrupoAcciones", "nombre"): 50,
    ("Arbitraje_ListaArbitros", "nombre"): 5,
    ("Arbitraje_ListaArbitros", "descripcion"): 20,
    ("Arbitraje_EstiloFuente", "descripcion"): 50,
    ("Arbitraje_EstiloFuente", "nombre_fuente"): 50,
    ("Arbitraje_EstiloFuente", "estilo_fuente"): 10,
    ("Arbitraje_EstiloFuente", "color_fuente"): 10,
    ("Arbitraje_TipoAcciones", "img_pos"): 1,
    ("Arbitraje_TipoAcciones", "directorio"): 256,
    ("Arbitraje_TipoAcciones", "accion"): 256,
    ("Arbitraje_ZonaAcciones", "zona"): 256,
    ("Arbitraje_Etiqueta", "valor"): 50,
    ("Arbitraje_Etiqueta", "justificacion"): 6,
}

def _n(v):
    """Los campos de coordenadas de la base de datos son INT."""
    return int(round(float(v)))


def _bool(v):
    return "TRUE " if v else "FALSE"


def _nulo(v):
    return "NULL" if v is None else str(int(v))


def _lado(m, inst):
    """FK_LADO de un parcial (Arbitraje_ZonaAcciones).

    La columna no admite nulo y el ID de un lado ya no puede ser 0, asi que un
    parcial sin lado (o con uno que se ha borrado del catalogo) se vuelca con el
    primero que haya. Si el lado no esta en el catalogo, _revisar() lo avisa aparte.
    """
    lado = inst.get("param", {}).get("lado")
    if lado is None:
        return int(m.catalogos.lado_defecto())
    return int(lado)


class Identificadores:
    """Asigna los identificadores de la base de datos a partir del modelo.

    Se hace en un paso previo porque las tablas se referencian entre si: los
    botones apuntan a las guias de control, los parciales a las de colocacion, y
    todos al grupo. La asignacion es determinista (por posicion o por orden en el
    modelo), de modo que volver a generar el mismo mapa da el mismo script.
    """

    def __init__(self, m):
        self.avisos = []
        self.grupo = {}         # id de grupo del modelo -> ID_GRUPO_ACCIONES
        self.guia_gx = {}       # id de guia vertical    -> ID_GUIA de Guia_GrupoX
        self.guia_gy = {}       # id de guia horizontal  -> ID_GUIA de Guia_GrupoY
        self.guia_cx = {}       # (grupo, guia)          -> ID_GUIA de Guia_ControlX
        self.guia_cy = {}       # (grupo, guia)          -> ID_GUIA de Guia_ControlY
        self.accion = {}        # id de control          -> ID_TIPO_ACCIONES
        self.zona = {}          # id de colocacion       -> ID_ZONA_ACCIONES
        self.etiqueta = {}      # id de control          -> ID_ETIQUETA (dentro del grupo)
        self._asignar(m)

    def _asignar(self, m):
        # --- Grupos, en el orden en que los creo el usuario, detras de los totales ---
        for n, t in enumerate(m.tipos, m.catalogos.primer_grupo()):
            self.grupo[t["id"]] = n

        # --- Guias de colocacion: numeradas por posicion, para que el script salga
        #     ordenado y sea facil de leer ---
        for orient, destino in (("v", self.guia_gx), ("h", self.guia_gy)):
            guias = sorted([g for g in m.guias_col if g["orient"] == orient],
                           key=lambda g: g["pos"])
            for n, g in enumerate(guias, 1):
                destino[g["id"]] = n

        # --- Guias de control: numeradas por distancia al origen, dentro de cada
        #     grupo (su clave primaria es ID_GUIA + FK_GRUPO_ACCIONES) ---
        for t in m.tipos:
            for orient, destino in (("v", self.guia_cx), ("h", self.guia_cy)):
                guias = sorted(m.guias_ctrl_tipo(t["id"], orient),
                               key=lambda g: g["rel"])
                for n, g in enumerate(guias, 1):
                    destino[(t["id"], g["id"])] = n

        # --- Botones: numerados dentro de cada grupo ---
        for t in m.tipos:
            n = 0
            for c in m.controles_tipo(t["id"]):
                if c["clase"] == "boton":
                    n += 1
                    self.accion[c["id"]] = n

        # --- Parciales: la clave primaria es (ID_ZONA, grupo, lado), asi que una
        #     pareja simetrica comparte ID_ZONA y se distingue por el lado ---
        for t in m.tipos:
            n = 0
            usados = set()
            for inst in m.instancias_tipo(t["id"]):
                par = inst.get("espejo")
                if par in self.zona:
                    ident = self.zona[par]
                else:
                    n += 1
                    ident = n
                lado = _lado(m, inst)
                if (ident, lado) in usados:
                    # Dos parciales del mismo grupo, mismo lado y mismo ID: la base
                    # de datos los rechazaria, asi que se le da uno nuevo.
                    n += 1
                    ident = n
                usados.add((ident, lado))
                self.zona[inst["id"]] = ident

        # --- Etiquetas: se numeran dentro de su grupo, porque la clave primaria es
        #     (ID_ETIQUETA, FK_GRUPO_ACCIONES). Una etiqueta es una sola fila aunque
        #     su grupo este colocado varias veces: la vista la reparte por todas las
        #     colocaciones, igual que hace con las acciones.
        for t in m.tipos:
            n = 0
            for c in m.controles_tipo(t["id"]):
                if c["clase"] != "etiqueta":
                    continue
                n += 1
                self.etiqueta[c["id"]] = n


# ===================================================================== TABLAS
def insert_grupos(m, ids):
    """Arbitraje_GrupoAcciones: primero los totales generales, que reservan los
    identificadores 1..N, y detras los grupos que ha dibujado el usuario.

    Los totales se escriben fila a fila desde el catalogo, y no con un
    SELECT ... FROM General_Resultado como en los scripts escritos a mano: la tabla
    puede traer filas de la base de datos de partidos que el editor no conoce, y
    entonces los identificadores de los grupos ya no cuadrarian.
    """
    totales = sorted(m.catalogos.totales, key=lambda t: t["id"])
    lineas = [SEPARADOR,
              "-- Los primeros grupos son los totales generales (General_Resultado):",
              "-- reservan los identificadores 1.." + str(len(totales)) + " y los grupos",
              "-- del editor empiezan justo después."]
    if totales:
        an = max(len(texto_sql(t["nombre"])) for t in totales)
        lineas += ["INSERT INTO Arbitraje_GrupoAcciones (",
                   "        ID_GRUPO_ACCIONES,",
                   "        nombre) VALUES"]
        lineas.append(",\n".join(f'    ({int(t["id"]):3d}, {texto_sql(t["nombre"]):<{an}})'
                                 for t in totales) + ";")
    lineas.append("")
    if not m.tipos:
        return lineas
    lineas += ["-- Y después, los grupos definidos con el editor.",
               "INSERT INTO Arbitraje_GrupoAcciones (",
               "        ID_GRUPO_ACCIONES,",
               "        nombre,",
               "        comun) VALUES"]
    ancho = max(len(texto_sql(t["nombre"])) for t in m.tipos)
    filas = [f'    ({ids.grupo[t["id"]]:3d}, {texto_sql(t["nombre"]):<{ancho}}, '
             f'{_bool(t.get("comun"))})' for t in m.tipos]
    return _unir(lineas, filas)


def insert_guias_grupo(m, ids):
    lineas = []
    for tabla, destino, orient in (("Guia_GrupoX", ids.guia_gx, "v"),
                                   ("Guia_GrupoY", ids.guia_gy, "h")):
        guias = sorted([g for g in m.guias_col if g["orient"] == orient],
                       key=lambda g: g["pos"])
        if not guias:
            continue
        lineas += [SEPARADOR,
                   f"INSERT INTO {tabla} (",
                   "        ID_GUIA,",
                   "        posicion) VALUES"]
        _unir(lineas, [f'    ({destino[g["id"]]:3d}, {_n(g["pos"]):5d})'
                       for g in guias])
    return lineas


def insert_guias_control(m, ids):
    lineas = []
    for tabla, destino, orient in (("Guia_ControlX", ids.guia_cx, "v"),
                                   ("Guia_ControlY", ids.guia_cy, "h")):
        filas = []
        for t in m.tipos:
            guias = sorted(m.guias_ctrl_tipo(t["id"], orient), key=lambda g: g["rel"])
            if not guias:
                continue
            if filas:
                filas.append("")   # una linea en blanco entre grupos
            for g in guias:
                filas.append(f'    ({ids.grupo[t["id"]]:3d}, '
                             f'{destino[(t["id"], g["id"])]:3d}, '
                             f'{_n(g["rel"]):5d})')
        if not filas:
            continue
        lineas += [SEPARADOR,
                   f"INSERT INTO {tabla} (",
                   "        FK_GRUPO_ACCIONES,",
                   "        ID_GUIA,",
                   "        posicion) VALUES"]
        _unir(lineas, filas)
    return lineas


def insert_acciones(m, ids, avisos):
    """Arbitraje_TipoAcciones: un registro por boton."""
    botones = [(t, c) for t in m.tipos for c in m.controles_tipo(t["id"])
               if c["clase"] == "boton"]
    if not botones:
        return []
    lineas = [SEPARADOR,
              "INSERT INTO Arbitraje_TipoAcciones (",
              "        ID_TIPO_ACCIONES,",
              "        FK_GRUPO_ACCIONES,",
              "        FK_ESTILO_FUENTE,",
              "        FK_TIPO_ACCION,",
              "        publicar,",
              "        valor_maximo,",
              "        img_pos,",
              "        directorio,",
              "        accion,",
              "        FK_GUIA_X1,",
              "        FK_GUIA_X2,",
              "        FK_GUIA_Y1,",
              "        FK_GUIA_Y2,",
              "        tipo_d) VALUES"]
    an_dir = max(len(texto_sql(c["param"].get("directorio", ""))) for _, c in botones)
    an_acc = max(len(texto_sql(c["param"].get("accion") or c.get("nombre", "")))
                 for _, c in botones)
    filas, grupo_ant = [], None
    for t, c in botones:
        p = c.get("param", {})
        tipo = p.get("tipo_accion", "click")
        if tipo not in ID_TIPO_ACCION:
            avisos.append(f"El botón '{c.get('nombre')}' tiene un tipo de acción "
                          f"desconocido ('{tipo}'); se ha guardado como 'click'.")
            tipo = "click"
        x1, x2 = _guias_ordenadas(m, ids.guia_cx, t["id"], c["v1"], c["v2"], "rel")
        y1, y2 = _guias_ordenadas(m, ids.guia_cy, t["id"], c["h1"], c["h2"], "rel")
        if grupo_ant is not None and t["id"] != grupo_ant:
            filas.append("")
        grupo_ant = t["id"]
        filas.append(
            f'    ({ids.accion[c["id"]]:3d}, {ids.grupo[t["id"]]:3d}, '
            f'{int(p.get("estilo", 0)):2d}, {ID_TIPO_ACCION[tipo]:2d}, '
            f'{_bool(p.get("publicar", True))}, '
            f'{_nulo(p.get("valor_maximo")):>4}, '
            f'{texto_sql(p.get("img_pos", "")):<4}, '
            f'{texto_sql(p.get("directorio", "")):<{an_dir}}, '
            f'{texto_sql(p.get("accion") or c.get("nombre", "")):<{an_acc}}, '
            f'{x1:3d}, {x2:3d}, {y1:3d}, {y2:3d}, '
            f'{int(p.get("tipo_d", 0)):3d})')
    return _unir(lineas, filas)


def _guias_ordenadas(m, destino, tid, id_a, id_b, campo):
    """Devuelve los ID_GUIA de las dos guias, la de menor coordenada primero."""
    a, b = m.guia_ctrl(id_a), m.guia_ctrl(id_b)
    if a[campo] > b[campo]:
        a, b = b, a
    return destino[(tid, a["id"])], destino[(tid, b["id"])]


def _unir(lineas, filas):
    """Cierra un INSERT juntando sus filas.

    Cada elemento de `filas` es el texto de una fila, o una tupla
    (texto, comentario), o "" para dejar una linea en blanco de separacion.
    La coma va pegada al final de la fila y ANTES del comentario: al reves
    quedaria dentro del comentario y el SQL no seria valido.
    """
    # Se normaliza primero para saber cual es la ultima fila (esa no lleva coma).
    normal = []
    for f in filas:
        fila, comentario = f if isinstance(f, tuple) else (f, "")
        normal.append((fila, comentario))
    ultima = max((i for i, (fila, _) in enumerate(normal) if fila), default=-1)

    partes = []
    for i, (fila, comentario) in enumerate(normal):
        if not fila:
            partes.append("")          # linea en blanco entre bloques
            continue
        # El punto y coma cierra la ultima fila, tambien antes del comentario.
        texto = fila + (";" if i == ultima else ",")
        if comentario:
            texto += f"    # {comentario}"
        partes.append(texto)
    lineas.append("\n".join(partes))
    lineas.append("")
    return lineas


def insert_total_grupos(m, ids):
    """Arbitraje_TotalGrupoAcciones: la etiqueta del total, una fila por GRUPO.

    La tabla es 1 a 1 con Arbitraje_GrupoAcciones y su ausencia es lo que dice que un
    grupo no muestra el total, asi que solo se escriben los grupos cuya etiqueta se ve
    en alguno de sus parciales. Dentro de cada grupo la geometria son guias de control
    suyas (las mismas coordenadas en todos, porque el rectangulo es unico para todo el
    mapa); que un parcial concreto la oculte se guarda en Arbitraje_ZonaAcciones.
    """
    grupos = m.grupos_con_total()
    if not grupos:
        return []
    lineas = [SEPARADOR,
              "-- Etiqueta con el total de puntos (Arbitraje_TotalGrupoAcciones): una",
              "-- fila por grupo, con las guías que la enmarcan dentro de ese grupo. Los",
              "-- grupos que no aparecen aquí no muestran el total en ninguna zona.",
              "INSERT INTO Arbitraje_TotalGrupoAcciones (",
              "        FK_GRUPO_ACCIONES,",
              "        FK_ESTILO_FUENTE,",
              "        FK_GUIA_X1,",
              "        FK_GUIA_X2,",
              "        FK_GUIA_Y1,",
              "        FK_GUIA_Y2,",
              "        zona_d) VALUES"]
    filas = []
    for t in grupos:
        tv1, tv2, th1, th2 = m.total["guias"][t["id"]]
        x1, x2 = _guias_ordenadas(m, ids.guia_cx, t["id"], tv1, tv2, "rel")
        y1, y2 = _guias_ordenadas(m, ids.guia_cy, t["id"], th1, th2, "rel")
        filas.append((f'    ({ids.grupo[t["id"]]:3d}, {int(m.estilo_total(t["id"])):2d}, '
                      f'{x1:3d}, {x2:3d}, {y1:3d}, {y2:3d}, '
                      f'{m.desp_total(t["id"]):3d})',
                      t["nombre"]))
    return _unir(lineas, filas)


def insert_zonas(m, ids):
    """Arbitraje_ZonaAcciones: un registro por parcial.

    De la etiqueta del total, el parcial solo aporta mostrar_puntos: la geometria y el
    estilo son del grupo (Arbitraje_TotalGrupoAcciones). La vista VistaAuxParciales
    exige las dos cosas, asi que un parcial con mostrar_puntos a TRUE cuyo grupo no
    tenga fila tampoco la dibuja.
    """
    if not m.instancias:
        return []
    lineas = [SEPARADOR,
              "-- mostrar_puntos dice si ESTA zona dibuja la etiqueta del total; dónde y",
              "-- con qué letra lo hace es del grupo (Arbitraje_TotalGrupoAcciones).",
              "INSERT INTO Arbitraje_ZonaAcciones (",
              "        ID_ZONA_ACCIONES,",
              "        FK_GRUPO_ACCIONES,",
              "        FK_LADO,",
              "        FK_ARBITRO,",
              "        zona,",
              "        valor_defecto,",
              "        reflejar_x,",
              "        FK_OFFSET_X,",
              "        FK_OFFSET_Y,",
              "        mostrar_puntos,",
              "        color_v) VALUES"]
    an_zona = max(len(texto_sql(i.get("nombre", ""))) for i in m.instancias)
    filas, grupo_ant = [], None
    for t in m.tipos:
        for inst in m.instancias_tipo(t["id"]):
            p = inst.get("param", {})
            if grupo_ant is not None and t["id"] != grupo_ant:
                filas.append("")
            grupo_ant = t["id"]
            filas.append(
                f'    ({ids.zona[inst["id"]]:3d}, {ids.grupo[t["id"]]:3d}, '
                f'{_lado(m, inst):2d}, {_nulo(p.get("arbitro")):>4}, '
                f'{texto_sql(inst.get("nombre", "")):<{an_zona}}, '
                f'{int(p.get("valor_defecto", 0)):4d}, '
                f'{_bool(inst.get("inv"))}, '
                f'{ids.guia_gx[inst["gv"]]:3d}, {ids.guia_gy[inst["gh"]]:3d}, '
                f'{_bool(m.muestra_total(inst))}, '
                f'{int(p.get("color_v", 255)):4d})')
    return _unir(lineas, filas)


def insert_etiquetas(m, ids, avisos):
    """Arbitraje_Etiqueta: una fila por etiqueta, no por colocacion.

    La tabla define la posicion con guias de control del grupo (como las acciones), y
    el contenido con tres campos: externa (de donde sale el valor), tipo (1 texto,
    2 imagen, 3 imagen web) y valor. La vista Arbitraje_VistaAuxEtiquetas la dibuja en
    cada colocacion del grupo, aplicando su desplazamiento y su reflejo, y toma el
    color de fondo del lado de esa colocacion.
    """
    etiquetas = [(t, c) for t in m.tipos for c in m.controles_tipo(t["id"])
                 if c["clase"] == "etiqueta"]
    if not etiquetas:
        return []

    lineas = [SEPARADOR,
              "-- Etiquetas (Arbitraje_Etiqueta): texto o imagen que se dibuja en cada",
              "-- colocacion del grupo. Con externa = FALSE, 'valor' es el contenido; con",
              "-- externa = TRUE es el identificador del dato en",
              "-- VistaPartido_EtiquetasPartido, que da un valor por lado.",
              "INSERT INTO Arbitraje_Etiqueta (",
              "        ID_ETIQUETA,",
              "        FK_GRUPO_ACCIONES,",
              "        FK_ESTILO_FUENTE,",
              "        FK_GUIA_X1,",
              "        FK_GUIA_X2,",
              "        FK_GUIA_Y1,",
              "        FK_GUIA_Y2,",
              "        externa,",
              "        tipo,",
              "        valor,",
              "        etiqueta_d,",
              "        color_v,",
              "        justificacion) VALUES"]

    an = max(len(texto_sql(c["contenido"].get("valor", ""))) for _, c in etiquetas)
    filas, grupo_ant = [], None
    for t, c in etiquetas:
        cont, p = c["contenido"], c.get("param", {})
        x1, x2 = _guias_ordenadas(m, ids.guia_cx, t["id"], c["v1"], c["v2"], "rel")
        y1, y2 = _guias_ordenadas(m, ids.guia_cy, t["id"], c["h1"], c["h2"], "rel")
        externa = bool(cont.get("externa"))
        if externa and len(str(cont.get("valor", ""))) > MAX_ID_PARTIDO:
            avisos.append(
                f"La etiqueta '{c.get('nombre')}' es externa y su identificador "
                f"'{cont.get('valor')}' pasa de {MAX_ID_PARTIDO} caracteres, que es el "
                f"maximo de VistaPartido_EtiquetasPartido: la aplicacion no encontrara "
                f"su valor.")
        if grupo_ant is not None and t["id"] != grupo_ant:
            filas.append(("", ""))
        grupo_ant = t["id"]
        filas.append((
            f'    ({ids.etiqueta[c["id"]]:3d}, {ids.grupo[t["id"]]:3d}, '
            f'{int(p.get("estilo", 0)):2d}, '
            f'{x1:3d}, {x2:3d}, {y1:3d}, {y2:3d}, '
            f'{_bool(externa):<5}, {int(cont.get("tipo", 1) or 1):2d}, '
            f'{texto_sql(cont.get("valor", "")):<{an}}, '
            f'{int(p.get("desp", 0)):3d}, {int(p.get("color_v", 255)):4d}, '
            f'{texto_sql(p.get("justif", "c"))})',
            c.get("nombre", "")))
    return _unir(lineas, filas)


# ==================================================================== SCRIPT
def script_edicion(m):
    """Script completo de datos de la edicion. Devuelve (texto, avisos)."""
    # La base de datos define la etiqueta del total con guias de control de cada
    # grupo, pero en el editor es un rectangulo unico: aqui se crean las guias que
    # falten, antes de repartir los identificadores.
    m.preparar_total()
    ids = Identificadores(m)
    avisos = list(ids.avisos)

    cab = [
        "START TRANSACTION;",
        "",
        "-- Datos de esta edición, generados por el editor de mapas.",
        "-- Se ejecuta después de eurobot_ACCIONES.sql (estructura) y de",
        "-- eurobot_DATOS.sql (datos comunes a todas las ediciones).",
        "--",
        "-- Los cuatro catálogos se vuelcan aquí. General_Resultado y Partido_Lado van con",
        "-- ON DUPLICATE KEY UPDATE porque la tabla puede venir ya creada y con datos",
        "-- (la trae la base de datos de partidos, o eurobot_DATOS.sql en la",
        "-- construcción autónoma): así se añaden los lados que falten y se actualizan",
        "-- el nombre y el color de los que ya estén, que es lo que cambia cada año.",
        "",
    ]
    cuerpo = []
    cuerpo += insert_totales(m.catalogos.totales) + [""]
    cuerpo += insert_lados(m.catalogos.lados) + [""]
    cuerpo += insert_arbitros(m.catalogos.arbitros) + [""]
    cuerpo += insert_estilos(m.catalogos.estilos) + [""]
    cuerpo += insert_grupos(m, ids) + [""]
    cuerpo += insert_guias_grupo(m, ids)
    cuerpo += insert_guias_control(m, ids)
    # Va aqui porque sus claves ajenas apuntan a las guias de control del grupo.
    cuerpo += insert_total_grupos(m, ids)
    cuerpo += insert_acciones(m, ids, avisos)
    cuerpo += insert_zonas(m, ids)
    cuerpo += insert_etiquetas(m, ids, avisos)

    # Comprobaciones de coherencia que la base de datos rechazaria.
    avisos += _revisar(m)
    avisos += _revisar_limites(m)
    return "\n".join(cab + cuerpo + ["COMMIT;", ""]), avisos


def _largo(avisos, tabla, columna, valor, de_quien):
    """Avisa si un texto no cabe en su columna."""
    limite = LIMITES_TEXTO.get((tabla, columna))
    texto = "" if valor is None else str(valor)
    if limite is not None and len(texto) > limite:
        avisos.append(f"{de_quien}: «{texto}» tiene {len(texto)} caracteres y "
                      f"{tabla}.{columna} solo admite {limite}. MariaDB en modo "
                      f"estricto rechazará el INSERT; acórtalo.")


def _solo_nombre(avisos, tabla, columna, valor, de_quien):
    """Las imagenes se guardan por su nombre: el directorio raiz lo pone la
    configuracion de la aplicacion de arbitraje, asi que una ruta escrita aqui no la
    encontraria ningun otro ordenador."""
    texto = "" if valor is None else str(valor)
    if "/" in texto or "\\" in texto:
        avisos.append(f"{de_quien}: {tabla}.{columna} guarda «{texto}», que es una "
                      f"ruta. Solo debe ir el nombre del archivo "
                      f"(«{os.path.basename(texto)}»), porque el directorio lo pone "
                      f"la configuración del arbitraje.")


def _negativo(avisos, tabla, columna, valor, de_quien):
    if valor is not None and int(valor) < 0:
        avisos.append(f"{de_quien}: {columna} = {valor}, pero {tabla}.{columna} es "
                      f"INT UNSIGNED y no admite negativos.")


def _revisar_limites(m):
    """Comprueba que todo cabe en su columna. Es lo que mas veces rompe un volcado,
    porque el editor no limita la longitud de lo que se teclea."""
    avisos = []
    for t in m.tipos:
        _largo(avisos, "Arbitraje_GrupoAcciones", "nombre", t["nombre"],
               f"El grupo '{t['nombre']}'")
    for t in m.catalogos.totales:
        _largo(avisos, "General_Resultado", "nombre", t.get("nombre"),
               f"El total general {t['id']}")
    for l in m.catalogos.lados:
        _largo(avisos, "Partido_Lado", "nombre", l.get("nombre"),
               f"El lado {l['id']}")
    for a in m.catalogos.arbitros:
        quien = f"El árbitro {a['id']}"
        _largo(avisos, "Arbitraje_ListaArbitros", "nombre", a.get("nombre"), quien)
        _largo(avisos, "Arbitraje_ListaArbitros", "descripcion",
               a.get("descripcion"), quien)
    for e in m.catalogos.estilos:
        quien = f"El estilo de fuente {e['id']}"
        for col in ("descripcion", "nombre_fuente", "estilo_fuente", "color_fuente"):
            _largo(avisos, "Arbitraje_EstiloFuente", col, e.get(col), quien)
        _negativo(avisos, "Arbitraje_EstiloFuente", "tamano_fuente",
                  e.get("tamano_fuente"), quien)
    for c in m.controles:
        p = c.get("param", {})
        quien = f"El elemento '{c.get('nombre')}'"
        if c["clase"] == "boton":
            _largo(avisos, "Arbitraje_TipoAcciones", "accion",
                   p.get("accion") or c.get("nombre"), quien)
            _largo(avisos, "Arbitraje_TipoAcciones", "directorio",
                   p.get("directorio"), quien)
            _solo_nombre(avisos, "Arbitraje_TipoAcciones", "directorio",
                         p.get("directorio"), quien)
            _largo(avisos, "Arbitraje_TipoAcciones", "img_pos", p.get("img_pos"), quien)
        elif c["clase"] == "etiqueta":
            _largo(avisos, "Arbitraje_Etiqueta", "justificacion",
                   p.get("justif"), quien)
            _negativo(avisos, "Arbitraje_Etiqueta", "color_v", p.get("color_v"), quien)
            # Ojo con las imagenes: aqui el limite es 50, no 256 como en los iconos de
            # los botones, y por eso solo se guarda el nombre del archivo.
            _largo(avisos, "Arbitraje_Etiqueta", "valor",
                   c["contenido"].get("valor"), quien)
            if c["contenido"].get("tipo") == 2 and not c["contenido"].get("externa"):
                _solo_nombre(avisos, "Arbitraje_Etiqueta", "valor",
                             c["contenido"].get("valor"), quien)
    for i in m.instancias:
        quien = f"El parcial '{i.get('nombre')}'"
        _largo(avisos, "Arbitraje_ZonaAcciones", "zona", i.get("nombre"), quien)
        _negativo(avisos, "Arbitraje_ZonaAcciones", "valor_defecto",
                  i.get("param", {}).get("valor_defecto"), quien)
    return avisos


def _revisar(m):
    """Avisos sobre cosas que el script no puede arreglar por si mismo."""
    # El ID de cada catalogo es la clave primaria de su tabla (INT UNSIGNED): con un 0
    # o un negativo, MariaDB rechaza el INSERT y con el todo el script.
    avisos = list(m.catalogos.ids_invalidos())
    for t in m.tipos:
        if not m.instancias_tipo(t["id"]):
            avisos.append(f"El grupo '{t['nombre']}' no está colocado en ningún sitio: "
                          f"no genera ningún parcial, así que sus elementos no "
                          f"aparecerán en la aplicación de arbitraje.")
    ids_estilo = {e["id"] for e in m.catalogos.estilos}
    ids_lado = {l["id"] for l in m.catalogos.lados}
    ids_arb = {a["id"] for a in m.catalogos.arbitros}
    for t in m.grupos_con_total():
        if t.get("total_estilo") not in ids_estilo:
            avisos.append(f"La etiqueta del total del grupo '{t['nombre']}' usa el "
                          f"estilo de fuente {t.get('total_estilo')}, que no está en "
                          f"el catálogo.")
    for c in m.controles:
        est = c.get("param", {}).get("estilo")
        if est not in ids_estilo:
            avisos.append(f"El elemento '{c.get('nombre')}' usa el estilo de fuente "
                          f"{est}, que no está en el catálogo.")
        if c["clase"] == "boton" and not (c["param"].get("accion")
                                          or c.get("nombre")):
            avisos.append("Hay un botón sin descripción de acción.")
    for i in m.instancias:
        p = i.get("param", {})
        if p.get("lado") not in ids_lado:
            avisos.append(f"El parcial '{i.get('nombre')}' usa el lado "
                          f"{p.get('lado')}, que no está en el catálogo.")
        if p.get("arbitro") is not None and p["arbitro"] not in ids_arb:
            avisos.append(f"El parcial '{i.get('nombre')}' usa el árbitro "
                          f"{p['arbitro']}, que no está en el catálogo.")
    nombres = [t["nombre"] for t in m.tipos]
    repes = sorted({n for n in nombres if nombres.count(n) > 1})
    if repes:
        avisos.append("Hay grupos con el mismo nombre: " + ", ".join(repes))
    return avisos


def guardar_edicion(m, ruta):
    texto, avisos = script_edicion(m)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto)
    return avisos