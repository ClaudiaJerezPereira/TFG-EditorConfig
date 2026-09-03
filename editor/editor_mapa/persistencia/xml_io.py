"""Lectura y escritura del XML de configuracion.

El XML es el formato de trabajo del editor y la fuente del futuro generador de
SQL: cada elemento se corresponde con una tabla de la base de datos. Modulo sin
dependencias de la interfaz.
"""
import os
from xml.etree import ElementTree as ET

_SI = ("1", "true", "True", "sí", "si")


def _contenido_etiqueta(el):
    """(externa, tipo, valor) de una etiqueta: los tres campos de Arbitraje_Etiqueta."""
    try:
        tipo = int(el.get("TIPO", 1) or 1)
    except ValueError:
        tipo = 1
    return ((el.get("EXTERNA", "0") in _SI), tipo if tipo in (1, 2, 3) else 1,
            el.get("VALOR", ""))


def _num(v):
    """Los valores enteros se escriben sin decimales, como en el formato de ejemplo."""
    v = float(v)
    return str(int(round(v))) if abs(v - round(v)) < 1e-6 else f"{v:.2f}"


# =============================================================== ESCRITURA
def serializar(m):
    """Construye el arbol XML completo a partir del modelo."""
    raiz = ET.Element("arbitraje")
    if m.ruta_mapa:
        raiz.append(ET.Comment(" Imagen del campo de juego "))
        ET.SubElement(raiz, "mapa", {"RUTA": m.ruta_mapa})

    _escribir_simetria(raiz, m)
    _escribir_catalogos(raiz, m)
    nom_col = m.nombres_guias_col()
    _escribir_guias_col(raiz, m, nom_col)
    _escribir_grupos(raiz, m)
    _escribir_total(raiz, m)
    _escribir_parciales(raiz, m, nom_col)
    return raiz


def _escribir_total(raiz, m):
    """La etiqueta del total es unica para todo el mapa, asi que va fuera de los
    grupos: X e Y son su esquina respecto al origen del grupo, en pixeles."""
    if not m.hay_total():
        return
    x, y, w, h = m.geom_total()
    raiz.append(ET.Comment(" Etiqueta con el total de puntos: la misma para todos los "
                           "grupos (X, Y, W, H respecto al origen de cada uno). Cada "
                           "parcial solo decide si la muestra "))
    ET.SubElement(raiz, "total", {"NOMBRE": m.total.get("nombre", "Total"),
                                  "X": _num(x), "Y": _num(y),
                                  "W": _num(w), "H": _num(h)})


def _escribir_simetria(raiz, m):
    eje = m.eje()
    raiz.append(ET.Comment(" Simetria horizontal: si esta activa, cada guia vertical y "
                           "cada parcial tienen su pareja al otro lado del eje. Los "
                           'elementos con ESPEJO="1" los ha creado la simetria '))
    ET.SubElement(raiz, "simetria", {"ACTIVA": "1" if m.simetria else "0",
                                     "EJE": _num(eje) if eje is not None else ""})


def _escribir_catalogos(raiz, m):
    cat_m = m.catalogos
    raiz.append(ET.Comment(" Catalogos: tablas de referencia (General_Resultado, "
                           "Partido_Lado, Arbitraje_ListaArbitros, "
                           "Arbitraje_EstiloFuente). Los cuatro se exportan a SQL. "
                           "Los <resultado> son los totales generales, y reservan los "
                           "primeros ID_GRUPO_ACCIONES "))
    cat = ET.SubElement(raiz, "catalogos")
    for t in cat_m.totales:
        ET.SubElement(cat, "resultado", {"ID": str(t["id"]),
                                         "NOMBRE": str(t.get("nombre", ""))})
    for l in cat_m.lados:
        ET.SubElement(cat, "lado", {"ID": str(l["id"]), "NOMBRE": str(l["nombre"]),
                                    "COLOR_H": _num(l.get("color_h", 0)),
                                    "COLOR_S": _num(l.get("color_s", 0))})
    for a in cat_m.arbitros:
        ET.SubElement(cat, "arbitro", {"ID": str(a["id"]), "NOMBRE": str(a["nombre"]),
                                       "DESCRIPCION": str(a.get("descripcion", ""))})
    for e in cat_m.estilos:
        ET.SubElement(cat, "estilo", {
            "ID": str(e["id"]), "DESCRIPCION": str(e.get("descripcion", "")),
            "NOMBRE_FUENTE": str(e.get("nombre_fuente", "Arial")),
            "ESTILO_FUENTE": str(e.get("estilo_fuente", "")),
            "TAMANO_FUENTE": str(int(e.get("tamano_fuente", 20))),
            "COLOR_FUENTE": str(e.get("color_fuente", "#000000"))})


