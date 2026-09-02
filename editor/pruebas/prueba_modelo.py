"""Pruebas de todo lo implementado hasta ahora, ya sobre la estructura MVC.

Se apoyan solo en `modelo` y `persistencia`, que no necesitan interfaz grafica:
esa es justamente la ventaja de haberlos independizado de tkinter.
"""
from xml.etree import ElementTree as ET

from rutas import XML_EJEMPLO   # noqa: F401  (deja el paquete importable)

from editor_mapa.modelo import ModeloMapa, color_lado          # noqa: E402
from editor_mapa.modelo.catalogos import ESTILOS_DEFECTO, LADOS_DEFECTO   # noqa: E402
from editor_mapa.modelo.constantes import ID_MINIMO             # noqa: E402
from editor_mapa.modelo.constantes import CATALOGOS_VOLCADOS   # noqa: E402
from editor_mapa.modelo.geometria import reparto_icono         # noqa: E402
from editor_mapa.persistencia import xml_io                    # noqa: E402



def modelo(ancho=1000, alto=600):
    m = ModeloMapa()
    m.dim_mapa = (ancho, alto)
    return m


def texto(m):
    return ET.tostring(xml_io.serializar(m), encoding="unicode")


def titulo(t):
    print(f"\n=== {t} ===")


# ============================================================ ETIQUETA DE TOTAL
def prueba_total():
    titulo("Etiqueta del total")
    m = modelo()
    tid = m.crear_grupo("Despensa")
    v0 = m.guia_ctrl_en(tid, "v", 0.0)
    v1 = m.guia_ctrl_en(tid, "v", 60.0)
    h0 = m.guia_ctrl_en(tid, "h", 0.0)
    h1 = m.guia_ctrl_en(tid, "h", 40.0)
    m.guia_ctrl_en(tid, "h", -30.0)
    m.anadir_control(tid, "boton", "Boton", v0, v1, h0, h1,
                     {"modo": "texto", "valor": "1", "tam": None}, m.param_accion())
    # El total es del mapa, no del grupo: se define una vez con su rectangulo.
    m.poner_total(0.0, -30.0, 60.0, 30.0, "Total")

    gh = m.anadir_guia_colocacion("h", 300)
    insts = [m.colocar_grupo(tid, m.anadir_guia_colocacion("v", x), gh, nom)[0]
             for x, nom in ((200, "Amarilla"), (400, "Azul"), (600, "Gris"))]
    insts[2]["param"]["mostrar_puntos"] = False   # el gris no lleva etiqueta
    # Estilo y desplazamiento de la etiqueta: son del GRUPO (TotalGrupoAcciones).
    m.tipo(tid)["total_d"] = 3

    print("Geometría del total (común a todo el mapa):", m.geom_total())
    for i in insts:
        print(f'   {i["nombre"]:<9} muestra={m.muestra_total(i)}')
    assert m.muestra_total(insts[0]) and not m.muestra_total(insts[2])
    assert m.geom_total()[2:] == (60.0, 30.0)
    assert [t["nombre"] for t in m.grupos_con_total()] == ["Despensa"], \
        "el grupo lleva fila mientras alguno de sus parciales muestre el total"

    x = texto(m)
    zonas = {p.get("NOMBRE"): p.get("MOSTRAR_PUNTOS")
             for p in ET.fromstring(x).findall("parcial")}
    assert zonas == {"Amarilla": "1", "Azul": "1", "Gris": "0"}
    m2 = modelo()
    xml_io.cargar(m2, ET.fromstring(x))
    assert {i["nombre"]: m2.muestra_total(i) for i in m2.instancias} == \
           {"Amarilla": True, "Azul": True, "Gris": False}
    assert m2.desp_total(m2.tipos[0]["id"]) == 3, "el desplazamiento es del grupo"
    assert texto(m2) == x
    print("Ida y vuelta estable; cada parcial recuerda si lo muestra.")

    # El total es del mapa: otro grupo distinto lo dibuja en el mismo sitio relativo.
    otro = m.crear_grupo("Nido")
    m.guia_ctrl_en(otro, "v", 0.0)
    inst_otro = m.colocar_grupo(otro, m.anadir_guia_colocacion("v", 800), gh)[0]
    assert m.muestra_total(inst_otro), \
        "la etiqueta del total debe ser la misma en todos los grupos"
    assert [t["nombre"] for t in m.grupos_con_total()] == ["Despensa", "Nido"]
    inst_otro["param"]["mostrar_puntos"] = False
    assert not m.muestra_total(inst_otro), \
        "lo único que puede hacer un parcial es ocultarla"
    assert [t["nombre"] for t in m.grupos_con_total()] == ["Despensa"], \
        "sin ningún parcial que la muestre, el grupo se queda sin fila"
    print("Misma etiqueta en todos los grupos; cada parcial solo la muestra u oculta.")


