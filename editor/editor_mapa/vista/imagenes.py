"""Carga y cacheo de las imagenes que se dibujan (iconos y etiquetas graficas)."""
from PIL import Image

# Filtro de reescalado: el mejor de Pillow para reducir sin dientes de sierra.
RESAMPLE = Image.Resampling.LANCZOS

_CACHE = {}


def imagen(ruta):
    """Imagen PIL en RGBA, o None si no se puede abrir. Se cachea por ruta."""
    if not ruta:
        return None
    if ruta not in _CACHE:
        try:
            _CACHE[ruta] = Image.open(ruta).convert("RGBA")
        except Exception:
            _CACHE[ruta] = None
    return _CACHE[ruta]


def escalada(ruta, ancho, alto):
    """Imagen ajustada a ese tamano, o None."""
    img = imagen(ruta)
    if img is None:
        return None
    return img.resize((max(1, int(ancho)), max(1, int(alto))), RESAMPLE)