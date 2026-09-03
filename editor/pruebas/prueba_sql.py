"""Comprueba que el SQL generado es estructuralmente correcto.

No hay servidor MySQL en este entorno, asi que se valida a mano lo que mas
facilmente se rompe al generar texto: que cada INSERT tenga tantos valores por
fila como columnas declara, que los parentesis y las comillas cierren, que las
comas y los puntos y coma no acaben dentro de un comentario, y que las claves
ajenas apunten a filas que existen.
"""
import re
import sys

from rutas import XML_EJEMPLO   # noqa: F401  (deja el paquete importable)

from editor_mapa.persistencia import sql_mapa   # noqa: E402


def sin_comentario(linea):
    """Quita el comentario final, respetando las comillas."""
    fuera, comilla = [], False
    i = 0
    while i < len(linea):
        c = linea[i]
        if c == "'":
            if comilla and i + 1 < len(linea) and linea[i + 1] == "'":
                fuera.append("''")
                i += 2
                continue
            comilla = not comilla
        if not comilla and (c == "#" or linea[i:i + 2] == "--"):
            break
        fuera.append(c)
        i += 1
    return "".join(fuera)


def partir_valores(fila):
    """Separa los valores de una fila '( a, b, 'c,d' )' respetando las comillas."""
    fila = fila.strip()
    assert fila.startswith("(") and fila.endswith(")"), fila
    dentro = fila[1:-1]
    valores, actual, comilla = [], "", False
    i = 0
    while i < len(dentro):
        c = dentro[i]
        if c == "'":
            if comilla and i + 1 < len(dentro) and dentro[i + 1] == "'":
                actual += "''"
                i += 2
                continue
            comilla = not comilla
            actual += c
        elif c == "," and not comilla:
            valores.append(actual.strip())
            actual = ""
        else:
            actual += c
        i += 1
    valores.append(actual.strip())
    return valores


def filas_de(cuerpo):
    """Extrae las filas '(...)' de un VALUES, respetando parentesis y comillas
    dentro de los textos (un nombre como 'Despensa 1 (reflejado)' lleva los suyos)."""
    filas, actual, nivel, comilla = [], "", 0, False
    i = 0
    while i < len(cuerpo):
        c = cuerpo[i]
        if c == "'":
            if comilla and i + 1 < len(cuerpo) and cuerpo[i + 1] == "'":
                actual += "''"
                i += 2
                continue
            comilla = not comilla
        if not comilla:
            if c == "(":
                nivel += 1
                if nivel == 1:
                    actual = ""
                    i += 1
                    continue
            elif c == ")":
                nivel -= 1
                if nivel == 0:
                    filas.append("(" + actual + ")")
                    actual = ""
                    i += 1
                    continue
        if nivel >= 1:
            actual += c
        i += 1
    return filas


def sentencias(sql):
    """Parte el script en sentencias, quitando comentarios y lineas vacias."""
    limpio = "\n".join(sin_comentario(l).rstrip() for l in sql.split("\n"))
    for trozo in limpio.split(";"):
        if trozo.strip():
            yield trozo.strip() + ";"


