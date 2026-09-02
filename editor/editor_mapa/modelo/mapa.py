"""Modelo del mapa de arbitraje.

Contiene TODO el estado del documento y las operaciones que lo modifican, en
pixeles del mapa y sin ninguna dependencia de tkinter ni de PIL. La vista lee de
aqui para dibujar; el controlador llama a estos metodos para modificarlo.

Estructura de los datos (diccionarios, tal y como se guardan en el XML):

    guia_col   {id, orient:'v'/'h', pos, espejo, auto}
        Guia de colocacion, absoluta sobre la imagen -> Guia_GrupoX / Guia_GrupoY.

    tipo       {id, nombre, comun, total_estilo, total_d}
        Grupo -> Arbitraje_GrupoAcciones. Puede contener botones y etiquetas
        mezclados; el total es unico para todo el mapa (ver self.total).
        total_estilo y total_d son la fuente y el desplazamiento vertical con
        los que ESTE grupo dibuja la etiqueta del total, y son los dos campos
        propios de Arbitraje_TotalGrupoAcciones (FK_ESTILO_FUENTE y zona_d).

    guia_ctrl  {id, tipo, orient, rel}
        Guia de control, relativa al origen del grupo -> Guia_ControlX / ControlY.

    control    {id, tipo, nombre, v1, v2, h1, h2, clase, contenido, param}
        Elemento del grupo -> Arbitraje_TipoAcciones o Arbitraje_Etiqueta.

    instancia  {id, tipo, nombre, gv, gh, inv, espejo, auto, param}
        Colocacion de un grupo sobre la imagen -> Arbitraje_ZonaAcciones.
"""
import os

from .catalogos import Catalogos
from .constantes import TEXTO_TOTAL, TOL_SIMETRIA

# Carpeta de las imagenes de las etiquetas: la "graficos" del editor. Se calcula desde
# la ubicacion de este archivo (editor/editor_mapa/modelo/mapa.py), y no escrita a mano,
# para que el proyecto siga funcionando al moverlo o al abrirlo en otro ordenador.
CARPETA_GRAFICOS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "graficos")


