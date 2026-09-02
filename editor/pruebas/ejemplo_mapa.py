"""Mapa de ejemplo que usan las pruebas del generador de SQL."""
import rutas   # noqa: F401  (deja el paquete importable)
from editor_mapa.modelo import ModeloMapa


def mapa():
    m = ModeloMapa()
    m.dim_mapa = (1920, 1080)
    m.catalogos.arbitros = [{"id": 1, "nombre": "IZQ",
                             "descripcion": "Árbitro izquierda"}]
    m.simetria = True
    gh = m.anadir_guia_colocacion("h", 400)
    gv = m.anadir_guia_colocacion("v", 300)

    # --- Grupo "Despensa": un boton por nivel, mas un rotulo fijo ---
    tid = m.crear_grupo("Despensa")
    vs = [m.guia_ctrl_en(tid, "v", r) for r in (0, 60)]
    hs = [m.guia_ctrl_en(tid, "h", r) for r in (-40, 0, 40, 80, 120)]
    for n, (a, b) in enumerate(zip(hs[1:], hs[2:]), 1):
        m.anadir_control(
            tid, "boton", f"Despensa{n}", vs[0], vs[1], a, b,
            {"modo": "texto", "valor": "0", "tam": None},
            dict(m.param_accion(), accion=f"Cajas nivel {n}", valor_maximo=3,
                 img_pos="w", directorio="cajas", tipo_d=2))

    # El total es unico para todo el mapa: rectangulo respecto al origen del grupo.
    m.poner_total(0, -40, 60, 40, "Total")
    # Estilo y desplazamiento con los que ESTE grupo lo dibuja (TotalGrupoAcciones).
    m.tipo(tid)["total_d"] = 2

    m.anadir_control(
        tid, "etiqueta", "Rótulo", vs[0], vs[1], hs[3], hs[4],
        {"externa": False, "tipo": 1, "valor": "DESPENSA", "tam": None},
        dict(m.param_etiqueta(), justif="w"))

    i1, i2 = m.colocar_grupo(tid, gv, gh)
    i1["param"].update(lado=1, arbitro=1, color_v=240)
    i2["param"].update(lado=2, arbitro=1, color_v=240)

    # --- Grupo "Marcador": dos etiquetas externas, sin total ---
    gv2 = m.anadir_guia_colocacion("v", 200)
    t2 = m.crear_grupo("Marcador")
    a, b = m.guia_ctrl_en(t2, "v", 0), m.guia_ctrl_en(t2, "v", 300)
    c, d = m.guia_ctrl_en(t2, "h", 0), m.guia_ctrl_en(t2, "h", 50)
    # Etiqueta externa: su valor lo pone la vista del partido, uno por lado.
    m.anadir_control(
        t2, "etiqueta", "Nombre equipo", a, b, c, d,
        {"externa": True, "tipo": 1, "valor": "NOMBRE", "tam": None},
        m.param_etiqueta())
    m.anadir_control(
        t2, "etiqueta", "Logo", a, b, c, d,
        {"externa": True, "tipo": 2, "valor": "LOGO", "tam": None},
        m.param_etiqueta())

    j1, j2 = m.colocar_grupo(t2, gv2, gh)
    j1["param"]["lado"] = 1
    j2["param"]["lado"] = 2
    # El total existe para todo el mapa; el marcador es el caso de "ocultarlo": al no
    # mostrarlo ninguno de sus parciales, ese grupo no llega a TotalGrupoAcciones.
    j1["param"]["mostrar_puntos"] = False
    j2["param"]["mostrar_puntos"] = False
    return m
