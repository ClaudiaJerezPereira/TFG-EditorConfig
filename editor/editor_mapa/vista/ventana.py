"""Ventana principal: barra de herramientas, lienzo y barra de estado.

La ventana no decide nada: construye los widgets y avisa al controlador de lo que
hace el usuario. Las acciones se le pasan en un diccionario para que la vista no
tenga que conocer los metodos del controlador.
"""
import tkinter as tk
from tkinter import ttk

from .apariencia import AYUDA, COL_MODO_ON, ESTADO_MODO
from .lienzo import VistaLienzo

# (clave del modo, texto del boton)
MODOS = (("grupo", "Grupo"), ("control", "Control"), ("boton", "Botón"),
         ("total", "Total"), ("etiqueta", "Etiqueta"))

# Botones de la primera fila que no son de modo: (texto, nombre de la accion)
BOTONES_ARCHIVO = (("Cargar mapa", "cargar_mapa"), ("Abrir XML", "abrir_xml"),
                   ("Guardar XML", "guardar_xml"), ("Exportar SQL", "exportar_sql"))
BOTONES_GUIAS = (("Guía coloc. V", "guia_col_v"), ("Guía coloc. H", "guia_col_h"),
                 ("Guía control V", "guia_ctrl_v"), ("Guía control H", "guia_ctrl_h"))
BOTONES_EDICION = (("Reflejar colocación", "reflejar"), ("Eliminar", "eliminar"))