def _escribir_guias_col(raiz, m, nom_col):
    raiz.append(ET.Comment(' Guias de grupo horizontales: nombre y coordenada "y" '))
    for g in sorted([g for g in m.guias_col if g["orient"] == "h"], key=lambda g: g["pos"]):
        ET.SubElement(raiz, "horizontal",
                      {"NOMBRE": nom_col[g["id"]], "POSICION": _num(g["pos"])})

    raiz.append(ET.Comment(' Guias de grupo verticales: nombre y coordenada "x" '))
    for g in sorted([g for g in m.guias_col if g["orient"] == "v"], key=lambda g: g["pos"]):
        attrs = {"NOMBRE": nom_col[g["id"]], "POSICION": _num(g["pos"])}
        if g.get("auto"):
            attrs["ESPEJO"] = "1"
        ET.SubElement(raiz, "vertical", attrs)


def _escribir_grupos(raiz, m):
    raiz.append(ET.Comment(" Grupos (Arbitraje_GrupoAcciones): guias propias y los "
                           "elementos que contienen (botones, etiquetas y total) "))
    for t in m.tipos:
        # TOTAL_ESTILO y TOTAL_D son los dos campos propios de
        # Arbitraje_TotalGrupoAcciones: con que letra y con que desplazamiento dibuja
        # este grupo la etiqueta del total. La geometria no esta aqui: es la del
        # elemento <total>, comun a todo el mapa.
        gel = ET.SubElement(raiz, "grupo", {
            "NOMBRE": t["nombre"],
            "COMUN": "1" if t.get("comun") else "0",
            "TOTAL_ESTILO": str(t.get("total_estilo", m.estilo_defecto())),
            "TOTAL_D": str(int(t.get("total_d", 0)))})
        nom_k = m.nombres_guias_ctrl(t["id"])
        for orient, tag in (("h", "horizontal"), ("v", "vertical")):
            for g in sorted(m.guias_ctrl_tipo(t["id"], orient), key=lambda g: g["rel"]):
                ET.SubElement(gel, tag,
                              {"NOMBRE": nom_k[g["id"]], "POSICION": _num(g["rel"])})
        for c in m.controles_tipo(t["id"]):
            ET.SubElement(gel, "control", _attrs_control(m, c, nom_k))