def prueba_total_en_el_xml():
    titulo("La etiqueta del total viaja en el XML")
    actual = """<arbitraje>
      <vertical NOMBRE="GV1" POSICION="300" />
      <vertical NOMBRE="GV2" POSICION="700" />
      <horizontal NOMBRE="GH1" POSICION="200" />
      <grupo NOMBRE="Despensa" COMUN="0" TOTAL_ESTILO="0" TOTAL_D="2">
        <vertical NOMBRE="CV0" POSICION="0" /><vertical NOMBRE="CV1" POSICION="60" />
        <horizontal NOMBRE="CH0" POSICION="0" /><horizontal NOMBRE="CH1" POSICION="40" />
        <control NOMBRE="D1" X1="CV0" X2="CV1" Y1="CH0" Y2="CH1" CLASE="boton"
                 TIPO_ACCION="click" ACCION="D1" ESTILO="0" PUBLICAR="1" />
      </grupo>
      <total NOMBRE="Total" X="0" Y="-30" W="60" H="30" />
      <parcial NOMBRE="Con total" GRUPO="Despensa" X="GV1" Y="GH1" LADO="1"
               MOSTRAR_PUNTOS="1" />
      <parcial NOMBRE="Sin total" GRUPO="Despensa" X="GV2" Y="GH1" LADO="0"
               MOSTRAR_PUNTOS="0" />
    </arbitraje>"""
    m = modelo()
    _, err = xml_io.cargar(m, ET.fromstring(actual))
    assert not err, err
    tid = m.tipos[0]["id"]
    print("Etiqueta única del mapa:", m.geom_total())
    assert m.geom_total() == (0.0, -30.0, 60.0, 30.0)
    # Cada parcial decide si la muestra (Arbitraje_ZonaAcciones.mostrar_puntos).
    assert m.muestra_total(m.instancias[0]) and not m.muestra_total(m.instancias[1])
    # El desplazamiento es del grupo (Arbitraje_TotalGrupoAcciones), no del parcial.
    assert m.desp_total(tid) == 2
    print("Cada parcial decide si se ve; el desplazamiento es del grupo.")