class BarraFlexible(tk.Frame):
    """Barra de herramientas que pasa a la linea siguiente cuando no cabe.

    Los botones se colocan con `place`, midiendo lo que ocupa cada uno, y se
    recolocan cada vez que cambia el ancho de la ventana. Asi ningun boton queda
    fuera por estrechar la ventana, que es lo que pasaba con `pack(side=LEFT)`.
    """

    HUECO = 4      # margen vertical de cada linea

    def __init__(self, padre, **kw):
        super().__init__(padre, **kw)
        self._elementos = []
        self._ancho = None
        self.bind("<Configure>", lambda e: self._recolocar(e.width))

    def anadir(self, widget, pad=2, estirar=False):
        """`estirar` es para los separadores: no tienen alto propio y hay que darles
        el de la linea."""
        self._elementos.append((widget, pad, estirar))
        return widget

    def _recolocar(self, ancho):
        # Al cambiar nuestra altura llega otro <Configure> con el mismo ancho; sin
        # esta comprobacion nos meteriamos en un bucle.
        if ancho <= 1 or ancho == self._ancho or not self._elementos:
            return
        self._ancho = ancho
        alto_fila = max(w.winfo_reqheight() for w, _, _ in self._elementos) + self.HUECO
        x = y = 0
        for widget, pad, estirar in self._elementos:
            ocupa = widget.winfo_reqwidth() + 2 * pad
            if x > 0 and x + ocupa > ancho:
                x, y = 0, y + alto_fila
            if estirar:
                widget.place(x=x + pad, y=y + self.HUECO // 2,
                             height=alto_fila - self.HUECO)
            else:
                widget.place(x=x + pad, y=y + self.HUECO // 2)
            x += ocupa
        self.config(height=y + alto_fila)


class VentanaPrincipal:

    def __init__(self, root, modelo, acciones):
        """`acciones` es un diccionario nombre -> funcion sin argumentos."""
        self.root = root
        self.modelo = modelo
        self.acciones = acciones
        self.botones_modo = {}

        root.title("Editor de mapas de arbitraje")
        root.geometry("1280x800")
        # Por debajo de esto el lienzo se queda sin sitio util; las barras ya se
        # reparten solas en varias lineas.
        root.minsize(560, 420)

        self._barra()
        # La barra de estado se coloca ANTES que el lienzo: si no, el lienzo (que se
        # expande) se queda con todo el hueco y la deja sin sitio.
        self.estado = tk.Label(root, anchor="w", relief=tk.SUNKEN, bd=1, text=AYUDA)
        self.estado.pack(side=tk.BOTTOM, fill=tk.X)
        self.lienzo = VistaLienzo(root, modelo)

    # ------------------------------------------------------------------- WIDGETS
    def _barra(self):
        # Las barras reparten sus botones en varias lineas cuando la ventana no da
        # para todos: con pack(side=LEFT) a secas, al encoger la ventana los ultimos
        # se salian y no habia forma de llegar a ellos.
        fila1 = BarraFlexible(self.root, bd=1, relief=tk.RAISED)
        fila1.pack(side=tk.TOP, fill=tk.X)
        fila2 = BarraFlexible(self.root, bd=1, relief=tk.RAISED)
        fila2.pack(side=tk.TOP, fill=tk.X)

        def sep(barra):
            barra.anadir(tk.Frame(barra, width=2, bg="gray70"), pad=4, estirar=True)

        def boton(barra, texto, accion, **kw):
            barra.anadir(tk.Button(barra, text=texto, command=self.acciones[accion],
                                   **kw))

        # ---------- Fila 1: archivo, catalogos, modos, guias, edicion ----------
        for texto, accion in BOTONES_ARCHIVO:
            boton(fila1, texto, accion)
        fila1.anadir(tk.Button(fila1, text=" + ",
                               command=lambda: self.acciones["zoom"](1.25)))
        fila1.anadir(tk.Button(fila1, text=" − ",
                               command=lambda: self.acciones["zoom"](0.8)))

        sep(fila1)
        boton(fila1, "Catálogos", "catalogos")
        self.var_simetria = tk.BooleanVar(value=False)
        fila1.anadir(tk.Checkbutton(fila1, text="Simétrico", variable=self.var_simetria,
                                    command=self.acciones["simetria"]))

        sep(fila1)
        fila1.anadir(tk.Label(fila1, text="MODO:"))
        for clave, texto in MODOS:
            b = fila1.anadir(tk.Button(fila1, text=texto, width=8,
                                       command=lambda m=clave: self.acciones["modo"](m)),
                             pad=1)
            self.botones_modo[clave] = b
        self._bg_boton = self.botones_modo["grupo"].cget("background")

        sep(fila1)
        for texto, accion in BOTONES_GUIAS:
            boton(fila1, texto, accion)

        sep(fila1)
        for texto, accion in BOTONES_EDICION:
            boton(fila1, texto, accion)

        # ---------- Fila 2: el desplegable de grupos ----------
        fila2.anadir(tk.Label(fila2, text="Grupo activo:"))
        self.var_grupo = tk.StringVar()
        self.combo_grupo = ttk.Combobox(fila2, textvariable=self.var_grupo,
                                        state="readonly", width=24)
        fila2.anadir(self.combo_grupo)
        self.combo_grupo.bind("<<ComboboxSelected>>",
                              lambda e: self.acciones["elegir_grupo"]())
        fila2.anadir(tk.Button(fila2, text="Nuevo", command=self.acciones["nuevo_grupo"]))
        fila2.anadir(tk.Button(fila2, text="Colocar",
                               command=self.acciones["colocar_grupo"]))
        fila2.anadir(tk.Label(fila2, text="(un grupo puede llevar botones y etiquetas; "
                                          "el total es común a todo el mapa)", fg="#555"),
                     pad=8)

    # ---------------------------------------------------------------- REFRESCOS
    def marcar_modo(self, modo):
        for clave, b in self.botones_modo.items():
            b.config(background=COL_MODO_ON if clave == modo else self._bg_boton)

    def decir(self, texto):
        self.estado.config(text=texto)

    def decir_modo(self, modo):
        self.decir(ESTADO_MODO.get(modo, AYUDA))

    def refrescar_grupos(self):
        """Vuelca los grupos del modelo en el desplegable."""
        nombres = [t["nombre"] for t in self.modelo.tipos]
        self.combo_grupo["values"] = nombres
        if not nombres:
            self.var_grupo.set("")
            return
        if self.modelo.tipo_activo:
            self.var_grupo.set(self.modelo.nombre_tipo(self.modelo.tipo_activo))
        elif self.var_grupo.get() not in nombres:
            self.var_grupo.set(nombres[-1])

    def grupo_elegido(self):
        """Grupo seleccionado en el desplegable, o None."""
        t = self.modelo.tipo_por_nombre(self.var_grupo.get())
        return t["id"] if t else None