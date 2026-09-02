"""Calculos geometricos, en pixeles del MAPA (nunca de pantalla).

Quien dibuje se encarga de aplicar la escala del zoom. Modulo del MODELO: aqui
no entra tkinter.
"""

MARGEN_TEXTO = 3    # holgura interior (px) entre el texto y el borde del recuadro


def reparto_icono(x1, y1, x2, y2, pos):
    """Parte el recuadro de un control en (hueco del icono, hueco del texto) segun
    img_pos: w=izquierda, e=derecha, n=arriba, s=abajo. Sin icono devuelve
    (None, recuadro entero)."""
    if pos not in ("w", "e", "n", "s"):
        return None, (x1, y1, x2, y2)
    w = x2 - x1
    h = y2 - y1
    if pos in ("w", "e"):
        lado = max(1.0, min(h, w / 2))
        cy1, cy2 = y1 + (h - lado) / 2, y1 + (h + lado) / 2
        if pos == "w":
            return (x1, cy1, x1 + lado, cy2), (x1 + lado, y1, x2, y2)
        return (x2 - lado, cy1, x2, cy2), (x1, y1, x2 - lado, y2)
    lado = max(1.0, min(w, h / 2))
    cx1, cx2 = x1 + (w - lado) / 2, x1 + (w + lado) / 2
    if pos == "n":
        return (cx1, y1, cx2, y1 + lado), (x1, y1 + lado, x2, y2)
    return (cx1, y2 - lado, cx2, y2), (x1, y1, x2, y2 - lado)