def _attrs_control(m, c, nom_k):
    # X1/Y1 son siempre la guia menor, para que el rectangulo quede normalizado.
    v1, v2 = sorted((c["v1"], c["v2"]), key=lambda i: m.guia_ctrl(i)["rel"])
    h1, h2 = sorted((c["h1"], c["h2"]), key=lambda i: m.guia_ctrl(i)["rel"])
    attrs = {"NOMBRE": c.get("nombre", c["id"]),
             "X1": nom_k[v1], "X2": nom_k[v2], "Y1": nom_k[h1], "Y2": nom_k[h2],
             "CLASE": c["clase"]}
    p = c.get("param", {})
    if c["clase"] == "etiqueta":
        # Arbitraje_Etiqueta. EXTERNA, TIPO y VALOR son los tres campos de la tabla que
        # deciden que se muestra; el lado ya no es de la etiqueta, sale del parcial.
        cont = c["contenido"]
        attrs["EXTERNA"] = "1" if cont.get("externa") else "0"
        attrs["TIPO"] = str(int(cont.get("tipo", 1) or 1))
        attrs["VALOR"] = str(cont.get("valor", ""))
        if cont.get("tam"):
            attrs["TAM"] = _num(cont["tam"])
        attrs["ESTILO"] = str(p.get("estilo", m.estilo_defecto()))
        attrs["JUSTIFICACION"] = p.get("justif", "c")
        attrs["COLOR_V"] = str(int(p.get("color_v", 255)))
        attrs["DESPLAZAMIENTO"] = str(int(p.get("desp", 0)))
        return attrs
    # Arbitraje_TipoAcciones
    attrs["TIPO_ACCION"] = p.get("tipo_accion", "click")
    attrs["ACCION"] = p.get("accion", "") or c.get("nombre", "")
    attrs["ESTILO"] = str(p.get("estilo", m.estilo_defecto()))
    attrs["PUBLICAR"] = "1" if p.get("publicar", True) else "0"
    vm = p.get("valor_maximo")
    attrs["VALOR_MAXIMO"] = "" if vm is None else str(int(vm))
    attrs["IMG_POS"] = p.get("img_pos", "")
    attrs["DIRECTORIO"] = p.get("directorio", "")
    attrs["DESPLAZAMIENTO"] = str(int(p.get("tipo_d", 0)))
    # No es un dato del arbitraje: es el valor con el que el editor dibuja el boton,
    # para poder comprobar como queda el texto.
    attrs["VALOR_MUESTRA"] = str(c["contenido"].get("valor", "0"))
    return attrs


def _escribir_parciales(raiz, m, nom_col):
    raiz.append(ET.Comment(
        " Parciales (Arbitraje_ZonaAcciones): colocacion de un grupo sobre la imagen. "
        "X e Y son las guias de grupo que hacen de origen (offset_x/offset_y). "
        "De la etiqueta del total, el parcial solo guarda MOSTRAR_PUNTOS: su "
        "geometria es la del elemento <total>, y su letra y su desplazamiento son "
        "del grupo "))
    for inst in m.instancias:
        p = inst.get("param", {})
        attrs = {
            "NOMBRE": inst.get("nombre", inst["id"]),
            "GRUPO": m.nombre_tipo(inst["tipo"]),
            "X": nom_col[inst["gv"]], "Y": nom_col[inst["gh"]],
            "REFLEJADO": "1" if inst.get("inv") else "0",
            "LADO": str(p.get("lado", m.catalogos.lado_defecto())),
            "VALOR_DEFECTO": str(int(p.get("valor_defecto", 0))),
            "COLOR_V": str(int(p.get("color_v", 255))),
            "MOSTRAR_PUNTOS": "1" if p.get("mostrar_puntos", True) else "0",
        }
        if p.get("arbitro") is not None:
            attrs["ARBITRO"] = str(p["arbitro"])
        if inst.get("auto"):
            attrs["ESPEJO"] = "1"
        ET.SubElement(raiz, "parcial", attrs)


def guardar(m, ruta):
    raiz = serializar(m)
    ET.indent(raiz, space="    ")
    ET.ElementTree(raiz).write(ruta, encoding="utf-8", xml_declaration=True)


# ================================================================== LECTURA
def cargar(m, raiz):
    """Reconstruye el modelo a partir del XML. Devuelve (ruta_mapa, errores)."""
    errores = []
    m.reiniciar()
    m.catalogos.reiniciar()

    _leer_simetria(m, raiz)
    _leer_catalogos(m, raiz, errores)
    col_por_nombre = _leer_guias_col(m, raiz, errores)
    tipo_por_nombre = _leer_grupos(m, raiz, errores)
    _leer_total(m, raiz)
    _leer_parciales(m, raiz, col_por_nombre, tipo_por_nombre, errores)

    # El emparejado de las simetricas lo hace el controlador, cuando ya conoce las
    # dimensiones de la imagen y, con ellas, el eje.
    mapa = raiz.find("mapa")
    return (mapa.get("RUTA") if mapa is not None else None), errores