# ==================================================================== SIMETRIA
def prueba_simetria():
    titulo("Simetría horizontal")
    m = modelo(1000)
    assert m.eje() == 500.0
    gv = m.anadir_guia_colocacion("v", 100)
    gh = m.anadir_guia_colocacion("h", 200)
    tid = m.crear_grupo("Nido")
    inst, _ = m.colocar_grupo(tid, gv, gh, "Nido 1")
    assert len(m.guias_col) == 2 and len(m.instancias) == 1

    m.simetria = True
    print("Al activar ->", m.aplicar_simetria(), "(guías, colocaciones) nuevas")
    esp_g = m.guia_col(gv["espejo"])
    esp_i = m.instancia(inst["espejo"])
    assert esp_g["pos"] == 900.0 and esp_i["inv"] is True and esp_i["gh"] == gh["id"]

    # Mover arrastra a la pareja, en los dos sentidos.
    m.mover_guia_col(gv, 150)
    assert esp_g["pos"] == 850.0
    m.mover_guia_col(esp_g, 800)
    assert gv["pos"] == 200.0
    print("Movimiento sincronizado en los dos sentidos.")

    # Añadir con la simetría puesta.
    gv2 = m.anadir_guia_colocacion("v", 300)
    assert m.guia_col(gv2["espejo"])["pos"] == 700.0
    _, esp2 = m.colocar_grupo(tid, gv2, gh, "Nido 2")
    assert esp2 is not None and esp2["inv"] is True

    # Guardar y volver a abrir.
    x = texto(m)
    m2 = modelo(1000)
    xml_io.cargar(m2, ET.fromstring(x))
    m2.emparejar()
    assert m2.simetria
    assert sum(1 for g in m2.guias_col if g.get("auto")) == 2
    assert all(g.get("espejo") for g in m2.guias_col if g["orient"] == "v")
    m2.quitar_simetria()
    assert len(m2.guias_col) == 3 and len(m2.instancias) == 2
    print("Al desactivar solo desaparece lo creado por la simetría.")

    # Un diseño ya simétrico a mano no se duplica.
    m3 = modelo(1000)
    a = m3.anadir_guia_colocacion("v", 100)
    b = m3.anadir_guia_colocacion("v", 900)
    h = m3.anadir_guia_colocacion("h", 200)
    t3 = m3.crear_grupo("Granero")
    i1, _ = m3.colocar_grupo(t3, a, h, "izq")
    i2, _ = m3.colocar_grupo(t3, b, h, "der")
    i2["inv"] = True
    m3.simetria = True
    assert m3.aplicar_simetria() == (0, 0)
    assert a["espejo"] == b["id"] and i1["espejo"] == i2["id"]
    print("Un diseño ya simétrico se empareja sin duplicar nada.")

    # Guía sobre el eje: sin pareja, pero el grupo sí se refleja.
    m4 = modelo(1000)
    m4.simetria = True
    c = m4.anadir_guia_colocacion("v", 500)
    assert m4.es_central(c) and len(m4.guias_col) == 1
    hc = m4.anadir_guia_colocacion("h", 100)
    t4 = m4.crear_grupo("Centro")
    _, esp = m4.colocar_grupo(t4, c, hc, "Centro 1")
    assert esp is not None and esp["gv"] == c["id"] and esp["inv"] is True
    print("Guía sobre el eje: sin pareja, pero el grupo se refleja sobre sí mismo.")


