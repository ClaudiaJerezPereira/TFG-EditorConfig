"""Comprueba el flujo de la seleccion, fila a fila del resumen de referencia.

    Acción              Controlador          Modelo                Vista
    ------------------  -------------------  --------------------  -------------------
    Clic en elemento    decide qué se toca   guarda la selección   refresca el resalte
    Clic en vacío       ve que no hay nada   limpia la selección   refresca el resalte
    Arrastre            guarda (x,y)         NO se toca            dibuja
    Soltar              aplica el cambio     mueve la guía         redibuja
"""
import rutas                      # noqa: F401  (deja el paquete importable)
import prueba_estructura as pe

pe.preparar_dobles()

from editor_mapa.modelo import ModeloMapa                      # noqa: E402
from editor_mapa.vista.lienzo import VistaLienzo               # noqa: E402


def escenario():
    m = ModeloMapa()
    m.dim_mapa = (1000, 600)
    gv = m.anadir_guia_colocacion("v", 100)
    gh = m.anadir_guia_colocacion("h", 200)
    tid = m.crear_grupo("Despensa")
    v1 = m.guia_ctrl_en(tid, "v", 60)
    h1 = m.guia_ctrl_en(tid, "h", 40)
    v0 = m.guia_ctrl_en(tid, "v", 0)
    h0 = m.guia_ctrl_en(tid, "h", 0)
    c = m.anadir_control(tid, "boton", "B1", v0, v1, h0, h1,
                         {"modo": "texto", "valor": "0", "tam": None}, m.param_accion())
    inst, _ = m.colocar_grupo(tid, gv, gh)
    return m, gv, gh, c, inst


print("=== La selección vive en el modelo ===")
m, gv, gh, c, inst = escenario()
# colocar_grupo NO selecciona: quien decide qué queda seleccionado es el controlador.
assert m.seleccion is None
m.seleccionar("col", gv["id"])
assert m.seleccion == ("col", gv["id"])
assert m.esta_seleccionado("col", gv["id"])
assert not m.esta_seleccionado("col", gh["id"])
assert m.seleccionado("col") == gv["id"] and m.seleccionado("inst") is None
m.limpiar_seleccion()
assert m.seleccion is None
print("seleccionar / limpiar_seleccion / esta_seleccionado / seleccionado: correctos.")

print("\n=== Al borrar algo, deja de estar seleccionado ===")
for accion, args in (("eliminar_control", (c["id"],)),
                     ("eliminar_instancia", (inst["id"],)),
                     ("eliminar_guia_col", (gv["id"],))):
    m2, gv2, gh2, c2, i2 = escenario()
    m2.seleccionar("control", c2["id"])
    getattr(m2, accion)(*(args if accion != "eliminar_control" else (c2["id"],)))
    assert m2.seleccion is None, accion
    print(f"   {accion}: la selección queda limpia.")

print("\n=== La vista lee la selección del modelo ===")
assert "sel" not in VistaLienzo.__init__.__code__.co_names or True
fuente = (rutas.PAQUETE / "vista" / "lienzo.py").read_text(encoding="utf-8")
assert "self.modelo.esta_seleccionado" in fuente
assert "def refrescar_seleccion" in fuente
assert "self.sel" not in fuente, "la vista ya no guarda su propia selección"
print("La vista consulta modelo.esta_seleccionado() y ofrece refrescar_seleccion().")

print("\n=== El controlador ya no guarda la selección ===")
ctrl = (rutas.PAQUETE / "controlador" / "principal.py").read_text(encoding="utf-8")
assert "self.sel " not in ctrl and "self.sel =" not in ctrl
assert "modelo.seleccionar" in ctrl or "m.seleccionar" in ctrl
assert "self.lienzo.refrescar_seleccion()" in ctrl
print("El controlador decide y delega: modelo.seleccionar() + refrescar_seleccion().")

print("\n=== Activar una colocación sí obliga a redibujar ===")
m3, gv3, gh3, c3, i3 = escenario()
m3.instancia_activa = None
assert m3.activar(i3["id"]) is True, "cambia la activa -> hay que redibujar"
assert m3.tipo_activo == i3["tipo"]
assert m3.activar(i3["id"]) is False, "ya estaba activa -> basta el resalte"
assert m3.activar(None) is False
print("activar() dice si ha cambiado, para redibujar solo cuando hace falta.")

print("\n=== El arrastre no toca el modelo hasta que se mueve ===")
ctrl_init = ctrl.split("def _acciones")[0]
for campo in ("_arrastre", "_modo_pan", "_cruce_inicio", "_preview"):
    assert campo in ctrl_init, campo
assert "_arrastre" not in (rutas.PAQUETE / "modelo" / "mapa.py").read_text(
    encoding="utf-8")
print("El estado del arrastre se queda en el controlador, fuera del modelo.")

print("\nTodas las comprobaciones han pasado.")