def _leer_simetria(m, raiz):
    sim = raiz.find("simetria")
    if sim is None:
        return
    m.simetria = sim.get("ACTIVA", "0") in _SI
    try:
        m.eje_simetria = float(sim.get("EJE"))
    except (TypeError, ValueError):
        m.eje_simetria = None


def _leer_catalogos(m, raiz, errores=None):
    cat = raiz.find("catalogos")
    if cat is None:
        return

    def num(el, attr, d=0.0):
        try:
            return float(el.get(attr, d))
        except (TypeError, ValueError):
            return d

    totales = [{"id": int(num(e, "ID")), "nombre": e.get("NOMBRE", "")}
               for e in cat.findall("resultado")]
    lados = [{"id": int(num(e, "ID")), "nombre": e.get("NOMBRE", ""),
              "color_h": num(e, "COLOR_H"), "color_s": num(e, "COLOR_S")}
             for e in cat.findall("lado")]
    arbitros = [{"id": int(num(e, "ID")), "nombre": e.get("NOMBRE", ""),
                 "descripcion": e.get("DESCRIPCION", "")} for e in cat.findall("arbitro")]
    estilos = [{"id": int(num(e, "ID")), "descripcion": e.get("DESCRIPCION", ""),
                "nombre_fuente": e.get("NOMBRE_FUENTE", "Arial"),
                "estilo_fuente": e.get("ESTILO_FUENTE", ""),
                "tamano_fuente": int(num(e, "TAMANO_FUENTE", 20)),
                "color_fuente": e.get("COLOR_FUENTE", "#000000")}
               for e in cat.findall("estilo")]
    if totales:
        m.catalogos.totales = totales
        # El ID de los totales es su posicion: se renumera por si el archivo trae
        # huecos, que dejarian un identificador de grupo pisado o perdido.
        m.catalogos.renumerar_totales()
    if lados:
        m.catalogos.lados = lados
    if arbitros:
        m.catalogos.arbitros = arbitros
    if estilos:
        m.catalogos.estilos = estilos

    # Un XML guardado con una version anterior puede traer identificadores 0 o
    # negativos, incluido el antiguo lado 0 («Común»), que ya no es valido: ahora lo
    # comun es una marca del grupo (Arbitraje_GrupoAcciones.comun) y el ID de un lado
    # empieza en 1 como el de los demas catalogos. No se tocan (cambiarlos romperia
    # las referencias del propio archivo), pero se avisa para que se corrijan en el
    # editor antes de exportar el SQL.
    if errores is not None:
        errores += m.catalogos.ids_invalidos()


def _leer_guias_col(m, raiz, errores):
    col_por_nombre = {}
    for tag, orient in (("horizontal", "h"), ("vertical", "v")):
        for el in raiz.findall(tag):
            nombre = el.get("NOMBRE", "")
            try:
                pos = float(el.get("POSICION", "0"))
            except ValueError:
                errores.append(f"<{tag} NOMBRE='{nombre}'>: POSICION no es un número.")
                continue
            m.n_col += 1
            g = {"id": f"c{m.n_col}", "orient": orient, "pos": pos, "espejo": None,
                 "auto": el.get("ESPEJO", "0") in _SI}
            m.guias_col.append(g)
            col_por_nombre[nombre] = g["id"]
    return col_por_nombre