# ================================================================== APARIENCIA
def prueba_apariencia():
    titulo("Apariencia: colores e iconos")
    lados = {l["nombre"]: l for l in LADOS_DEFECTO}
    for n, l in lados.items():
        print(f"   {n:<9} -> {color_lado(l, 255)}")
    assert color_lado(lados["Amarillo"], 255).startswith("#ff")
    assert color_lado(lados["Amarillo"], 0) == "#000000"
    assert color_lado(None, 255) is None
    # Compatibilidad con tonos en grados.
    assert color_lado({"color_h": 210.0, "color_s": 0.6}, 255) == \
           color_lado({"color_h": 210 / 360, "color_s": 0.6}, 255)

    for pos in ("w", "e", "n", "s"):
        ico, txt = reparto_icono(0, 0, 90, 60, pos)
        assert ico is not None and txt is not None
        assert ico[2] - ico[0] <= 90 and ico[3] - ico[1] <= 60
    ico, txt = reparto_icono(0, 0, 90, 60, "")
    assert ico is None and txt == (0, 0, 90, 60)
    print("Colores del lado y reparto del icono correctos.")

    # Una etiqueta no tiene lado propio: lo toma del parcial que la dibuja. Lo que si
    # es suyo son externa, tipo y valor (los tres campos de Arbitraje_Etiqueta).
    m = modelo()
    assert "lado" not in m.param_etiqueta()
    tid = m.crear_grupo("Marcador")
    v0, h0 = m.guia_ctrl_en(tid, "v", 0), m.guia_ctrl_en(tid, "h", 0)
    v1, h1 = m.guia_ctrl_en(tid, "v", 80), m.guia_ctrl_en(tid, "h", 30)
    m.anadir_control(tid, "etiqueta", "Fija", v0, v1, h0, h1,
                     {"externa": False, "tipo": 1, "valor": "PUNTOS", "tam": None},
                     m.param_etiqueta())
    m.anadir_control(tid, "etiqueta", "Dorsal", v0, v1, h0, h1,
                     {"externa": True, "tipo": 1, "valor": "DORSAL", "tam": None},
                     dict(m.param_etiqueta(), justif="e"))
    m.anadir_control(tid, "etiqueta", "Logo", v0, v1, h0, h1,
                     {"externa": True, "tipo": 2, "valor": "LOGO", "tam": None},
                     m.param_etiqueta())
    gv = m.anadir_guia_colocacion("v", 100)
    gh = m.anadir_guia_colocacion("h", 100)
    m.colocar_grupo(tid, gv, gh)
    x = texto(m)
    etqs = {c.get("NOMBRE"): (c.get("EXTERNA"), c.get("TIPO"), c.get("VALOR"))
            for c in ET.fromstring(x).find("grupo").findall("control")}
    print("Contenido en el XML:", etqs)
    assert etqs == {"Fija": ("0", "1", "PUNTOS"), "Dorsal": ("1", "1", "DORSAL"),
                    "Logo": ("1", "2", "LOGO")}
    m2 = modelo()
    xml_io.cargar(m2, ET.fromstring(x))
    assert {c["nombre"]: (c["contenido"]["externa"], c["contenido"]["tipo"]) 
            for c in m2.controles} == \
           {"Fija": (False, 1), "Dorsal": (True, 1), "Logo": (True, 2)}
    assert texto(m2) == x
    print("Etiqueta fija y externa: ida y vuelta estable.")

    # Una etiqueta de imagen guarda solo el nombre del archivo: el directorio lo pone
    # la configuracion del arbitraje, y Arbitraje_Etiqueta.valor solo admite 50
    # caracteres.
    otro = ET.fromstring(x)
    gel = otro.find("grupo")
    for el in list(gel.findall("control")):
        gel.remove(el)
    guias = {"X1": "CV0", "X2": "CV1", "Y1": "CH0", "Y2": "CH1", "CLASE": "etiqueta"}
    ET.SubElement(gel, "control", dict(guias, NOMBRE="Izquierda", EXTERNA="0", TIPO="1",
                                       VALOR="PUNTOS", JUSTIFICACION="w"))
    ET.SubElement(gel, "control", dict(guias, NOMBRE="Derecha", EXTERNA="1", TIPO="1",
                                       VALOR="DORSAL", JUSTIFICACION="e"))
    ET.SubElement(gel, "control", dict(guias, NOMBRE="Grafico", EXTERNA="0", TIPO="2",
                                       VALOR="logo.png"))
    m3 = modelo()
    _, errores = xml_io.cargar(m3, otro)
    leido = {c["nombre"]: (c["contenido"]["externa"], c["contenido"]["tipo"],
                           c["contenido"]["valor"], c["param"]["justif"])
             for c in m3.controles}
    print("Leído del XML:", leido)
    assert leido == {"Izquierda": (False, 1, "PUNTOS", "w"),
                     "Derecha": (True, 1, "DORSAL", "e"),
                     "Grafico": (False, 2, "logo.png", "c")}
    assert not errores, errores
    print("Justificación w/e y los tres campos de la tabla se leen tal cual.")


