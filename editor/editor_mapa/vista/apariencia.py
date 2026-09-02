"""Constantes de presentacion: colores, textos y tamanos de la interfaz.

Nada de esto pertenece al dominio: son decisiones de como se ve el editor.
"""
import tkinter as tk
from tkinter import ttk

# ttk.Spinbox solo existe desde Tk 8.6 / Python 3.7; si no, se usa el clasico.
Spin = getattr(ttk, "Spinbox", tk.Spinbox)

FUENTE = "Arial"
MARGEN_CRUCE = 10   # margen en pixeles de PANTALLA para "enganchar" un clic a un cruce

AYUDA = ("Elige un MODO arriba: Grupo (guías rojas), Control (guías verdes), "
         "Botón, Total o Etiqueta. Doble clic sobre una guía para escribir su "
         "posicion exacta.")

# --- Colores de las guias y los marcadores ---
COL_COLOCACION = "#cc2222"   # guias de colocacion (rojas, absolutas)
COL_CONTROL    = "#1a9e5a"   # guias de control (verdes, relativas)
COL_ORIGEN     = "#8e44ad"   # marcador del origen de una colocacion
COL_EJE        = "#0b6fa4"   # eje de simetria del campo
COL_SEL        = "#f39c12"   # resalte de seleccion
COL_MODO_ON    = "#a9d5ff"   # fondo del boton de modo activo
COL_DESBORDE   = "#c0392b"   # borde de un control cuyo texto no cabe

# --- Colores de respaldo de los controles ---
# El relleno real lo dan el lado y la intensidad del parcial; estos solo se usan
# cuando no hay catalogo de lados.
COL_BOTON       = "#f2a900"
COL_TOTAL       = "#7fc7b8"
COL_ETQ_TEXTO   = "#bfe3f2"
COL_ETQ_CAMPO   = "#d8ccf0"
COL_ETQ_GRAFICO = "#e2e2e2"

# Borde segun la clase: es lo que distingue un boton de una etiqueta ahora que el
# relleno es el color real del lado.
BORDE_CLASE = {"boton": "#333", "total": "#555", "etiqueta": "#888"}

# Como se llama cada clase de elemento en los mensajes al usuario.
NOMBRE_CLASE = {"boton": "Botón", "etiqueta": "Etiqueta", "total": "Total"}

# Etiquetas visibles de Arbitraje_TipoAcciones.img_pos.
IMG_POS_ETIQUETA = {"": "(ninguna)", "n": "arriba", "s": "abajo",
                    "e": "derecha", "w": "izquierda"}

# Marca que se dibuja en los controles de tipo "bool".
MARCA_BOOL = "✔"
COL_MARCA_BOOL = "#1a7f37"

# Tamano del lienzo de vista previa de los dialogos.
ANCHO_MUESTRA = 220
ALTO_MUESTRA = 140

# Textos de la barra de estado segun el modo activo.
# Textos de la barra de estado segun el modo activo.
ESTADO_MODO = {
    "grupo":    ("MODO GRUPO: selecciona/mueve guías de colocación (rojas) y orígenes. "
                 "Aunque una guía de control esté encima, aquí solo se selecciona la de "
                 "grupo. Doble clic en una guía = escribir su posición."),
    "control":  ("MODO CONTROL: selecciona/mueve guías de control (verdes) del grupo "
                 "activo. Doble clic en una guía = escribir su distancia al origen. "
                 "(Esc para salir)"),
    "boton":    ("MODO BOTÓN: arrastra entre dos cruces de guías de control para crear "
                 "un botón en el grupo activo. (Esc para salir)"),
    "total":    ("MODO TOTAL: arrastra entre dos cruces de guías de control para situar "
                 "la etiqueta con el total de puntos. Es ÚNICA para todo el mapa: sale "
                 "igual en todos los grupos, y en cada parcial solo se elige si se "
                 "muestra. (Esc para salir)"),
    "etiqueta": ("MODO ETIQUETA: arrastra entre dos cruces de guías de control para "
                 "crear una etiqueta en el grupo activo. (Esc para salir)"),
}

MODOS_DIBUJO = ("boton", "total", "etiqueta")