def _leer_grupos(m, raiz, errores):
    tipo_por_nombre = {}
    for gel in raiz.findall("grupo"):
        nombre = gel.get("NOMBRE", f"Grupo {len(m.tipos) + 1}")
        m.n_grupo += 1
        tid = f"G{m.n_grupo}"

        def entero_grupo(attr, d):
            try:
                return int(float(gel.get(attr)))
            except (TypeError, ValueError):
                return d

        # Arbitraje_TotalGrupoAcciones: con que letra y con que desplazamiento dibuja
        # este grupo la etiqueta del total.
        m.tipos.append({"id": tid, "nombre": nombre,
                        "comun": gel.get("COMUN", "0") in _SI,
                        "total_estilo": entero_grupo("TOTAL_ESTILO", m.estilo_defecto()),
                        "total_d": entero_grupo("TOTAL_D", 0)})
        tipo_por_nombre[nombre] = tid

        k_por_nombre = {}
        for tag, orient in (("horizontal", "h"), ("vertical", "v")):
            for el in gel.findall(tag):
                try:
                    rel = float(el.get("POSICION", "0"))
                except ValueError:
                    errores.append(f"Grupo '{nombre}': POSICION no válida en <{tag}>.")
                    continue
                m.n_ctrl += 1
                gk = {"id": f"k{m.n_ctrl}", "tipo": tid, "orient": orient, "rel": rel}
                m.guias_ctrl.append(gk)
                k_por_nombre[el.get("NOMBRE", "")] = gk["id"]
        # Las guias "cero" son imprescindibles: son los ejes del origen y el resto del
        # programa las da por hechas. Si el XML no las trae, se crean.
        for orient, pref in (("v", "CV"), ("h", "CH")):
            cero = next((g for g in m.guias_ctrl_tipo(tid, orient)
                         if abs(g["rel"]) < 1e-9), None)
            if cero is None:
                m.n_ctrl += 1
                cero = {"id": f"k{m.n_ctrl}", "tipo": tid, "orient": orient, "rel": 0.0}
                m.guias_ctrl.append(cero)
                k_por_nombre.setdefault(f"{pref}0", cero["id"])
                errores.append(f"Grupo '{nombre}': le faltaba el eje "
                               f"{'vertical' if orient == 'v' else 'horizontal'} del "
                               f"origen y se ha vuelto a crear.")
            cero["cero"] = True

        for el in gel.findall("control"):
            _leer_control(m, el, tid, nombre, k_por_nombre, errores)
    return tipo_por_nombre


def _leer_control(m, el, tid, nombre_grupo, k_por_nombre, errores):
    refs = [el.get(a, "") for a in ("X1", "X2", "Y1", "Y2")]
    if any(r not in k_por_nombre for r in refs):
        errores.append(f"Control '{el.get('NOMBRE', '?')}' del grupo '{nombre_grupo}': "
                       f"referencia a una guía que no existe.")
        return
    v1, v2, h1, h2 = (k_por_nombre[r] for r in refs)
    # El total no es un control de ningun grupo: es unico para todo el mapa y se lee
    # del elemento <total>.
    clase = el.get("CLASE")
    if clase not in ("boton", "etiqueta"):
        clase = "boton"

    def entero(attr, d=0):
        try:
            return int(float(el.get(attr)))
        except (TypeError, ValueError):
            return d

    externa, tipo, valor = _contenido_etiqueta(el)
    try:
        tam = float(el.get("TAM")) if el.get("TAM") else None
    except ValueError:
        tam = None

    if clase == "etiqueta":
        param = m.param_etiqueta()
        param.update({"estilo": entero("ESTILO", param["estilo"]),
                      "justif": (el.get("JUSTIFICACION") or "c").strip() or "c",
                      "color_v": entero("COLOR_V", 255),
                      "desp": entero("DESPLAZAMIENTO", 0)})
        contenido = {"externa": externa, "tipo": tipo, "valor": valor, "tam": tam}
    else:
        vm = el.get("VALOR_MAXIMO")
        param = m.param_accion()
        # VALOR_MUESTRA es el valor con el que el editor pinta el boton.
        contenido = {"modo": "texto",
                     "valor": el.get("VALOR_MUESTRA") or valor or "0", "tam": None}
        param.update({"tipo_accion": el.get("TIPO_ACCION", "click"),
                      "accion": el.get("ACCION", ""),
                      "estilo": entero("ESTILO", param["estilo"]),
                      "publicar": el.get("PUBLICAR", "1") in _SI,
                      "valor_maximo": (int(float(vm)) if vm not in (None, "") else None),
                      "img_pos": el.get("IMG_POS", ""),
                      # Solo el nombre del archivo: si el XML trae una ruta completa
                      # (se guardaban asi antes de restringir el "Examinar..." a la
                      # carpeta de graficos), se queda en el nombre, que es lo unico
                      # que la aplicacion de arbitraje sabe resolver.
                      "directorio": os.path.basename(el.get("DIRECTORIO", "")),
                      "tipo_d": entero("DESPLAZAMIENTO", 0)})

    m.n_control += 1
    m.controles.append({
        "id": f"e{m.n_control}", "tipo": tid,
        "nombre": el.get("NOMBRE", f"e{m.n_control}"),
        "v1": v1, "v2": v2, "h1": h1, "h2": h2, "clase": clase,
        "contenido": contenido, "param": param})