def prueba_total_anclado():
    titulo("La etiqueta del total cuelga de sus guías de control")
    m = modelo(1920, 1080)
    tid = m.crear_grupo("Despensa")
    inst, _ = m.colocar_grupo(tid, m.anadir_guia_colocacion("v", 400),
                              m.anadir_guia_colocacion("h", 300))
    m.guia_ctrl_en(tid, "v", 200)
    m.guia_ctrl_en(tid, "h", 80)
    m.poner_total(0, 0, 200, 80, nombre="Total")
    v1, v2, h1, h2 = m.guias_total(tid)
    assert m.geom_total() == (0.0, 0.0, 200.0, 80.0)
    print("Al dibujarla queda anclada a cuatro guías reales del grupo.")

    # Esto es lo que fallaba: la etiqueta no seguía a la guía.
    m.colocar_guia_ctrl(m.guia_ctrl(v2), 320)
    assert m.geom_total() == (0.0, 0.0, 320.0, 80.0), m.geom_total()
    m.colocar_guia_ctrl(m.guia_ctrl(h2), 130)
    assert m.geom_total() == (0.0, 0.0, 320.0, 130.0), m.geom_total()
    print("Al mover una guía, la etiqueta cambia de tamaño con ella.")

    # El rectángulo absoluto sale del origen del parcial más esas distancias.
    assert m.rect_control(inst, m.total) == (400.0, 300.0, 720.0, 430.0)
    print("El recuadro absoluto del parcial sale de las guías, no de un rectángulo fijo.")

    # Un grupo creado después hereda las guías, y moverlas sincroniza las del otro.
    tid2 = m.crear_grupo("Nido")
    assert m.rect_de_guias(m.guias_total(tid2)) == m.geom_total()
    movidas = m.colocar_guia_ctrl(m.guia_ctrl(m.guias_total(tid2)[1]), 250)
    assert movidas, "mover la guía de un grupo debe arrastrar la del otro"
    assert m.rect_de_guias(m.guias_total(tid)) == m.rect_de_guias(m.guias_total(tid2))
    print("El total sigue siendo el mismo en todos los grupos: las guías se sincronizan.")

    # Borrar una de sus guías se lleva la etiqueta entera.
    assert any(c.get("clase") == "total" for c in m.dependientes_guia_ctrl(v2))
    m.eliminar_guia_ctrl(v2)
    assert not m.hay_total()
    print("Borrar una de sus guías elimina la etiqueta, que se queda sin geometría.")

    # Ida y vuelta por el XML sin duplicar guías.
    m2 = modelo(1920, 1080)
    t2 = m2.crear_grupo("G")
    m2.colocar_grupo(t2, m2.anadir_guia_colocacion("v", 100),
                     m2.anadir_guia_colocacion("h", 100))
    m2.poner_total(10, 20, 60, 30, nombre="Total")
    x = texto(m2)
    m3 = modelo(1920, 1080)
    xml_io.cargar(m3, ET.fromstring(x))
    assert m3.geom_total() == (10.0, 20.0, 60.0, 30.0)
    assert len(m3.guias_ctrl) == len(m2.guias_ctrl)
    assert texto(m3) == x
    print("Ida y vuelta por el XML sin duplicar guías.")


# ==================================================================== CATALOGOS
def prueba_catalogos_en_el_xml():
    titulo("Catálogos en el XML")
    # El volcado de los catalogos se comprueba dentro del script completo, en
    # prueba_sql.py; aqui solo interesa que VOLCAR viaje bien en el XML.

    # VOLCAR viaja en el XML.
    m2 = modelo()
    x = texto(m2)
    assert (ET.fromstring(x).find("catalogos").get("VOLCAR")
            == "totales lados arbitros estilos")
    assert "lado" in {h.tag for h in ET.fromstring(x).find("catalogos")}
    m3 = modelo()
    xml_io.cargar(m3, ET.fromstring(x))
    assert m3.catalogos.volcar == list(CATALOGOS_VOLCADOS)
    print("Los cuatro catálogos viajan en el XML y los cuatro se vuelcan.")

    # Un XML guardado antes de que los lados se volcaran se completa al abrirlo.
    antiguo = ET.fromstring(x)
    antiguo.find("catalogos").set("VOLCAR", "arbitros estilos")
    m4 = modelo()
    xml_io.cargar(m4, antiguo)
    assert m4.catalogos.volcar == ["totales", "lados", "arbitros", "estilos"], \
        m4.catalogos.volcar
    print("Un XML antiguo con VOLCAR incompleto se completa al abrirlo.")

    # --- Totales generales: su ID es la posición y reservan los primeros grupos ---
    m5 = modelo()
    assert m5.catalogos.primer_grupo() == len(m5.catalogos.totales) + 1
    m5.catalogos.totales.append({"id": 99, "nombre": "Total no común"})
    m5.catalogos.renumerar_totales()
    assert [t["id"] for t in m5.catalogos.totales] == [1, 2, 3]
    assert m5.catalogos.primer_grupo() == 4
    print("Los totales generales se renumeran 1..N y corren el primer grupo libre.")

    # Un XML con huecos en los totales se renumera al abrirlo.
    x5 = texto(m5)
    con_hueco = ET.fromstring(x5)
    for n, el in enumerate(con_hueco.find("catalogos").findall("resultado")):
        el.set("ID", str(n * 5 + 3))
    m6 = modelo()
    xml_io.cargar(m6, con_hueco)
    assert [t["id"] for t in m6.catalogos.totales] == [1, 2, 3], m6.catalogos.totales
    print("Un XML con huecos en los totales se renumera al abrirlo.")