def revisar(sql):
    errores = []
    tablas = {}     # tabla -> [filas de valores]

    # 1) Comillas y parentesis equilibrados en todo el script (sin comentarios).
    limpio = "".join(sin_comentario(l) for l in sql.split("\n"))
    if limpio.count("'") % 2:
        errores.append("Hay un número impar de comillas simples.")
    if limpio.count("(") != limpio.count(")"):
        errores.append(f"Paréntesis descompensados: {limpio.count('(')} abiertos, "
                       f"{limpio.count(')')} cerrados.")

    # 2) Ni comas ni puntos y coma dentro de un comentario.
    for n, linea in enumerate(sql.split("\n"), 1):
        pos = linea.find("#")
        if pos >= 0 and pos > len(sin_comentario(linea)) - 1:
            resto = linea[pos:]
            if "," in resto or ";" in resto:
                errores.append(f"Línea {n}: hay una coma o un punto y coma dentro "
                               f"del comentario: {linea.strip()}")

    # 3) Cada INSERT ... VALUES: tantos valores como columnas.
    for sent in sentencias(sql):
        m = re.match(r"INSERT INTO (\w+)\s*\((.*?)\)\s*VALUES(.*)", sent,
                     re.S | re.I)
        if not m:
            continue
        tabla, cols, cuerpo = m.group(1), m.group(2), m.group(3)
        # Partido_Lado se vuelca con ON DUPLICATE KEY UPDATE, porque la tabla puede
        # venir ya con datos. Su cola lleva VALUES(nombre), que no son filas.
        cuerpo = re.split(r"ON DUPLICATE KEY UPDATE", cuerpo, flags=re.I)[0]
        columnas = [c.strip() for c in cols.split(",") if c.strip()]
        filas = filas_de(cuerpo)
        tablas.setdefault(tabla, [])
        for fila in filas:
            valores = partir_valores(fila.replace("\n", " "))
            if len(valores) != len(columnas):
                errores.append(f"{tabla}: una fila tiene {len(valores)} valores y la "
                               f"tabla declara {len(columnas)} columnas -> {fila.strip()}")
            tablas[tabla].append(dict(zip(columnas, valores)))

    # 4) Claves ajenas: que apunten a filas que se han insertado antes.
    grupos = {f["ID_GRUPO_ACCIONES"] for f in tablas.get("Arbitraje_GrupoAcciones", [])}
    gx = {f["ID_GUIA"] for f in tablas.get("Guia_GrupoX", [])}
    gy = {f["ID_GUIA"] for f in tablas.get("Guia_GrupoY", [])}
    cx = {(f["FK_GRUPO_ACCIONES"], f["ID_GUIA"]) for f in tablas.get("Guia_ControlX", [])}
    cy = {(f["FK_GRUPO_ACCIONES"], f["ID_GUIA"]) for f in tablas.get("Guia_ControlY", [])}
    estilos = {f["ID_ESTILO_FUENTE"] for f in tablas.get("Arbitraje_EstiloFuente", [])}
    arbitros = {f["ID_ARBITRO"] for f in tablas.get("Arbitraje_ListaArbitros", [])}
    lados = {f["ID_LADO"] for f in tablas.get("Partido_Lado", [])}

    def comprobar(tabla, campo, validos, etiqueta, salta_null=False):
        for f in tablas.get(tabla, []):
            v = f.get(campo)
            if v is None or (salta_null and v.upper() == "NULL"):
                continue
            if v not in validos:
                errores.append(f"{tabla}.{campo} = {v} no existe en {etiqueta}.")

    for tabla in ("Guia_ControlX", "Guia_ControlY", "Arbitraje_TipoAcciones",
                  "Arbitraje_ZonaAcciones", "Arbitraje_TotalGrupoAcciones"):
        comprobar(tabla, "FK_GRUPO_ACCIONES", grupos, "Arbitraje_GrupoAcciones")
    comprobar("Arbitraje_ZonaAcciones", "FK_OFFSET_X", gx, "Guia_GrupoX")
    comprobar("Arbitraje_ZonaAcciones", "FK_OFFSET_Y", gy, "Guia_GrupoY")
    comprobar("Arbitraje_TipoAcciones", "FK_ESTILO_FUENTE", estilos,
              "Arbitraje_EstiloFuente")
    comprobar("Arbitraje_TotalGrupoAcciones", "FK_ESTILO_FUENTE", estilos,
              "Arbitraje_EstiloFuente")
    comprobar("Arbitraje_Etiqueta", "FK_ESTILO_FUENTE", estilos,
              "Arbitraje_EstiloFuente")
    comprobar("Arbitraje_ZonaAcciones", "FK_ARBITRO", arbitros,
              "Arbitraje_ListaArbitros", salta_null=True)
    comprobar("Arbitraje_ZonaAcciones", "FK_LADO", lados, "Partido_Lado")
    # La etiqueta del total ya no lleva guías en la zona: son del grupo.
    for f in tablas.get("Arbitraje_ZonaAcciones", []):
        assert "FK_GUIA_X1" not in f, \
            "las guías del total salieron de ZonaAcciones al pasar a TotalGrupoAcciones"
    for tabla in ("Arbitraje_TipoAcciones", "Arbitraje_TotalGrupoAcciones"):
        for f in tablas.get(tabla, []):
            g = f["FK_GRUPO_ACCIONES"]
            for campo, validos in (("FK_GUIA_X1", cx), ("FK_GUIA_X2", cx),
                                   ("FK_GUIA_Y1", cy), ("FK_GUIA_Y2", cy)):
                if (g, f[campo]) not in validos:
                    errores.append(f"{tabla}.{campo} = {f[campo]} no existe como guía "
                                   f"del grupo {g}.")

    # 5) Claves primarias sin repetir.
    for tabla, clave in (("Arbitraje_GrupoAcciones", ("ID_GRUPO_ACCIONES",)),
                         ("Guia_GrupoX", ("ID_GUIA",)),
                         ("Guia_GrupoY", ("ID_GUIA",)),
                         ("Guia_ControlX", ("ID_GUIA", "FK_GRUPO_ACCIONES")),
                         ("Guia_ControlY", ("ID_GUIA", "FK_GRUPO_ACCIONES")),
                         ("Arbitraje_TipoAcciones", ("ID_TIPO_ACCIONES",
                                                     "FK_GRUPO_ACCIONES")),
                         ("Arbitraje_ZonaAcciones", ("ID_ZONA_ACCIONES",
                                                     "FK_GRUPO_ACCIONES", "FK_LADO")),
                         ("Arbitraje_Etiqueta", ("ID_ETIQUETA",
                                                 "FK_GRUPO_ACCIONES")),
                         ("Arbitraje_TotalGrupoAcciones", ("FK_GRUPO_ACCIONES",)),
                         ("Arbitraje_EstiloFuente", ("ID_ESTILO_FUENTE",)),
                         ("Arbitraje_ListaArbitros", ("ID_ARBITRO",))):
        vistas = set()
        for f in tablas.get(tabla, []):
            if not all(c in f for c in clave):
                continue
            k = tuple(f[c] for c in clave)
            if k in vistas:
                errores.append(f"{tabla}: clave primaria repetida {k}.")
            vistas.add(k)
    return errores, tablas