def _leer_parciales(m, raiz, col_por_nombre, tipo_por_nombre, errores):
    """Arbitraje_ZonaAcciones. De la etiqueta del total, el parcial solo guarda si la
    muestra (MOSTRAR_PUNTOS): su geometria es la del elemento <total> y su letra y su
    desplazamiento son del grupo (Arbitraje_TotalGrupoAcciones)."""
    for el in raiz.findall("parcial"):
        grupo = el.get("GRUPO", "")
        gx, gy = el.get("X", ""), el.get("Y", "")
        if grupo not in tipo_por_nombre:
            errores.append(f"Parcial '{el.get('NOMBRE', '?')}': el grupo '{grupo}' no existe.")
            continue
        if gx not in col_por_nombre or gy not in col_por_nombre:
            errores.append(f"Parcial '{el.get('NOMBRE', '?')}': guías de grupo "
                           f"'{gx}'/'{gy}' no encontradas.")
            continue

        def entero(attr, d=0):
            try:
                return int(float(el.get(attr)))
            except (TypeError, ValueError):
                return d

        param = m.param_zona()
        # Sin LADO en el archivo se queda el que trae param_zona (el primero del
        # catalogo): FK_LADO no admite nulo y el 0 ya no es un ID valido.
        param.update({"lado": entero("LADO", param["lado"]),
                      "valor_defecto": entero("VALOR_DEFECTO", 0),
                      "color_v": entero("COLOR_V", 255)})
        param["arbitro"] = entero("ARBITRO", None) \
            if el.get("ARBITRO") not in (None, "") else None
        tid_grupo = tipo_por_nombre[grupo]
        param["mostrar_puntos"] = el.get("MOSTRAR_PUNTOS", "1") in _SI

        m.n_inst += 1
        m.instancias.append({
            "id": f"i{m.n_inst}", "tipo": tid_grupo,
            "nombre": el.get("NOMBRE", f"i{m.n_inst}"),
            "gv": col_por_nombre[gx], "gh": col_por_nombre[gy],
            "inv": el.get("REFLEJADO", "0") in _SI,
            "espejo": None, "auto": el.get("ESPEJO", "0") in _SI,
            "param": param})


def _leer_total(m, raiz):
    """Etiqueta del total, unica para todo el mapa."""
    el = raiz.find("total")
    if el is None:
        return

    def num(attr):
        try:
            return float(el.get(attr, 0))
        except (TypeError, ValueError):
            return 0.0

    if num("W") <= 0 or num("H") <= 0:
        return
    m.poner_total(num("X"), num("Y"), num("W"), num("H"),
                  nombre=el.get("NOMBRE", "Total"), activar=False)