def prueba_ids_catalogos():
    titulo("El ID de los catálogos empieza en 1")
    # Los catalogos que crea el editor (arbitros y estilos) van a una tabla cuya
    # clave primaria es INT UNSIGNED: ni 0 ni negativos. Los lados son la excepcion,
    # porque Partido_Lado la crea eurobot_DATOS.sql y alli el lado 0 ("Comun") existe.
    assert ID_MINIMO["arbitros"] == 1 and ID_MINIMO["estilos"] == 1
    assert all(e["id"] >= 1 for e in ESTILOS_DEFECTO)
    print("El catálogo de estilos por defecto ya no usa el ID 0.")

    m = modelo()
    assert not m.catalogos.ids_invalidos()
    m.catalogos.arbitros = [{"id": 0, "nombre": "Cero", "descripcion": ""}]
    m.catalogos.estilos = [{"id": -1, "descripcion": "Negativo", "nombre_fuente": "Arial",
                            "estilo_fuente": "", "tamano_fuente": 20,
                            "color_fuente": "#000000"}]
    malos = m.catalogos.ids_invalidos()
    assert len(malos) == 2, malos
    assert any("árbitro con ID 0" in a for a in malos)
    assert any("estilo de fuente con ID -1" in a for a in malos)
    print("Un 0 o un negativo se detectan en árbitros y en estilos.")

    # El lado 0 sigue siendo valido: lo necesita la aplicacion de arbitraje.
    m2 = modelo()
    assert any(l["id"] == 0 for l in m2.catalogos.lados)
    assert not m2.catalogos.ids_invalidos()
    print("El lado 0 («Común») no se marca como error: no lo crea el editor.")

    # Al abrir un XML antiguo con IDs no validos, se avisa en vez de callar.
    x = texto(m)
    m3 = modelo()
    _, err = xml_io.cargar(m3, ET.fromstring(x))
    assert len(err) == 2, err
    print("Un XML antiguo con IDs 0 o negativos se abre, pero avisa.")


# ============================================================== ARCHIVO REAL
def prueba_archivo_real():
    titulo("El diseño real del proyecto")
    m = modelo(1920, 1080)
    _, err = xml_io.cargar(m, ET.parse(XML_EJEMPLO).getroot())
    print("errores:", err)
    print(" ", m.resumen())
    assert not err
    assert all("familia" not in t for t in m.tipos)
    x = texto(m)
    assert "FAMILIA" not in x
    m2 = modelo(1920, 1080)
    xml_io.cargar(m2, ET.fromstring(x))
    assert texto(m2) == x
    print("Carga sin errores e ida y vuelta estable.")

    # Un grupo puede mezclar botón, etiqueta y total.
    m3 = modelo()
    tid = m3.crear_grupo("Mixto")
    v0, v1 = m3.guia_ctrl_en(tid, "v", 0), m3.guia_ctrl_en(tid, "v", 60)
    h0, h1, h2 = (m3.guia_ctrl_en(tid, "h", r) for r in (0, 30, 60))
    m3.anadir_control(tid, "boton", "B", v0, v1, h0, h1,
                      {"modo": "texto", "valor": "0", "tam": None}, m3.param_accion())
    m3.anadir_control(tid, "etiqueta", "E", v0, v1, h1, h2,
                      {"modo": "texto", "valor": "PUNTOS", "tam": None},
                      m3.param_etiqueta())
    m3.poner_total(0.0, 0.0, 60.0, 30.0, "T")
    m3.colocar_grupo(tid, m3.anadir_guia_colocacion("v", 100),
                     m3.anadir_guia_colocacion("h", 100))
    x3 = texto(m3)
    m4 = modelo()
    xml_io.cargar(m4, ET.fromstring(x3))
    assert sorted(c["clase"] for c in m4.controles) == ["boton", "etiqueta"]
    assert m4.hay_total() and m4.geom_total() == (0.0, 0.0, 60.0, 30.0)
    assert len(m4.tipos) == 1
    print("Un grupo con botón y etiqueta más el total del mapa sigue siendo un grupo.")


if __name__ == "__main__":
    prueba_total()
    prueba_total_en_el_xml()
    prueba_simetria()
    prueba_apariencia()
    prueba_total_anclado()
    prueba_catalogos_en_el_xml()
    prueba_ids_catalogos()
    prueba_archivo_real()
    print("\nTodas las comprobaciones han pasado.")