class ModeloMapa:

    def __init__(self):
        self.catalogos = Catalogos()
        self.reiniciar()

    def reiniciar(self):
        self.guias_col = []
        self.tipos = []
        self.guias_ctrl = []
        self.controles = []
        self.instancias = []

        # Etiqueta del total: es UNICA para todo el mapa, no una por grupo. Guarda su
        # rectangulo respecto al origen del grupo (x, y, w, h en pixeles), de modo que
        # todos los grupos la dibujan en el mismo sitio relativo. Cada parcial solo
        # decide si la muestra o no.
        #
        # En la base de datos esto se reparte en dos sitios: la geometria va a
        # Arbitraje_TotalGrupoAcciones, con una fila por GRUPO (relacion 1 a 1 con
        # Arbitraje_GrupoAcciones); si un grupo no tiene fila, no muestra el total en
        # ninguna de sus zonas. Y cada parcial guarda en Arbitraje_ZonaAcciones el
        # campo mostrar_puntos, con el que puede ocultarlo solo en esa zona.
        self.total = None

        # Contadores para generar identificadores internos unicos.
        self.n_col = 0
        self.n_grupo = 0
        self.n_ctrl = 0
        self.n_inst = 0
        self.n_control = 0

        # Grupo y colocacion sobre los que se esta trabajando.
        self.tipo_activo = None
        self.instancia_activa = None

        # Elemento resaltado: ("col"/"ctrl"/"inst"/"control", id) o None. Es estado de
        # la edicion, no del documento (no se guarda en el XML), pero vive aqui para
        # que la vista pueda dibujarlo sin depender del controlador.
        self.seleccion = None

        # Imagen del campo: solo su ruta y sus dimensiones. El modelo no abre
        # imagenes; de eso se encarga la vista.
        self.ruta_mapa = None
        self.dim_mapa = None      # (ancho, alto) en pixeles

        # Simetria horizontal del campo.
        self.simetria = False
        self.eje_simetria = None  # solo se usa si no se conocen las dimensiones

    # ------------------------------------------------------------------ BUSQUEDAS
    def guia_col(self, ident):
        return next((g for g in self.guias_col if g["id"] == ident), None)

    def guia_ctrl(self, ident):
        return next((g for g in self.guias_ctrl if g["id"] == ident), None)

    def instancia(self, ident):
        return next((i for i in self.instancias if i["id"] == ident), None)

    def control(self, ident):
        if self.total is not None and ident == self.total["id"]:
            return self.total
        return next((c for c in self.controles if c["id"] == ident), None)

    def tipo(self, ident):
        return next((t for t in self.tipos if t["id"] == ident), None)

    def nombre_tipo(self, ident):
        t = self.tipo(ident)
        return t["nombre"] if t else "?"

    def tipo_por_nombre(self, nombre):
        return next((t for t in self.tipos if t["nombre"] == nombre), None)

    def guias_ctrl_tipo(self, tipo, orient=None):
        return [g for g in self.guias_ctrl
                if g["tipo"] == tipo and (orient is None or g["orient"] == orient)]

    def controles_tipo(self, tipo):
        return [c for c in self.controles if c["tipo"] == tipo]

    def instancias_tipo(self, tipo):
        return [i for i in self.instancias if i["tipo"] == tipo]

    def elementos_inst(self, inst):
        """Lo que se dibuja en una colocacion: los controles de su grupo y, si lo
        muestra, la etiqueta del total (que es del mapa, no del grupo)."""
        elems = [c for c in self.controles if c["tipo"] == inst["tipo"]]
        if self.muestra_total(inst):
            elems.append(self.total)
        return elems

    # --------------------------------------------------- PARAMETROS POR DEFECTO
    def estilo_defecto(self):
        return self.catalogos.estilo_defecto()

    def depurar_catalogos(self):
        """Quita las referencias a filas de catalogo que ya no existen.

        Al borrar un arbitro o un estilo, los parciales y los controles que lo usaban se
        quedaban apuntando a un identificador inexistente: el dialogo lo mostraba como
        "(ninguno)" pero el dato seguia ahi, y la base de datos lo rechazaria por la
        clave ajena. FK_ARBITRO admite nulo, asi que se vacia; el estilo y el lado son
        obligatorios, asi que se sustituyen por el de por defecto. Devuelve la lista de
        cambios para poder contarlos."""
        cambios = []
        arbitros = {a["id"] for a in self.catalogos.arbitros}
        estilos = {e["id"] for e in self.catalogos.estilos}
        lados = {l["id"] for l in self.catalogos.lados}
        estilo_def = self.estilo_defecto()
        lado_def = 0 if 0 in lados else (min(lados) if lados else 0)

        for i in self.instancias:
            p = i.setdefault("param", {})
            quien = f"El parcial '{i.get('nombre', i['id'])}'"
            if p.get("arbitro") is not None and p["arbitro"] not in arbitros:
                cambios.append(f"{quien} usaba el árbitro {p['arbitro']}, que ya no "
                               f"existe: se ha quedado sin árbitro.")
                p["arbitro"] = None
            if lados and p.get("lado") not in lados:
                cambios.append(f"{quien} usaba el lado {p.get('lado')}, que ya no "
                               f"existe: ahora usa el {lado_def}.")
                p["lado"] = lado_def

        for t in self.tipos:
            if estilos and t.get("total_estilo") not in estilos:
                cambios.append(f"El total del grupo '{t.get('nombre', t['id'])}' usaba "
                               f"el estilo {t.get('total_estilo')}, que ya no existe: "
                               f"ahora usa el {estilo_def}.")
                t["total_estilo"] = estilo_def

        for c in self.controles:
            p = c.setdefault("param", {})
            if estilos and p.get("estilo") not in estilos:
                cambios.append(f"El elemento '{c.get('nombre', c['id'])}' usaba el "
                               f"estilo {p.get('estilo')}, que ya no existe: ahora usa "
                               f"el {estilo_def}.")
                p["estilo"] = estilo_def
        return cambios

    def param_accion(self):
        # Arbitraje_TipoAcciones (los parametros de la accion ya no se reparten en
        # una segunda tabla: todo va aqui).
        return {"tipo_accion": "click", "accion": "", "estilo": self.estilo_defecto(),
                "publicar": True, "valor_maximo": None, "img_pos": "",
                "directorio": "", "tipo_d": 0}

    def param_etiqueta(self):
        # Arbitraje_Etiqueta. Ya no lleva lado: el color de fondo lo pone el parcial
        # que la dibuja (la vista une la etiqueta con Arbitraje_ZonaAcciones por el
        # grupo), y de la etiqueta solo sale color_v.
        return {"estilo": self.estilo_defecto(), "justif": "c",
                "color_v": 255, "desp": 0}

    def contenido_etiqueta(self):
        """Contenido de una etiqueta: externa dice de donde sale el valor y tipo que
        se hace con el (1 texto, 2 imagen, 3 imagen web). `tam` es del editor: fuerza
        el tamano de la letra en vez de ajustarla al hueco."""
        return {"externa": False, "tipo": 1, "valor": "", "tam": None}

    def carpeta_graficos(self):
        """Unica carpeta de la que se admiten imagenes para las etiquetas."""
        return CARPETA_GRAFICOS

    def ruta_grafico(self, nombre):
        """Ruta local de la imagen de una etiqueta.

        En la base de datos solo se guarda el nombre del archivo: el directorio raiz lo
        pone la configuracion de la aplicacion de arbitraje. El editor usa siempre
        `editor/graficos`, asi que una imagen que no este ahi no se dibuja (sale el
        interrogante de "no se puede abrir"), que es la pista de que hay que copiarla."""
        nombre = str(nombre or "").strip()
        if not nombre:
            return ""
        # Solo el nombre, aunque venga una ruta de un XML antiguo: la imagen se busca
        # siempre en la carpeta de graficos y en ningun otro sitio.
        return os.path.join(CARPETA_GRAFICOS, os.path.basename(nombre))

    def param_zona(self):
        # Arbitraje_ZonaAcciones. De la etiqueta del total, el parcial solo guarda
        # mostrar_puntos: la geometria y el estilo son del grupo
        # (Arbitraje_TotalGrupoAcciones), para que todos los parciales la dibujen
        # igual y en la misma posicion relativa.
        return {"lado": 0, "arbitro": None, "valor_defecto": 0, "color_v": 255,
                "mostrar_puntos": True}

    # ---------------------------------------------------------------- SELECCION
    def seleccionar(self, clase, ident):
        self.seleccion = (clase, ident)

    def limpiar_seleccion(self):
        self.seleccion = None

    def esta_seleccionado(self, clase, ident):
        return self.seleccion == (clase, ident)

    def seleccionado(self, clase):
        """Identificador seleccionado si es de esa clase, o None."""
        if self.seleccion and self.seleccion[0] == clase:
            return self.seleccion[1]
        return None

    def activar(self, inst_id):
        """Pone una colocacion (y su grupo) como activos. Devuelve True si ha
        cambiado: entonces hay que redibujar, porque cambian las guias visibles."""
        if inst_id is None or inst_id == self.instancia_activa:
            return False
        self.instancia_activa = inst_id
        inst = self.instancia(inst_id)
        if inst is not None:
            self.tipo_activo = inst["tipo"]
        return True

    # ------------------------------------------------------------------ GEOMETRIA
    def origen(self, inst):
        """Cruce de guias de colocacion que hace de origen del grupo."""
        return self.guia_col(inst["gv"])["pos"], self.guia_col(inst["gh"])["pos"]

    def pos_ctrl_abs(self, inst, gk):
        """Posicion absoluta de una guia de control en una colocacion concreta.
        Si la colocacion esta reflejada, las distancias horizontales van al reves."""
        ox, oy = self.origen(inst)
        if gk["orient"] == "v":
            return ox - gk["rel"] if inst.get("inv") else ox + gk["rel"]
        return oy + gk["rel"]

    def rect_control(self, inst, c):
        """Recuadro del control en pixeles del mapa, ya normalizado."""
        if c.get("clase") == "total":
            return self.rect_total(inst)
        xs = sorted((self.pos_ctrl_abs(inst, self.guia_ctrl(c["v1"])),
                     self.pos_ctrl_abs(inst, self.guia_ctrl(c["v2"]))))
        ys = sorted((self.pos_ctrl_abs(inst, self.guia_ctrl(c["h1"])),
                     self.pos_ctrl_abs(inst, self.guia_ctrl(c["h2"]))))
        return xs[0], ys[0], xs[1], ys[1]

    def tam_control(self, c):
        """Ancho y alto del control en pixeles del mapa (no dependen del zoom)."""
        if c.get("clase") == "total":
            return self.geom_total()[2], self.geom_total()[3]
        ancho = abs(self.guia_ctrl(c["v2"])["rel"] - self.guia_ctrl(c["v1"])["rel"])
        alto = abs(self.guia_ctrl(c["h2"])["rel"] - self.guia_ctrl(c["h1"])["rel"])
        return ancho, alto

    # ----------------------------------------------------- ETIQUETA DEL TOTAL
    # La etiqueta es la misma para todos los grupos, pero cuelga de guias de control
    # de verdad: cuatro por grupo, a la misma distancia del origen en todos. Asi se
    # mueve y se redimensiona arrastrando sus guias, igual que cualquier otro
    # elemento, y es ademas lo que pide Arbitraje_TotalGrupoAcciones, que guarda una
    # fila por grupo con FK_GUIA_X1/X2/Y1/Y2.
    #
    # Antes se guardaba aqui el rectangulo suelto (x, y, w, h) y las guias se
    # inventaban al exportar: por eso la etiqueta no se enganchaba a las guias y no
    # habia forma de cambiarle el tamano.
    def poner_total(self, x, y, ancho, alto, nombre=None, activar=True):
        """Define (o redefine) la etiqueta del total para todo el mapa.

        `activar` pone a True el "mostrar" de todos los parciales: es lo que se quiere
        cuando el usuario acaba de dibujarla (si no, no vería aparecer nada en los que
        estuvieran desmarcados). Al cargar un archivo va a False, porque entonces lo
        que manda es lo que traiga cada parcial."""
        self.total = {"id": "total", "clase": "total",
                      "nombre": nombre or (self.total or {}).get("nombre") or TEXTO_TOTAL,
                      "contenido": self.contenido_total(), "param": {},
                      "guias": {}}
        self.anclar_total(x, y, ancho, alto)
        for i in self.instancias:
            if activar:
                i.setdefault("param", {})["mostrar_puntos"] = True
            else:
                i.setdefault("param", {}).setdefault("mostrar_puntos", True)
        return self.total

    def anclar_total(self, x, y, ancho, alto):
        """Cuelga la etiqueta de cuatro guias de control en CADA grupo, creando las
        que falten. El rectangulo se guarda ademas suelto, pero solo como respaldo
        para el caso raro de que todavia no haya ningun grupo."""
        t = self.total
        t["x"], t["y"] = float(x), float(y)
        t["w"], t["h"] = float(ancho), float(alto)
        t["guias"] = {g["id"]: self.crear_guias_total(g["id"], t["x"], t["y"],
                                                      t["w"], t["h"])
                      for g in self.tipos}
        return t["guias"]

    def crear_guias_total(self, tipo, x, y, ancho, alto):
        """(v1, v2, h1, h2) de ese grupo para ese rectangulo, creando las que falten."""
        return (self.guia_ctrl_en(tipo, "v", x), self.guia_ctrl_en(tipo, "v", x + ancho),
                self.guia_ctrl_en(tipo, "h", y), self.guia_ctrl_en(tipo, "h", y + alto))

    def estilo_total(self, tid):
        """Arbitraje_TotalGrupoAcciones.FK_ESTILO_FUENTE de ese grupo."""
        t = self.tipo(tid) or {}
        return t.get("total_estilo", self.estilo_defecto())

    def desp_total(self, tid):
        """Arbitraje_TotalGrupoAcciones.zona_d de ese grupo."""
        t = self.tipo(tid) or {}
        try:
            return int(t.get("total_d", 0))
        except (TypeError, ValueError):
            return 0

    def quitar_total(self):
        self.total = None

    def hay_total(self):
        return self.total is not None

    def geom_total(self):
        """(x, y, ancho, alto) de la etiqueta del total respecto al origen del grupo.

        Se lee de sus guias, que es donde vive el dato desde que la etiqueta esta
        anclada: asi mover una guia cambia la etiqueta sola. Se recorren los grupos en
        orden para que el resultado no dependa del orden del diccionario; las cuatro
        guias estan a la misma distancia en todos (lo mantiene sincronizar_total).
        Sin total, todo a cero."""
        if self.total is None:
            return 0.0, 0.0, 0.0, 0.0
        guias = self.total.get("guias", {})
        for t in self.tipos:
            rect = self.rect_de_guias(guias.get(t["id"]))
            if rect is not None:
                return rect
        t = self.total
        return t.get("x", 0.0), t.get("y", 0.0), t.get("w", 0.0), t.get("h", 0.0)

    def rect_de_guias(self, guias):
        """(x, y, ancho, alto) que enmarcan cuatro guias de control, o None si falta
        alguna (por ejemplo si se ha borrado)."""
        if not guias or len(guias) != 4:
            return None
        v1, v2, h1, h2 = (self.guia_ctrl(i) for i in guias)
        if None in (v1, v2, h1, h2):
            return None
        xs = sorted((v1["rel"], v2["rel"]))
        ys = sorted((h1["rel"], h2["rel"]))
        return xs[0], ys[0], xs[1] - xs[0], ys[1] - ys[0]

    def guias_del_total(self):
        """Identificadores de todas las guias que enmarcan el total, en todos los
        grupos."""
        if self.total is None:
            return set()
        return {i for g in self.total.get("guias", {}).values() for i in g}

    def sincronizar_total(self, gk):
        """Si la guia movida es una de las que enmarcan el total, lleva su pareja de
        los demas grupos a la misma distancia del origen.

        El total es unico para todo el mapa, asi que sus cuatro guias tienen que
        estar en el mismo sitio en todos los grupos. Devuelve las guias movidas."""
        if self.total is None:
            return []
        guias = self.total.get("guias", {})
        propias = guias.get(gk.get("tipo"))
        if not propias or gk["id"] not in propias:
            return []
        idx = list(propias).index(gk["id"])
        movidas = []
        for tid, otras in guias.items():
            if tid == gk.get("tipo") or len(otras) != 4:
                continue
            otra = self.guia_ctrl(otras[idx])
            if otra is not None and otra["rel"] != gk["rel"]:
                otra["rel"] = float(gk["rel"])
                movidas.append(otra["id"])
        # El rectangulo de respaldo se deja al dia por si algun dia no quedan guias.
        (self.total["x"], self.total["y"],
         self.total["w"], self.total["h"]) = self.geom_total()
        return movidas

    def rect_total(self, inst):
        """Recuadro absoluto de la etiqueta del total en una colocacion. Si esta
        reflejada, se refleja igual que los controles."""
        ox, oy = self.origen(inst)
        x, y, w, h = self.geom_total()
        x1 = ox - x - w if inst.get("inv") else ox + x
        return x1, oy + y, x1 + w, oy + y + h

    def guias_total(self, tipo):
        """(v1, v2, h1, h2): guias de ese grupo que enmarcan el total. Si el grupo aun
        no las tiene (se ha creado despues que la etiqueta, o se ha borrado alguna),
        se crean donde toca."""
        if self.total is None:
            return None
        guias = self.total.setdefault("guias", {})
        if self.rect_de_guias(guias.get(tipo)) is None:
            x, y, w, h = self.geom_total()
            guias[tipo] = self.crear_guias_total(tipo, x, y, w, h)
        return guias[tipo]

    def grupos_con_total(self):
        """Grupos que llevan fila en Arbitraje_TotalGrupoAcciones.

        La tabla es 1 a 1 con Arbitraje_GrupoAcciones y su ausencia significa que ese
        grupo no muestra el total en ninguna de sus zonas, asi que hay fila cuando el
        mapa tiene etiqueta y al menos un parcial del grupo la muestra."""
        if self.total is None:
            return []
        return [t for t in self.tipos
                if any(self.muestra_total(i) for i in self.instancias_tipo(t["id"]))]

    def preparar_total(self):
        """Comprueba que cada grupo que va a tener fila en Arbitraje_TotalGrupoAcciones
        conserva sus cuatro guias. Ya no las inventa: la etiqueta esta anclada desde
        que se dibuja, y esto solo repone lo que falte."""
        if self.total is None:
            return {}
        for t in self.grupos_con_total():
            self.guias_total(t["id"])
        return self.total["guias"]

    def muestra_total(self, inst):
        """¿Este parcial dibuja la etiqueta del total? Solo si el mapa tiene una y el
        parcial no la ha desmarcado (Arbitraje_ZonaAcciones.mostrar_puntos)."""
        if self.total is None:
            return False
        return bool(inst.get("param", {}).get("mostrar_puntos", True))

    def hermanas(self, inst):
        """Colocaciones que comparten el mismo cruce de guias que esta."""
        return [i for i in self.instancias
                if i["gv"] == inst["gv"] and i["gh"] == inst["gh"]]

    def cercana(self, lista, coord, orient, pos_fn, margen):
        """Elemento de la lista cuya posicion queda a menos de `margen` de `coord`."""
        mejor, mejor_d = None, margen
        for g in lista:
            if g["orient"] != orient:
                continue
            d = abs(coord - pos_fn(g))
            if d <= mejor_d:
                mejor_d, mejor = d, g
        return mejor

    def guia_col_cercana(self, x, y, margen):
        """Par de guias de colocacion bajo un punto del mapa (o None, None)."""
        gv = self.cercana(self.guias_col, x, "v", lambda g: g["pos"], margen)
        gh = self.cercana(self.guias_col, y, "h", lambda g: g["pos"], margen)
        return gv, gh

    def cruce_ctrl(self, inst, x, y, margen):
        """Par de guias de control del grupo bajo un punto del mapa."""
        guias = self.guias_ctrl_tipo(inst["tipo"])
        gv = self.cercana(guias, x, "v", lambda g: self.pos_ctrl_abs(inst, g), margen)
        gh = self.cercana(guias, y, "h", lambda g: self.pos_ctrl_abs(inst, g), margen)
        return gv, gh

    # ------------------------------------------------------- GUIAS DE COLOCACION
    def anadir_guia_colocacion(self, orient, pos):
        """Anade una guia absoluta y, con la simetria activa, tambien su pareja."""
        self.n_col += 1
        g = {"id": f"c{self.n_col}", "orient": orient, "pos": float(pos),
             "espejo": None, "auto": False}
        self.guias_col.append(g)
        if self.simetria:
            self.crear_espejo_guia(g)
        return g

    def mover_guia_col(self, g, pos):
        g["pos"] = float(pos)
        self.sincronizar_espejo_guia(g)

    # ---------------------------------------------------------- GUIAS DE CONTROL
    def anadir_guia_control(self, inst, orient, x, y):
        """Anade una guia relativa al origen del grupo de esa colocacion."""
        ox, oy = self.origen(inst)
        if orient == "v":
            signo = -1 if inst.get("inv") else 1
            rel = signo * (x - ox)
        else:
            rel = y - oy
        self.n_ctrl += 1
        gk = {"id": f"k{self.n_ctrl}", "tipo": inst["tipo"], "orient": orient, "rel": rel}
        self.guias_ctrl.append(gk)
        return gk

    def mover_guia_ctrl(self, gk, inst, coord_abs):
        """Recoloca una guia de control a partir de una coordenada absoluta."""
        ox, oy = self.origen(inst)
        if gk["orient"] == "v":
            # Si la colocacion esta reflejada, pos_abs = ox - rel; hay que invertir
            # el signo para que la guia siga al cursor.
            signo = -1 if inst.get("inv") else 1
            return self.colocar_guia_ctrl(gk, signo * (coord_abs - ox))
        return self.colocar_guia_ctrl(gk, coord_abs - oy)

    def colocar_guia_ctrl(self, gk, rel):
        """Pone una guia de control a esa distancia del origen de su grupo.

        Es el unico sitio por el que se cambia `rel`, para que la etiqueta del total
        no se descuadre: si la guia es una de las suyas, las de los demas grupos la
        siguen. Devuelve las guias que ha arrastrado la sincronizacion."""
        gk["rel"] = float(rel)
        return self.sincronizar_total(gk)

    def guia_cero(self, tipo, orient):
        """Eje del origen del grupo: la guia de control que esta a distancia 0. La
        crea `crear_grupo` y el resto del programa da por hecho que existe (el
        generador de SQL la usa para la geometria degenerada del total)."""
        return next((g for g in self.guias_ctrl_tipo(tipo, orient)
                     if g.get("cero")), None)

    def es_guia_cero(self, ident):
        """Las guias cero no se mueven ni se borran: su posicion no es un dato libre,
        es el origen. El origen se mueve moviendo su guia de colocacion."""
        g = self.guia_ctrl(ident)
        return bool(g and g.get("cero"))

    def garantizar_guias_cero(self):
        """Cada grupo necesita sus dos ejes. Repara los mapas guardados antes de que
        las guias cero fueran intocables, donde pudieron moverse o borrarse."""
        arreglados = []
        for t in self.tipos:
            for orient in ("v", "h"):
                if self.guia_cero(t["id"], orient) is not None:
                    continue
                ident = self.guia_ctrl_en(t["id"], orient, 0.0)
                self.guia_ctrl(ident)["cero"] = True
                arreglados.append(t["nombre"])
        return sorted(set(arreglados))

    def guia_ctrl_en(self, tipo, orient, rel):
        """Guia de control del grupo a esa distancia del origen; si no existe, la crea.
        Se usa al convertir configuraciones antiguas."""
        for g in self.guias_ctrl_tipo(tipo, orient):
            if abs(g["rel"] - rel) < 1e-6:
                return g["id"]
        self.n_ctrl += 1
        self.guias_ctrl.append({"id": f"k{self.n_ctrl}", "tipo": tipo,
                                "orient": orient, "rel": float(rel)})
        return f"k{self.n_ctrl}"

    # ------------------------------------------------------ GRUPOS Y COLOCACIONES
    def crear_grupo(self, nombre, comun=False):
        """Crea el grupo con sus dos guias 'cero', que son los ejes de su origen."""
        self.n_grupo += 1
        tid = f"G{self.n_grupo}"
        # total_estilo y total_d son de Arbitraje_TotalGrupoAcciones: la etiqueta del
        # total tiene la misma geometria en todos los grupos, pero cada uno la dibuja
        # con su tipo de letra y su desplazamiento.
        self.tipos.append({"id": tid, "nombre": nombre, "comun": bool(comun),
                           "total_estilo": self.estilo_defecto(), "total_d": 0})
        for orient in ("v", "h"):
            self.n_ctrl += 1
            self.guias_ctrl.append({"id": f"k{self.n_ctrl}", "tipo": tid,
                                    "orient": orient, "rel": 0.0, "cero": True})
        # Un grupo creado despues que la etiqueta del total necesita tambien sus
        # cuatro guias: la etiqueta se dibuja igual en todos.
        if self.total is not None:
            self.guias_total(tid)
        self.tipo_activo = tid
        self.instancia_activa = None
        return tid

    def colocar_grupo(self, tid, gv, gh, nombre=None):
        """Coloca el grupo sobre un cruce de guias. Con la simetria activa, tambien
        coloca su reflejo. Devuelve (colocacion, colocacion_espejo o None)."""
        if nombre is None:
            nombre = f"{self.nombre_tipo(tid)} {len(self.instancias_tipo(tid)) + 1}"
        self.n_inst += 1
        inst = {"id": f"i{self.n_inst}", "tipo": tid, "nombre": nombre,
                "gv": gv["id"], "gh": gh["id"], "inv": False,
                "param": self.param_zona(), "espejo": None, "auto": False}
        self.instancias.append(inst)
        espejo = self.crear_espejo_inst(inst) if self.simetria else None
        self.instancia_activa = inst["id"]
        self.tipo_activo = tid
        return inst, espejo

    def renombrar_inst(self, inst, nombre):
        """Renombra una colocacion y arrastra a su espejo SI este conserva todavia el
        nombre automatico (el del original mas "(espejo)"). Si el usuario ya le habia
        puesto uno propio, se respeta: igual que el lado o el arbitro, cada mitad del
        campo puede querer el suyo. Devuelve el espejo si lo ha renombrado."""
        viejo = str(inst.get("nombre", "")).strip()
        inst["nombre"] = nombre
        par = self.instancia(inst.get("espejo"))
        if (par is not None and par.get("auto")
                and str(par.get("nombre", "")).strip() == f"{viejo} (espejo)".strip()):
            par["nombre"] = f"{nombre} (espejo)".strip()
            return par
        return None

    def reflejar(self, inst):
        """Alterna el reflejo de una colocacion; su pareja simetrica queda al reves."""
        inst["inv"] = not inst.get("inv", False)
        par = self.instancia(inst.get("espejo"))
        if par is not None:
            par["inv"] = not inst["inv"]
        return inst["inv"]

    # ------------------------------------------------------------------ CONTROLES
    def anadir_control(self, tid, clase, nombre, gv1, gv2, gh1, gh2,
                       contenido, param):
        """Anade un elemento al grupo: se replica en todas sus colocaciones. El total
        no pasa por aqui: no es de un grupo, sino del mapa (ver poner_total)."""
        self.n_control += 1
        c = {"id": f"e{self.n_control}", "tipo": tid, "nombre": nombre,
             "v1": gv1, "v2": gv2, "h1": gh1, "h2": gh2, "clase": clase,
             "contenido": contenido, "param": param}
        self.controles.append(c)
        return c

    def contenido_total(self):
        return {"modo": "texto", "valor": TEXTO_TOTAL, "tam": None}

    # ------------------------------------------------------------------- ELIMINAR
    def eliminar_guia_col(self, ident):
        """Elimina una guia de colocacion, su pareja simetrica y las colocaciones que
        cuelguen de ellas. Devuelve (n_guias, n_colocaciones) eliminadas."""
        g = self.guia_col(ident)
        par = self.guia_espejo(g)
        fuera = {ident} if par is None or par is g else {ident, par["id"]}
        dep = [i for i in self.instancias if i["gv"] in fuera or i["gh"] in fuera]
        ids = {i["id"] for i in dep}
        self.instancias = [i for i in self.instancias if i["id"] not in ids]
        self.guias_col = [x for x in self.guias_col if x["id"] not in fuera]
        for x in self.guias_col:
            if x.get("espejo") in fuera:
                x["espejo"] = None
        if self.instancia_activa in ids:
            self.instancia_activa = None
        self.limpiar_seleccion()
        return len(fuera), len(ids)

    def dependientes_guia_col(self, ident):
        """Colocaciones que se perderian al eliminar esa guia (y su simetrica)."""
        g = self.guia_col(ident)
        par = self.guia_espejo(g)
        fuera = {ident} if par is None or par is g else {ident, par["id"]}
        dep = [i for i in self.instancias if i["gv"] in fuera or i["gh"] in fuera]
        return len(fuera), dep

    def eliminar_instancia(self, ident):
        """Elimina una colocacion y su pareja simetrica."""
        inst = self.instancia(ident)
        fuera = {ident}
        if inst is not None and inst.get("espejo"):
            fuera.add(inst["espejo"])
        self.instancias = [i for i in self.instancias if i["id"] not in fuera]
        for i in self.instancias:
            if i.get("espejo") in fuera:
                i["espejo"] = None
        if self.instancia_activa in fuera:
            self.instancia_activa = None
        self.limpiar_seleccion()
        return len(fuera)

    def dependientes_guia_ctrl(self, ident):
        """Elementos que se quedarian sin geometria si se borrara esa guia. La
        etiqueta del total cuenta: desde que esta anclada, tambien cuelga de guias."""
        dep = [c for c in self.controles
               if ident in (c["v1"], c["v2"], c["h1"], c["h2"])]
        if self.total is not None and ident in self.guias_del_total():
            dep.append(self.total)
        return dep

    def eliminar_guia_ctrl(self, ident):
        """Elimina una guia de control y los elementos que dependen de ella. Las guias
        cero no se borran: son los ejes del origen del grupo."""
        if self.es_guia_cero(ident):
            return None
        n = len(self.dependientes_guia_ctrl(ident))
        if self.total is not None and ident in self.guias_del_total():
            # La etiqueta es unica para todo el mapa: sin una de sus guias se queda
            # sin geometria, asi que desaparece entera y no solo en este grupo.
            self.quitar_total()
        self.controles = [c for c in self.controles
                          if ident not in (c["v1"], c["v2"], c["h1"], c["h2"])]
        self.guias_ctrl = [g for g in self.guias_ctrl if g["id"] != ident]
        self.limpiar_seleccion()
        return n

    def eliminar_control(self, ident):
        if self.total is not None and ident == self.total["id"]:
            self.quitar_total()
        else:
            self.controles = [c for c in self.controles if c["id"] != ident]
        self.limpiar_seleccion()

    # ----------------------------------------------------------------- SIMETRIA
    # El campo de juego es simetrico respecto a su eje vertical: si la simetria
    # esta activa, cada guia vertical y cada colocacion tienen su pareja al otro
    # lado, y se mueven y se borran juntas.
    #   "espejo": id de la pareja (cada una apunta a la otra).
    #   "auto":   True si la creo la simetria. Al desactivarla solo se borran estas,
    #             no lo que habia dibujado el usuario a mano.
    def eje(self):
        """El eje es el centro de la imagen del campo. Si no se conocen sus
        dimensiones, se usa el eje que viniera guardado en el archivo."""
        if self.dim_mapa is not None:
            return self.dim_mapa[0] / 2.0
        return self.eje_simetria

    def espejo_pos(self, x):
        eje = self.eje()
        return None if eje is None else 2 * eje - x

    def es_central(self, g):
        """Una guia que cae sobre el eje es su propia simetrica: no necesita pareja."""
        eje = self.eje()
        return eje is not None and abs(g["pos"] - eje) <= TOL_SIMETRIA

    def guia_espejo(self, g):
        """Pareja de una guia vertical: ella misma si esta sobre el eje, o None si no
        tiene (simetria desactivada, guia horizontal o guia sin emparejar)."""
        if g is None or not self.simetria or g["orient"] != "v":
            return None
        if self.es_central(g):
            return g
        ident = g.get("espejo")
        return self.guia_col(ident) if ident else None

    def emparejar(self):
        """Empareja por geometria lo que YA es simetrico, sin crear nada. Asi, al
        activar la simetria sobre un diseno dibujado a mano en los dos lados, no se
        duplica nada."""
        for g in self.guias_col:
            g["espejo"] = None
        # De izquierda a derecha, para que la guia izquierda haga de referencia.
        libres = sorted([g for g in self.guias_col
                         if g["orient"] == "v" and not self.es_central(g)],
                        key=lambda g: g["pos"])
        for i, g in enumerate(libres):
            if g.get("espejo"):
                continue
            objetivo = self.espejo_pos(g["pos"])
            for h in libres[i + 1:]:
                if not h.get("espejo") and abs(h["pos"] - objetivo) <= TOL_SIMETRIA:
                    g["espejo"], h["espejo"] = h["id"], g["id"]
                    # Si estaban puestas "a ojo", se ajusta a la simetria exacta.
                    h["pos"] = objetivo
                    break

        # Dos colocaciones son pareja si son del mismo grupo, cuelgan de la misma
        # guia horizontal, de guias verticales simetricas, y una esta reflejada
        # respecto de la otra.
        for i in self.instancias:
            i["espejo"] = None
        libres = list(self.instancias)
        for n, a in enumerate(libres):
            if a.get("espejo"):
                continue
            par = self.guia_espejo(self.guia_col(a["gv"]))
            if par is None:
                continue
            for b in libres[n + 1:]:
                if (not b.get("espejo") and b["tipo"] == a["tipo"] and b["gh"] == a["gh"]
                        and b["gv"] == par["id"]
                        and bool(b.get("inv")) != bool(a.get("inv"))):
                    a["espejo"], b["espejo"] = b["id"], a["id"]
                    break

    def crear_espejo_guia(self, g):
        """Crea la guia simetrica de una vertical que aun no tiene pareja."""
        if g["orient"] != "v" or self.es_central(g) or g.get("espejo"):
            return None
        pos = self.espejo_pos(g["pos"])
        if pos is None:
            return None
        self.n_col += 1
        esp = {"id": f"c{self.n_col}", "orient": "v", "pos": pos,
               "espejo": g["id"], "auto": True}
        g["espejo"] = esp["id"]
        self.guias_col.append(esp)
        return esp

    def crear_espejo_inst(self, inst):
        """Crea la colocacion simetrica: mismo grupo, misma guia horizontal, la guia
        vertical de enfrente y reflejada. Los parametros (lado, arbitro, color...) se
        copian, pero luego pueden editarse por separado: en el campo real cada lado
        tiene su color y su arbitro."""
        if inst.get("espejo"):
            return None
        par = self.guia_espejo(self.guia_col(inst["gv"]))
        if par is None:
            return None
        self.n_inst += 1
        esp = {"id": f"i{self.n_inst}", "tipo": inst["tipo"],
               # "(espejo)" y no "(reflejado)": lo que la distingue de su pareja es
               # que la ha creado la simetria, no que este del reves.
               "nombre": f'{inst.get("nombre", "")} (espejo)'.strip(),
               "gv": par["id"], "gh": inst["gh"],
               "inv": not bool(inst.get("inv")), "param": dict(inst.get("param", {})),
               "espejo": inst["id"], "auto": True}
        inst["espejo"] = esp["id"]
        self.instancias.append(esp)
        return esp

    def aplicar_simetria(self):
        """Empareja lo que ya sea simetrico y crea lo que falte. Devuelve cuantas
        guias y cuantas colocaciones se han anadido."""
        self.emparejar()
        nuevas_g = [g for g in list(self.guias_col) if self.crear_espejo_guia(g)]
        # Las colocaciones se emparejan despues, para que puedan usar las guias que
        # se acaban de crear.
        nuevas_i = [i for i in list(self.instancias) if self.crear_espejo_inst(i)]
        return len(nuevas_g), len(nuevas_i)

    def contar_automaticos(self):
        return (sum(1 for g in self.guias_col if g.get("auto")),
                sum(1 for i in self.instancias if i.get("auto")))

    def quitar_simetria(self):
        """Solo desaparece lo que creo la simetria; lo dibujado a mano se conserva."""
        self.simetria = False
        fuera = {g["id"] for g in self.guias_col if g.get("auto")}
        self.guias_col = [g for g in self.guias_col if g["id"] not in fuera]
        self.instancias = [i for i in self.instancias
                           if not i.get("auto") and i["gv"] not in fuera
                           and i["gh"] not in fuera]
        for g in self.guias_col:
            g["espejo"] = None
            g["auto"] = False
        for i in self.instancias:
            i["espejo"] = None
            i["auto"] = False
        if not any(i["id"] == self.instancia_activa for i in self.instancias):
            self.instancia_activa = None
        self.limpiar_seleccion()

    def sincronizar_espejo_guia(self, g):
        """Al mover una guia, su pareja se mueve al otro lado del eje."""
        par = self.guia_espejo(g)
        if par is not None and par is not g:
            par["pos"] = self.espejo_pos(g["pos"])

    # ------------------------------------------------------------------ NOMBRES
    def nombres_guias_col(self):
        """Asigna GV1..GVn y GH1..GHn ordenando por posicion, como en el XML."""
        nombres = {}
        for orient, pref in (("h", "GH"), ("v", "GV")):
            guias = sorted([g for g in self.guias_col if g["orient"] == orient],
                           key=lambda g: g["pos"])
            for n, g in enumerate(guias, 1):
                nombres[g["id"]] = f"{pref}{n}"
        return nombres

    def nombres_guias_ctrl(self, tid):
        """La guia 'cero' siempre se llama CV0/CH0; las demas se numeran por distancia."""
        nombres = {}
        for orient, pref in (("h", "CH"), ("v", "CV")):
            guias = sorted(self.guias_ctrl_tipo(tid, orient), key=lambda g: g["rel"])
            n = 1
            for g in guias:
                if abs(g["rel"]) < 1e-9:
                    nombres[g["id"]] = f"{pref}0"
                else:
                    nombres[g["id"]] = f"{pref}{n}"
                    n += 1
        return nombres

    # ------------------------------------------------------------------- RESUMEN
    def resumen(self):
        return (f"{len(self.guias_col)} guías de grupo, {len(self.tipos)} grupo(s), "
                f"{len(self.controles)} control(es), {len(self.instancias)} parcial(es).")

    def vacio(self):
        return not self.guias_col and not self.tipos