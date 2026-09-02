"""Fuentes y medidas de texto.

Medir texto exige preguntarle a Tk, asi que esto es responsabilidad de la VISTA,
no del modelo: el modelo guarda que estilo usa cada control, pero no sabe cuantos
pixeles ocupa una letra.
"""
import tkinter.font as tkfont

from ..modelo.geometria import MARGEN_TEXTO
from .apariencia import FUENTE

# Cache de fuentes, compartida por el lienzo y por las vistas previas de los
# dialogos. El tamano se pide en NEGATIVO para que Tk lo interprete en pixeles y
# no en puntos (los puntos dependen de los DPI de la pantalla).
_CACHE = {}
_FAMILIAS = None

# Arbitraje_EstiloFuente.estilo_fuente es texto libre y la base de datos lo
# documenta en castellano ("Negrita, cursiva, ..."), asi que se admiten las dos
# formas. Antes solo se miraba "bold": cualquier otro valor se dibujaba normal y
# parecia que el estilo no se aplicaba.
_NEGRITA = ("bold", "negrita")
_CURSIVA = ("italic", "cursiva", "itálica", "italica")
_SUBRAYADO = ("underline", "subrayado", "subrayada")


def familias_disponibles():
    """Familias que Tk sabe dibujar. Se piden una sola vez (la consulta es lenta)."""
    global _FAMILIAS
    if _FAMILIAS is None:
        try:
            # Las que empiezan por @ son las verticales de CJK; no interesan aqui.
            _FAMILIAS = sorted({f for f in tkfont.families() if not f.startswith("@")})
        except Exception:
            _FAMILIAS = []
    return _FAMILIAS


def familia_valida(nombre):
    """Familia realmente instalada. Si el nombre no existe, Tk lo sustituye por otra
    en silencio y da la sensacion de que el estilo no se aplica; se avisa antes
    devolviendo la de por defecto."""
    nombre = str(nombre or "").strip()
    if not nombre:
        return FUENTE
    familias = familias_disponibles()
    if not familias:
        return nombre     # sin lista (Tk aun sin arrancar), se confia en el nombre
    for f in familias:
        if f.lower() == nombre.lower():
            return f      # se devuelve con las mayusculas correctas
    return FUENTE


def rasgos_de_estilo(estilo):
    """(negrita, cursiva, subrayado) de una fila de Arbitraje_EstiloFuente."""
    txt = str((estilo or {}).get("estilo_fuente", "")).lower()
    return (any(p in txt for p in _NEGRITA),
            any(p in txt for p in _CURSIVA),
            any(p in txt for p in _SUBRAYADO))


def fuente_px(familia, negrita, px, cursiva=False, subrayado=False):
    px = max(1, int(px))
    clave = (familia, bool(negrita), px, bool(cursiva), bool(subrayado))
    if clave not in _CACHE:
        _CACHE[clave] = tkfont.Font(family=familia, size=-px,
                                    weight="bold" if negrita else "normal",
                                    slant="italic" if cursiva else "roman",
                                    underline=bool(subrayado))
    return _CACHE[clave]


def fuente_de_estilo(estilo, px):
    """Un estilo es una fila de Arbitraje_EstiloFuente: nombre, estilo y tamano."""
    if not estilo:
        return fuente_px(FUENTE, True, px)
    negrita, cursiva, subrayado = rasgos_de_estilo(estilo)
    return fuente_px(familia_valida(estilo.get("nombre_fuente")), negrita, px,
                     cursiva, subrayado)


def color_de_estilo(estilo):
    return (estilo or {}).get("color_fuente") or "#000000"


def tamano_de_estilo(estilo):
    """Tamano fijo del estilo, o 0 si no lo define (entonces el texto se ajusta)."""
    try:
        return int((estilo or {}).get("tamano_fuente") or 0)
    except (TypeError, ValueError):
        return 0


def tam_automatico(estilo, texto, ancho, alto):
    """Mayor tamano que cabe DENTRO del recuadro, teniendo en cuenta tanto la altura
    de la linea como la anchura real del texto (no solo la del hueco: 'hola' ocupa
    mucho mas que '0' con la misma fuente)."""
    ancho = max(1, ancho - 2 * MARGEN_TEXTO)
    alto = max(1, alto - 2 * MARGEN_TEXTO)
    cand = max(1, int(alto * 0.8))
    while cand > 1 and fuente_de_estilo(estilo, cand).metrics("linespace") > alto:
        cand -= 1
    if texto:
        w = fuente_de_estilo(estilo, cand).measure(texto)
        if w > ancho:
            cand = max(1, int(cand * ancho / w))
            while cand > 1 and fuente_de_estilo(estilo, cand).measure(texto) > ancho:
                cand -= 1
    return max(1, cand)


def cabe_texto(estilo, texto, px, ancho, alto):
    """¿El texto, en ese tamano, cabe dentro del recuadro?"""
    f = fuente_de_estilo(estilo, px)
    return (f.measure(texto) <= max(1, ancho - 2 * MARGEN_TEXTO)
            and f.metrics("linespace") <= max(1, alto - 2 * MARGEN_TEXTO))