def main():
    import ejemplo_mapa
    m = ejemplo_mapa.mapa()
    sql, avisos = sql_mapa.script_edicion(m)
    errores, tablas = revisar(sql)

    print("Filas generadas por tabla:")
    for t, filas in tablas.items():
        print(f"   {t:<28} {len(filas)}")
    print(f"\nAvisos del generador: {avisos or 'ninguno'}")
    if errores:
        print("\nERRORES DE ESTRUCTURA:")
        for e in errores:
            print("  -", e)
        return 1
    print("\nEstructura correcta: columnas, paréntesis, comillas, claves ajenas y "
          "primarias.")

    # --- Catálogos: qué se vuelca y cómo se escapan los textos ---
    assert "INSERT INTO Partido_Lado" in sql, "los lados también se vuelcan"
    assert "ON DUPLICATE KEY UPDATE" in sql, \
        "Partido_Lado puede venir ya con datos: el volcado tiene que actualizarla"
    assert "INSERT INTO Arbitraje_ListaArbitros" in sql
    assert "INSERT INTO Arbitraje_EstiloFuente" in sql
    lados_sql = {f["ID_LADO"] for f in tablas["Partido_Lado"]}
    assert lados_sql == {"1", "2"}, lados_sql
    assert "0" not in lados_sql, "en Partido_Lado el ID empieza en 1, como en el resto"
    print("Catálogos: se vuelcan los cuatro, y Partido_Lado sin romper si ya existe.")

    # --- Los lados no son 1 y 2 por obligación: ni el número ni la cantidad ---
    # Cuatro robots enfrentándose a la vez son cuatro lados, y sus identificadores no
    # tienen que ir seguidos: lo común (que al tocar una acción se refresquen todos
    # los parciales) es una marca del GRUPO, no un lado reservado.
    m_lados = ejemplo_mapa.mapa()
    m_lados.catalogos.lados = [
        {"id": 1,   "nombre": "Robot A", "color_h": 0.122, "color_s": 0.919},
        {"id": 7,   "nombre": "Robot B", "color_h": 0.559, "color_s": 0.519},
        {"id": 42,  "nombre": "Robot C", "color_h": 0.333, "color_s": 0.700},
        {"id": 547, "nombre": "Robot D", "color_h": 0.800, "color_s": 0.600},
    ]
    for inst, lado in zip(m_lados.instancias, (1, 7, 42, 547)):
        inst["param"]["lado"] = lado
    sql_l, avisos_l = sql_mapa.script_edicion(m_lados)
    err_l, tab_l = revisar(sql_l)
    assert not err_l, err_l
    assert not avisos_l, avisos_l
    assert {f["ID_LADO"] for f in tab_l["Partido_Lado"]} == {"1", "7", "42", "547"}
    assert {z["FK_LADO"] for z in tab_l["Arbitraje_ZonaAcciones"]} \
        == {"1", "7", "42", "547"}
    print("Un partido con cuatro lados y con IDs sueltos (1, 7, 42, 547) se vuelca "
          "sin errores.")

    m_comillas = ejemplo_mapa.mapa()
    m_comillas.catalogos.estilos[0]["descripcion"] = "Penaliz. d'O"
    sql_c, _ = sql_mapa.script_edicion(m_comillas)
    assert "'Penaliz. d''O'" in sql_c, "las comillas simples deben duplicarse"
    print("Los textos con comillas se escapan al estilo de MySQL.")

    # --- Comprobaciones de contenido ---
    # Los grupos del editor van detrás de los totales generales, y cuántos son lo
    # dice el catálogo: no se puede dar por hecho que el primero sea el 4.
    g1 = str(m.catalogos.primer_grupo())
    g2 = str(m.catalogos.primer_grupo() + 1)
    zonas = tablas["Arbitraje_ZonaAcciones"]
    despensa = [z for z in zonas if z["FK_GRUPO_ACCIONES"] == g1]
    assert len(despensa) == 2, "el grupo simétrico debe dar dos parciales"
    assert {z["FK_LADO"] for z in despensa} == {"1", "2"}
    assert {z["ID_ZONA_ACCIONES"] for z in despensa} == {"1"}, \
        "la pareja simétrica comparte ID_ZONA y se distingue por el lado"
    assert [z["reflejar_x"] for z in despensa] == ["FALSE", "TRUE"]
    print("La pareja simétrica comparte ID_ZONA_ACCIONES y solo una va reflejada.")

    assert all(z["mostrar_puntos"].strip() == "TRUE" for z in despensa), \
        "los dos parciales de la despensa muestran el total"
    marcador = [z for z in zonas if z["FK_GRUPO_ACCIONES"] == g2]
    assert all(z["mostrar_puntos"].strip() == "FALSE" for z in marcador)
    print("Cada zona dice con mostrar_puntos si dibuja el total.")

    # La etiqueta del total es una fila por GRUPO, y solo de los que la muestran: la
    # ausencia de fila es lo que dice que ese grupo no la lleva en ninguna zona.
    totales = tablas["Arbitraje_TotalGrupoAcciones"]
    assert [t["FK_GRUPO_ACCIONES"] for t in totales] == [g1], \
        "la despensa tiene fila; el marcador, que la oculta en todos sus parciales, no"
    fila = totales[0]
    assert fila["FK_GUIA_X1"] != fila["FK_GUIA_X2"]
    assert fila["FK_GUIA_Y1"] != fila["FK_GUIA_Y2"]
    assert fila["zona_d"].strip() == "2", "el desplazamiento es del grupo"
    print("El total va a TotalGrupoAcciones: una fila por grupo que lo muestre.")

    # Las etiquetas son una fila por etiqueta, no por colocación: la vista las reparte
    # por todas las colocaciones de su grupo, igual que hace con las acciones.
    etq = tablas["Arbitraje_Etiqueta"]
    assert "Arbitraje_EtiquetaFija" not in tablas, \
        "esa tabla ya no existe: todo va en Arbitraje_Etiqueta"
    assert len(etq) == 3, "un rótulo fijo en Despensa y dos externas en Marcador"
    assert all("FK_LADO" not in e for e in etq), \
        "la etiqueta ya no lleva lado: lo pone el parcial que la dibuja"
    rotulo = next(e for e in etq if e["FK_GRUPO_ACCIONES"] == g1)
    assert rotulo["externa"] == "FALSE" and rotulo["tipo"] == "1"
    assert rotulo["valor"] == "'DESPENSA'" and rotulo["justificacion"] == "'w'"
    marcador = [e for e in etq if e["FK_GRUPO_ACCIONES"] == g2]
    assert [e["ID_ETIQUETA"] for e in marcador] == ["1", "2"], \
        "se numeran dentro de su grupo (la clave primaria es ID + grupo)"
    assert {e["valor"] for e in marcador} == {"'NOMBRE'", "'LOGO'"}
    assert all(e["externa"] == "TRUE" for e in marcador)
    assert {e["tipo"] for e in marcador} == {"1", "2"}, "texto y imagen"
    # La posición son guías del grupo, como en las acciones.
    for e in etq:
        assert e["FK_GUIA_X1"] != e["FK_GUIA_X2"]
        assert e["FK_GUIA_Y1"] != e["FK_GUIA_Y2"]
    print("Etiquetas: una fila por etiqueta, numeradas por grupo, situadas con guías.")
    print("Externas (valor = identificador de la vista del partido) y fijas conviven.")

    acciones = tablas["Arbitraje_TipoAcciones"]
    assert len(acciones) == 3
    assert [a["ID_TIPO_ACCIONES"] for a in acciones] == ["1", "2", "3"], \
        "los botones se numeran dentro de su grupo"
    assert all(a["FK_TIPO_ACCION"] == "1" for a in acciones), "click = 1"
    print("Los botones se numeran dentro de su grupo y su tipo se traduce al ID de "
          "Arbitraje_TipoAccion.")

    # Los totales generales reservan los primeros identificadores y los grupos van
    # detrás; si se define otro total, todo se corre un puesto.
    grupos = tablas["Arbitraje_GrupoAcciones"]
    n_tot = len(m.catalogos.totales)
    assert [int(g["ID_GRUPO_ACCIONES"]) for g in grupos][:n_tot] == list(range(1, n_tot + 1))
    assert min(int(g["ID_GRUPO_ACCIONES"]) for g in grupos
               if g.get("comun") is not None) == n_tot + 1
    print(f"Los {n_tot} totales generales ocupan los IDs 1..{n_tot} y los grupos del "
          f"editor empiezan en el {n_tot + 1}.")

    m_mas = ejemplo_mapa.mapa()
    m_mas.catalogos.totales.append({"id": 3, "nombre": "Total no común"})
    m_mas.catalogos.renumerar_totales()
    sql_mas, _ = sql_mapa.script_edicion(m_mas)
    t_mas = {}
    for sent in sentencias(sql_mas):
        mm = re.match(r"INSERT INTO (\w+)\s*\((.*?)\)\s*VALUES(.*)", sent, re.S | re.I)
        if mm:
            cuerpo = re.split(r"ON DUPLICATE KEY UPDATE", mm.group(3), flags=re.I)[0]
            cols = [c.strip() for c in mm.group(2).split(",") if c.strip()]
            t_mas.setdefault(mm.group(1), []).extend(
                dict(zip(cols, partir_valores(f.replace("\n", " "))))
                for f in filas_de(cuerpo))
    assert {r["ID_RESULTADO"] for r in t_mas["General_Resultado"]} == {"1", "2", "3"}
    assert min(int(g["ID_GRUPO_ACCIONES"]) for g in t_mas["Arbitraje_GrupoAcciones"]
               if g.get("comun") is not None) == 4, \
        "al añadir un total, los grupos del editor se corren un puesto"
    print("Al definir un total más, los grupos del editor se desplazan detrás de él.")

    prueba_avisos()
    print("\nTodas las comprobaciones han pasado.")
    return 0




