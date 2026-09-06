"""Carga y cacheo de las imagenes que se dibujan (iconos y etiquetas graficas)."""
import os

from PIL import Image

# Filtro de reescalado: el mejor de Pillow para reducir sin dientes de sierra.
RESAMPLE = Image.Resampling.LANCZOS

# Unicos formatos que admite el editor para las imagenes que elige el usuario: el
# icono de un control, la imagen de una etiqueta y la imagen del campo. JPG y PNG y
# nada mas, para no depender de formatos que la aplicacion de arbitraje podria no
# saber dibujar.
EXT_IMAGEN = (".png", ".jpg", ".jpeg")

# Filtro de los dialogos de archivo. Sin la entrada "Todos (*.*)": si se deja, el
# usuario puede colarse un GIF o un BMP y el limite deja de serlo.
TIPOS_IMAGEN = [("Imágenes JPG y PNG", "*.png *.jpg *.jpeg *.PNG *.JPG *.JPEG")]

# Como se nombran los formatos en los avisos, para no repetir el texto.
FORMATOS_IMAGEN = "JPG o PNG"


def extension_admitida(ruta):
    """True si el archivo tiene una de las extensiones de EXT_IMAGEN.

    El filtro del dialogo no basta: en Linux y en macOS se puede teclear el nombre
    a mano, y el nombre de la imagen tambien se puede escribir directamente en el
    campo del dialogo sin pasar por el boton de buscar.
    """
    return os.path.splitext(str(ruta or ""))[1].lower() in EXT_IMAGEN

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