def prueba_avisos():
    """Casos que la base de datos rechazaria: el generador debe avisar."""
    from editor_mapa.modelo import ModeloMapa

    def base():
        m = ModeloMapa()
        m.dim_mapa = (1920, 1080)
        gh = m.anadir_guia_colocacion("h", 400)
        gv = m.anadir_guia_colocacion("v", 300)
        t = m.crear_grupo("G")
        guias = (m.guia_ctrl_en(t, "v", 0), m.guia_ctrl_en(t, "v", 60),
                 m.guia_ctrl_en(t, "h", 0), m.guia_ctrl_en(t, "h", 40))
        return m, t, guias, gv, gh

    print("\n=== Avisos ===")
    # 1) Una etiqueta es UNA fila aunque su grupo esté colocado varias veces: la
    #    clave primaria es (ID_ETIQUETA, FK_GRUPO_ACCIONES) y la vista la reparte por
    #    las colocaciones. Antes se generaba una fila por colocación y chocaban.
    m, t, (a, b, c, d), gv, gh = base()
    m.anadir_control(t, "etiqueta", "Rótulo", a, b, c, d,
                     {"externa": False, "tipo": 1, "valor": "X", "tam": None},
                     m.param_etiqueta())
    gv2 = m.anadir_guia_colocacion("v", 800)
    m.colocar_grupo(t, gv, gh)
    m.colocar_grupo(t, gv2, gh)
    sql, avisos = sql_mapa.script_edicion(m)
    errores, tablas = revisar(sql)
    assert not errores, errores
    assert not avisos, avisos
    assert len(tablas["Arbitraje_Etiqueta"]) == 1, \
        "dos colocaciones del grupo, pero una sola fila de etiqueta"
    print("   Dos colocaciones del grupo: la etiqueta sigue siendo una sola fila.")

    # 2) Identificador de una etiqueta externa más largo de lo que admite la vista.
    m, t, (a, b, c, d), gv, gh = base()
    m.anadir_control(t, "etiqueta", "Ronda", a, b, c, d,
                     {"externa": True, "tipo": 1, "valor": "RONDA_DEL_PARTIDO",
                      "tam": None}, m.param_etiqueta())
    m.colocar_grupo(t, gv, gh)
    sql, avisos = sql_mapa.script_edicion(m)
    errores, tablas = revisar(sql)
    assert not errores, errores
    assert any("10 caracteres" in x for x in avisos), avisos
    assert len(tablas["Arbitraje_Etiqueta"]) == 1, "se guarda, pero avisando"
    print("   Identificador externo demasiado largo: se guarda y se avisa.")

    # 3) Grupo sin colocar y estilo que no está en el catálogo.
    m, t, (a, b, c, d), gv, gh = base()
    m.anadir_control(t, "boton", "B", a, b, c, d,
                     {"modo": "texto", "valor": "0", "tam": None},
                     dict(m.param_accion(), estilo=99))
    sql, avisos = sql_mapa.script_edicion(m)
    assert any("no está colocado" in a for a in avisos)
    assert any("estilo de fuente 99" in a for a in avisos)
    print("   Grupo sin colocar y estilo inexistente: los dos se avisan.")

    # 4) Textos que no caben en su columna y enteros negativos en columnas UNSIGNED.
    m, t, (a, b, c, d), gv, gh = base()
    m.catalogos.arbitros = [{"id": 1, "nombre": "Izquierda",
                             "descripcion": "Árbitro del lado izquierdo"}]
    m.anadir_control(t, "etiqueta", "Logo", a, b, c, d,
                     {"externa": False, "tipo": 2,
                      "valor": "/home/pedro/git/TFG/editor/graficos/logo_equipo.png",
                      "tam": None}, m.param_etiqueta())
    inst, _ = m.colocar_grupo(t, gv, gh)
    inst["param"]["valor_defecto"] = -5
    sql, avisos = sql_mapa.script_edicion(m)
    assert any("solo admite 5" in x for x in avisos), "nombre de árbitro VARCHAR(5)"
    assert any("Etiqueta.valor solo admite 50" in x for x in avisos), \
        "en la etiqueta solo cabe el nombre de la imagen (50), no una ruta"
    assert any("no admite negativos" in x for x in avisos)
    print("   Textos demasiado largos y negativos en UNSIGNED: se avisan por columna.")

    # 4b) De las imágenes solo se guarda el nombre: el directorio raíz lo pone la
    # configuración del arbitraje, así que una ruta no la encontraría otro ordenador.
    m, t, (a, b, c, d), gv, gh = base()
    m.anadir_control(t, "boton", "Robot", a, b, c, d,
                     {"modo": "texto", "valor": "0", "tam": None},
                     dict(m.param_accion(), img_pos="s",
                          directorio="C:/Users/claud/Escritorio/TFG/graficos/Robot2.png"))
    m.colocar_grupo(t, gv, gh)
    _, avisos = sql_mapa.script_edicion(m)
    assert any("es una ruta" in x and "Robot2.png" in x for x in avisos), avisos
    # Y el que guarda solo el nombre no da guerra.
    m, t, (a, b, c, d), gv, gh = base()
    m.anadir_control(t, "boton", "Robot", a, b, c, d,
                     {"modo": "texto", "valor": "0", "tam": None},
                     dict(m.param_accion(), img_pos="s", directorio="Robot2.png"))
    m.colocar_grupo(t, gv, gh)
    _, avisos = sql_mapa.script_edicion(m)
    assert not any("es una ruta" in x for x in avisos), avisos
    print("   Iconos y etiquetas con ruta en vez de nombre: se avisan.")

    # 4c) Al leer el XML, una ruta antigua se reduce al nombre del archivo.
    from xml.etree import ElementTree as ET2
    from editor_mapa.persistencia import xml_io as xio
    con_ruta = """<arbitraje>
      <vertical NOMBRE="GV1" POSICION="300" /><horizontal NOMBRE="GH1" POSICION="200" />
      <grupo NOMBRE="G" TOTAL_ESTILO="0" TOTAL_D="0">
        <vertical NOMBRE="CV0" POSICION="0" /><vertical NOMBRE="CV1" POSICION="60" />
        <horizontal NOMBRE="CH0" POSICION="0" /><horizontal NOMBRE="CH1" POSICION="40" />
        <control NOMBRE="B" X1="CV0" X2="CV1" Y1="CH0" Y2="CH1" CLASE="boton"
                 TIPO_ACCION="bool" ACCION="B" ESTILO="0" PUBLICAR="1" IMG_POS="s"
                 DIRECTORIO="C:/Users/claud/Escritorio/TFG/graficos/Robot2.png" />
      </grupo>
    </arbitraje>"""
    m5 = ModeloMapa()
    xio.cargar(m5, ET2.fromstring(con_ruta))
    assert m5.controles[0]["param"]["directorio"] == "Robot2.png", \
        m5.controles[0]["param"]["directorio"]
    print("   Un XML con la ruta completa del icono se lee como nombre de archivo.")

    # 5) El diseño real del repositorio se convierte sin errores.
    from xml.etree import ElementTree as ET
    from editor_mapa.persistencia import xml_io
    m = ModeloMapa()
    xml_io.cargar(m, ET.parse(XML_EJEMPLO).getroot())
    m.dim_mapa = (1920, 1080)
    sql, avisos = sql_mapa.script_edicion(m)
    errores, tablas = revisar(sql)
    assert not errores, errores
    assert not avisos, avisos
    print(f"   El arbitraje.xml del repositorio genera "
          f"{sum(len(f) for f in tablas.values())} filas sin errores ni avisos.")


if __name__ == "__main__":
    sys.exit(main())