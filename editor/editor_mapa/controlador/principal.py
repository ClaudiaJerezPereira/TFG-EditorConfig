"""Controlador: traduce lo que hace el usuario en operaciones sobre el modelo.

Es el unico que conoce a la vez el modelo y la vista. Aqui viven el modo de
trabajo, la seleccion y el arrastre, que son estado de la edicion y no del
documento.
"""
import os
from xml.etree import ElementTree as ET

from PIL import Image
from tkinter import filedialog, messagebox, simpledialog

from ..modelo import ModeloMapa
from ..modelo.constantes import CATALOGOS_ID_AUTOMATICO, ID_MINIMO
from ..persistencia import sql_mapa, xml_io
from ..vista.apariencia import MARGEN_CRUCE, MODOS_DIBUJO, NOMBRE_CLASE
from ..vista.dialogos import (DialogoAccion, DialogoCatalogo, DialogoContenido,
                              DialogoGrupo, DialogoTotal, DialogoZona)
from ..vista.dialogos.catalogo import ESTILOS_FUENTE
from ..vista.ventana import VentanaPrincipal

# Atajos de teclado de cada modo. La "t" ya estaba cogida por Etiqueta, asi que el
# Total usa la "o".
ATAJOS_MODO = (("g", "grupo"), ("c", "control"), ("b", "boton"),
               ("t", "total"), ("e", "etiqueta"))

# Columnas de cada catalogo en su editor de tabla.
CATALOGOS = {
    # Los totales generales (General_Resultado) reservan los primeros
    # ID_GRUPO_ACCIONES, asi que su ID no se teclea: es la posicion en la lista.
    "totales": ("Totales generales", [("id", "ID", "int"),
                                      ("nombre", "Nombre", "str")]),
    "lados": ("Lados", [("id", "ID", "int"), ("nombre", "Nombre", "str"),
                        ("color_h", "Color H", "float"), ("color_s", "Color S", "float")]),
    "arbitros": ("Árbitros", [("id", "ID", "int"), ("nombre", "Nombre", "str"),
                              ("descripcion", "Descripción", "str")]),
    # La fuente, el estilo y el color se eligen de una lista: tecleados a mano es
    # facil poner una familia que no esta instalada o un estilo que Tk no entiende,
    # y entonces el texto se dibuja con la fuente de por defecto sin avisar.
    "estilos": ("Estilos de fuente",
                [("id", "ID", "int"), ("descripcion", "Descripción", "str"),
                 ("nombre_fuente", "Fuente", "fuente"),
                 ("estilo_fuente", "Estilo", "lista:" + "|".join(ESTILOS_FUENTE)),
                 ("tamano_fuente", "Tamaño", "int"), ("color_fuente", "Color", "color")]),
}


class Controlador:

    def __init__(self, root):
        self.root = root
        self.modelo = ModeloMapa()

        # --- Estado de la edicion (no del documento) ---
        # La SELECCION vive en el modelo (modelo.seleccion): la vista necesita
        # conocerla para resaltar, y asi no depende del controlador. Lo que se queda
        # aqui es lo puramente transitorio: el modo, el arrastre y el trazado.
        self.modo = "grupo"
        self.ruta_xml = None
        self._arrastre = None      # {"clase", "id", "off"} mientras se mueve una guia
        self._modo_pan = False     # desplazar el mapa con el raton
        self._modo_colocar = False
        self._colocar_nuevo = False
        self._cruce_inicio = None  # primer cruce al trazar un control
        self._preview = None       # rectangulo de previsualizacion
        self._ultimo_clic = None   # para recorrer elementos superpuestos

        self.vista = VentanaPrincipal(root, self.modelo, self._acciones())
        self.lienzo = self.vista.lienzo
        self._eventos()
        self.vista.marcar_modo(self.modo)

    def _acciones(self):
        return {
            "cargar_mapa": self.cargar_mapa,
            "abrir_xml": self.abrir_xml,
            "guardar_xml": self.guardar_xml,
            "exportar_sql": self.exportar_sql,
            "zoom": self.zoom,
            "catalogos": self.editar_catalogos,
            "simetria": self.cambiar_simetria,
            "modo": self.set_modo,
            "guia_col_v": lambda: self.anadir_guia_col("v"),
            "guia_col_h": lambda: self.anadir_guia_col("h"),
            "guia_ctrl_v": lambda: self.anadir_guia_ctrl("v"),
            "guia_ctrl_h": lambda: self.anadir_guia_ctrl("h"),
            "reflejar": self.reflejar,
            "eliminar": self.eliminar,
            "nuevo_grupo": self.nuevo_grupo,
            "colocar_grupo": self.colocar_grupo,
            "elegir_grupo": self.elegir_grupo,
        }

    def _eventos(self):
        cv = self.lienzo.canvas
        cv.bind("<ButtonPress-1>", self._on_press)
        cv.bind("<B1-Motion>", self._on_motion)
        cv.bind("<ButtonRelease-1>", self._on_release)
        cv.bind("<Double-Button-1>", self._on_double)
        for ev in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            cv.bind(ev, self._zoom_rueda)
        self.root.bind("<Delete>", lambda e: self.eliminar())
        self.root.bind("<Escape>", self._cancelar_modo)
        self.root.bind("<Control-s>", lambda e: self.guardar_xml())
        self.root.bind("<Control-o>", lambda e: self.abrir_xml())
        for tecla, m in ATAJOS_MODO:
            self.root.bind(tecla, lambda e, m=m: self._atajo_modo(m))

    # ------------------------------------------------------------------ UTILIDADES
    def redibujar(self):
        self.lienzo.redibujar()

    def seleccionar(self, clase, ident, redibujar=False):
        """Cambia la seleccion. Si solo cambia el resalte, se repinta ese resalte en
        vez de redibujar el mapa entero."""
        self.modelo.seleccionar(clase, ident)
        if redibujar:
            self.redibujar()
        else:
            self.lienzo.refrescar_seleccion()

    def decir(self, texto):
        self.vista.decir(texto)

    @property
    def instancia_activa(self):
        ident = self.modelo.instancia_activa
        return self.modelo.instancia(ident) if ident else None

    def margen_mapa(self):
        """El margen de enganche esta en pixeles de pantalla; aqui hace falta en
        pixeles del mapa."""
        return MARGEN_CRUCE / max(self.lienzo.escala, 1e-6)

    def _hay_mapa(self):
        if self.lienzo.imagen_original is None:
            messagebox.showinfo("Aviso", "Primero carga un mapa.")
            return False
        return True

    # ---------------------------------------------------------------------- MODOS
    def _atajo_modo(self, m):
        # Las letras sueltas no deben cambiar de modo si se esta escribiendo.
        foco = self.root.focus_get()
        if foco is not None and foco.winfo_class() in ("Entry", "TEntry", "TCombobox",
                                                       "Text", "Spinbox", "TSpinbox"):
            return
        self.set_modo(m)

    def set_modo(self, nuevo):
        if nuevo in MODOS_DIBUJO:
            # Los tres modos dibujan sobre el MISMO grupo activo: un grupo puede
            # llevar botones, etiquetas y un total.
            if not self.activar_grupo():
                return
            inst = self.instancia_activa
            if nuevo == "total" and self.modelo.hay_total():
                messagebox.showinfo(
                    "El mapa ya tiene total",
                    "La etiqueta del total es única y la misma para todos los grupos: "
                    "no se define grupo a grupo.\n\nSi quieres cambiarla de sitio o de "
                    "tamaño, selecciónala, elimínala (Supr) y vuelve a dibujarla; en "
                    "cada parcial puedes decidir si se muestra o no.")
                return
            n_v = len(self.modelo.guias_ctrl_tipo(inst["tipo"], "v"))
            n_h = len(self.modelo.guias_ctrl_tipo(inst["tipo"], "h"))
            if n_v < 2 or n_h < 2:
                messagebox.showinfo(
                    "Faltan guías de control",
                    "Necesitas al menos dos guías de control verticales y dos "
                    "horizontales\npara poder trazar un elemento entre sus cruces.")
                return
        self.modo = nuevo
        self._cancelar_transitorios()
        self.vista.marcar_modo(nuevo)
        self.vista.decir_modo(nuevo)
        self.redibujar()

    def _cancelar_transitorios(self):
        self._arrastre = None
        self._modo_pan = False
        self._cruce_inicio = None
        self._modo_colocar = False
        self._colocar_nuevo = False
        if self._preview is not None:
            self.lienzo.canvas.delete(self._preview)
            self._preview = None

    def _cancelar_modo(self, event=None):
        if self._modo_colocar:
            self._modo_colocar = False
            self._colocar_nuevo = False
            self.vista.decir_modo(self.modo)
            return
        # Esc sale de cualquier modo, no solo de los de dibujo: que en Control no
        # funcionara era una excepcion que nadie espera.
        if self.modo != "grupo":
            self.set_modo("grupo")

    def _clases_pickables(self):
        """En modo grupo solo se pinchan guias de colocacion, origenes y controles;
        en modo control, ademas, las guias de control."""
        if self.modo == "control":
            return ("control", "inst", "ctrl", "col")
        return ("control", "inst", "col")

    # ------------------------------------------------------------ MAPA Y ARCHIVOS
    def cargar_mapa(self):
        ruta = filedialog.askopenfilename(
            title="Selecciona la imagen del campo",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos", "*.*")])
        if not ruta:
            return
        try:
            img = Image.open(ruta)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la imagen:\n{e}")
            return
        self.lienzo.cargar_imagen(img)
        self.modelo.ruta_mapa = ruta
        self.modelo.dim_mapa = (img.width, img.height)
        if self.modelo.simetria:
            # El eje es el centro de la imagen: si cambia la imagen, cambia el eje y
            # hay que rehacer las parejas.
            self.modelo.emparejar()
        self.redibujar()
        self.decir(f"Mapa cargado: {os.path.basename(ruta)} "
                   f"({img.width}×{img.height} px).")

    def guardar_xml(self):
        if self.modelo.vacio():
            messagebox.showinfo("Nada que guardar",
                                "Todavía no hay guías ni grupos definidos.")
            return
        ruta = filedialog.asksaveasfilename(
            title="Guardar configuración", defaultextension=".xml",
            initialfile=os.path.basename(self.ruta_xml) if self.ruta_xml
            else "arbitraje.xml",
            filetypes=[("XML", "*.xml"), ("Todos", "*.*")])
        if not ruta:
            return
        try:
            xml_io.guardar(self.modelo, ruta)
        except OSError as e:
            messagebox.showerror("Error al guardar", f"No se pudo escribir:\n{e}")
            return
        self.ruta_xml = ruta
        self.decir(f"Configuración guardada en {os.path.basename(ruta)}.")

    def abrir_xml(self):
        ruta = filedialog.askopenfilename(title="Abrir configuración",
                                          filetypes=[("XML", "*.xml"), ("Todos", "*.*")])
        if not ruta:
            return
        try:
            raiz = ET.parse(ruta).getroot()
        except (ET.ParseError, OSError) as e:
            messagebox.showerror("Error al abrir", f"No se pudo leer el XML:\n{e}")
            return

        ruta_mapa, errores = xml_io.cargar(self.modelo, raiz)
        self.ruta_xml = ruta

        # La imagen del campo se recupera si sigue estando donde se guardo.
        if ruta_mapa and os.path.exists(ruta_mapa):
            try:
                img = Image.open(ruta_mapa)
                self.lienzo.cargar_imagen(img)
                self.modelo.ruta_mapa = ruta_mapa
                self.modelo.dim_mapa = (img.width, img.height)
            except Exception as e:
                errores.append(f"No se pudo abrir la imagen del mapa:\n{e}")
        elif ruta_mapa:
            errores.append(f"No se encuentra la imagen del mapa:\n{ruta_mapa}\n"
                           f"Cárgala con 'Cargar mapa'.")

        # Ya se conoce la imagen: se rehacen las parejas simetricas por geometria.
        if self.modelo.simetria and self.modelo.eje() is None:
            errores.append("El archivo tenía la simetría activada, pero sin la imagen "
                           "del campo no se puede saber dónde está el eje: se ha "
                           "desactivado.")
            self.modelo.simetria = False
        if self.modelo.simetria:
            self.modelo.emparejar()

        # Un archivo puede traer referencias a filas de catalogo que no estan en el.
        errores += self.modelo.depurar_catalogos()

        self.modo = "grupo"
        self.modelo.limpiar_seleccion()
        self._cancelar_transitorios()
        self.vista.var_simetria.set(self.modelo.simetria)
        self.vista.marcar_modo(self.modo)
        self.vista.refrescar_grupos()
        self.redibujar()
        self.lienzo.canvas.xview_moveto(0)
        self.lienzo.canvas.yview_moveto(0)
        self.decir(f"Cargado {os.path.basename(ruta)}: {self.modelo.resumen()}")
        if errores:
            messagebox.showwarning("Cargado con avisos",
                                   "El archivo se ha cargado, pero:\n\n• "
                                   + "\n• ".join(errores))

    def exportar_sql(self):
        m = self.modelo
        if m.vacio():
            messagebox.showinfo("Nada que exportar",
                                "Todavía no hay guías ni grupos definidos.")
            return
        base = os.path.splitext(os.path.basename(self.ruta_xml))[0] if self.ruta_xml \
            else "eurobot_ACCIONES"
        ruta = filedialog.asksaveasfilename(
            title="Exportar a SQL", defaultextension=".sql",
            initialfile=f"{base}.sql",
            filetypes=[("SQL", "*.sql"), ("Todos", "*.*")])
        if not ruta:
            return
        try:
            avisos = sql_mapa.guardar_edicion(m, ruta)
        except OSError as e:
            messagebox.showerror("Error al exportar", f"No se pudo escribir:\n{e}")
            return
        n_b = sum(1 for c in m.controles if c["clase"] == "boton")
        n_e = sum(1 for c in m.controles if c["clase"] == "etiqueta")
        self.decir(f"Exportado a {os.path.basename(ruta)}: {len(m.tipos)} grupo(s), "
                   f"{n_b} botón(es), {n_e} etiqueta(s) y {len(m.instancias)} parcial(es), "
                   f"más los cuatro catálogos.")
        if avisos:
            messagebox.showwarning("Exportado con avisos",
                                   "El archivo se ha generado, pero:\n\n• "
                                   + "\n• ".join(avisos))

    # --------------------------------------------------------------------- ZOOM
    def zoom(self, factor, ancla=None):
        """`ancla` es el punto de la ventana que debe quedarse quieto: el del cursor
        cuando se usa la rueda, y el centro de lo que se ve con los botones + y -.
        Sin esto, al cambiar la escala la vista se iba a la esquina superior
        izquierda y perdias de vista la zona en la que estabas trabajando."""
        if self.lienzo.imagen_original is None:
            return
        nueva = self.lienzo.escala * factor
        if nueva < 0.1 or nueva > 8.0:
            return
        if ancla is None:
            ancla = (self.lienzo.canvas.winfo_width() / 2,
                     self.lienzo.canvas.winfo_height() / 2)
        fijo = self.lienzo.punto_mapa(*ancla)
        self.lienzo.escala = nueva
        self.redibujar()
        self.lienzo.anclar(fijo, *ancla)

    def _zoom_rueda(self, event):
        ancla = (event.x, event.y)
        if event.num == 4 or getattr(event, "delta", 0) > 0:
            self.zoom(1.1, ancla)
        elif event.num == 5 or getattr(event, "delta", 0) < 0:
            self.zoom(0.9, ancla)

    # -------------------------------------------------------------------- GUIAS
    def anadir_guia_col(self, orient):
        if not self._hay_mapa():
            return
        cx, cy = self.lienzo.centro_visible()
        g = self.modelo.anadir_guia_colocacion(orient, cx if orient == "v" else cy)
        self.modelo.seleccionar("col", g["id"])
        self.redibujar()

    def anadir_guia_ctrl(self, orient):
        if not self._hay_mapa():
            return
        inst = self.instancia_activa
        if inst is None:
            messagebox.showinfo("Sin grupo activo",
                                "Coloca o activa primero un grupo (necesito su origen "
                                "para medir la distancia de la guía de control).")
            return
        cx, cy = self.lienzo.centro_visible()
        gk = self.modelo.anadir_guia_control(inst, orient, cx, cy)
        self.modelo.seleccionar("ctrl", gk["id"])
        self.redibujar()

    # ------------------------------------------------------------------- GRUPOS
    def activar_grupo(self, exigir_instancia=True):
        """Pone como activo el grupo elegido en el desplegable."""
        tid = self.vista.grupo_elegido()
        if tid is None:
            messagebox.showinfo("Sin grupo",
                                "No hay ningún grupo. Créalo con el botón 'Nuevo'.")
            return False
        insts = self.modelo.instancias_tipo(tid)
        if exigir_instancia and not insts:
            messagebox.showinfo("Grupo sin colocar",
                                f"El grupo '{self.modelo.nombre_tipo(tid)}' todavía no "
                                f"está colocado.\nPulsa 'Colocar' y haz clic en un cruce "
                                f"de guías de colocación.")
            return False
        self.modelo.tipo_activo = tid
        if insts and (self.modelo.instancia_activa is None
                      or self.modelo.instancia(self.modelo.instancia_activa)["tipo"] != tid):
            self.modelo.instancia_activa = insts[-1]["id"]
        self.vista.refrescar_grupos()
        return True

    def elegir_grupo(self):
        tid = self.vista.grupo_elegido()
        if tid is None:
            return
        self.modelo.tipo_activo = tid
        insts = self.modelo.instancias_tipo(tid)
        self.modelo.instancia_activa = insts[-1]["id"] if insts else None
        if insts:
            self.modelo.seleccionar("inst", self.modelo.instancia_activa)
        else:
            self.modelo.limpiar_seleccion()
        self.redibujar()
        nombre = self.modelo.nombre_tipo(tid)
        if not insts:
            self.decir(f"Grupo activo: '{nombre}' (sin colocar). Pulsa 'Colocar' y haz "
                       f"clic en un cruce.")
        else:
            self.decir(f"Grupo activo: '{nombre}' ({len(insts)} colocación(es)).")

    def nuevo_grupo(self):
        if not self._hay_mapa():
            return
        m = self.modelo
        n_v = sum(1 for g in m.guias_col if g["orient"] == "v")
        n_h = sum(1 for g in m.guias_col if g["orient"] == "h")
        if n_v < 1 or n_h < 1:
            messagebox.showinfo("Faltan guías de colocación",
                                "Añade al menos una guía de colocación vertical y otra "
                                "horizontal;\nsu cruce marcará el origen del grupo.")
            return
        r = DialogoGrupo(self.root, nombre=f"Grupo {len(m.tipos) + 1}",
                         existentes=[t["nombre"] for t in m.tipos]).resultado
        if r is None:
            return
        m.crear_grupo(r["nombre"], r["comun"])
        self._modo_colocar = True
        self._colocar_nuevo = True
        self.modo = "grupo"
        self.vista.marcar_modo(self.modo)
        self.vista.refrescar_grupos()
        self.decir(f"Grupo '{r['nombre']}' creado. Haz clic en un CRUCE de guías de "
                   f"colocación para fijar su origen. (Esc para cancelar)")

    def colocar_grupo(self):
        if not self.activar_grupo(exigir_instancia=False):
            return
        self._modo_colocar = True
        self._colocar_nuevo = False
        self.modo = "grupo"
        self.vista.marcar_modo(self.modo)
        self.decir(f"Colocando '{self.modelo.nombre_tipo(self.modelo.tipo_activo)}': haz "
                   f"clic en un cruce de guías de colocación. (Esc para cancelar)")

    def _press_colocar(self, event):
        x, y = self.lienzo.a_mapa(event)
        gv, gh = self.modelo.guia_col_cercana(x, y, self.margen_mapa())
        if gv is None or gh is None:
            messagebox.showwarning("Fuera de un cruce",
                                   "El clic no cae sobre un cruce de guías de "
                                   "colocación (a menos de 10 px).")
            self._modo_colocar = False
            self._colocar_nuevo = False
            return
        inst, espejo = self.modelo.colocar_grupo(self.modelo.tipo_activo, gv, gh)
        self.modelo.seleccionar("inst", inst["id"])
        self.vista.refrescar_grupos()

        es_nuevo = self._colocar_nuevo
        self._modo_colocar = False
        self._colocar_nuevo = False
        aviso = " También se ha colocado su reflejo al otro lado." if espejo else ""
        if es_nuevo:
            self.modo = "control"
            self.decir("Grupo colocado. MODO CONTROL: añade guías de control "
                       "(Guía control V/H) y luego botones o etiquetas." + aviso)
        else:
            self.modo = "grupo"
            self.decir(f"Colocada otra copia de "
                       f"'{self.modelo.nombre_tipo(inst['tipo'])}'.{aviso}")
        self.vista.marcar_modo(self.modo)
        self.redibujar()

    def reflejar(self):
        ident = self.modelo.seleccionado("inst")
        if ident is None and self.modelo.instancia_activa is not None:
            ident = self.modelo.instancia_activa
        if ident is None:
            messagebox.showinfo("Sin colocación",
                                "Selecciona la colocación de un grupo (su origen) para "
                                "reflejarla.")
            return
        inst = self.modelo.instancia(ident)
        inv = self.modelo.reflejar(inst)
        self.modelo.instancia_activa = ident
        self.modelo.tipo_activo = inst["tipo"]
        self.redibujar()
        estado = "reflejada (espejo horizontal)" if inv else "normal"
        self.decir(f"Colocación {ident} de "
                   f"'{self.modelo.nombre_tipo(inst['tipo'])}': {estado}.")

    # ----------------------------------------------------------------- SIMETRIA
    def cambiar_simetria(self):
        m = self.modelo
        if self.vista.var_simetria.get():
            if self.lienzo.imagen_original is None:
                messagebox.showinfo("Falta el mapa",
                                    "Carga primero la imagen del campo: el eje de "
                                    "simetría es su centro.")
                self.vista.var_simetria.set(False)
                return
            m.simetria = True
            n_g, n_i = m.aplicar_simetria()
            self.decir(f"Simetría ACTIVADA (eje en x = {m.eje():g}). Añadidas {n_g} "
                       f"guía(s) y {n_i} colocación(es) reflejadas. Lo que dibujes a "
                       f"partir de ahora aparecerá también al otro lado.")
        else:
            n_g, n_i = m.contar_automaticos()
            if (n_g or n_i) and not messagebox.askyesno(
                    "Desactivar la simetría",
                    f"Se eliminarán los elementos creados por la simetría: {n_g} guía(s) "
                    f"de colocación y {n_i} colocación(es) de grupo, junto con los "
                    f"cambios que hayas hecho en ellas.\n\n¿Continuar?"):
                self.vista.var_simetria.set(True)
                return
            m.quitar_simetria()
            self.decir("Simetría desactivada. Lo reflejado se ha eliminado.")
        self.redibujar()

    # ---------------------------------------------------------------- CATALOGOS
    def editar_catalogos(self):
        from ..vista.dialogos.catalogo import menu_catalogos
        menu_catalogos(self.root, self._editar_catalogo)

    def _editar_catalogo(self, cual):
        titulo, columnas = CATALOGOS[cual]
        actual = getattr(self.modelo.catalogos, cual)
        # El ID minimo es el mismo en los cuatro catalogos (ID_MINIMO en
        # modelo/constantes.py): 1, porque es la clave primaria de la tabla.
        r = DialogoCatalogo(self.root, titulo, columnas, actual,
                            muestra_fuente=(cual == "estilos"),
                            id_minimo=ID_MINIMO,
                            id_automatico=(cual in CATALOGOS_ID_AUTOMATICO)).resultado
        if r is None:
            return
        setattr(self.modelo.catalogos, cual, r)
        if cual in CATALOGOS_ID_AUTOMATICO:
            self.modelo.catalogos.renumerar_totales()
        # Si se ha borrado alguna fila, hay quien puede estar apuntando a ella.
        cambios = self.modelo.depurar_catalogos()
        self.redibujar()
        if cambios:
            messagebox.showinfo(
                "Referencias actualizadas",
                "Al cambiar el catálogo, esto usaba filas que ya no existen:\n\n• "
                + "\n• ".join(cambios))
        self.decir(f"Catálogo '{titulo}' actualizado."
                   + (f" {len(cambios)} referencia(s) corregida(s)." if cambios else ""))

    # ------------------------------------------------------- ANADIR UN ELEMENTO
    def _press_anadir(self, event):
        inst = self.instancia_activa
        if inst is None:
            self.set_modo("grupo")
            return
        x, y = self.lienzo.a_mapa(event)
        gv, gh = self.modelo.cruce_ctrl(inst, x, y, self.margen_mapa())
        if gv is None or gh is None:
            # Sin cruce bajo el cursor: en vez de avisar, permite desplazar el mapa.
            self._cruce_inicio = None
            self._modo_pan = True
            self.lienzo.canvas.scan_mark(event.x, event.y)
            return
        self._cruce_inicio = (gv, gh)
        px, py = self.lienzo.a_pantalla(self.modelo.pos_ctrl_abs(inst, gv),
                                        self.modelo.pos_ctrl_abs(inst, gh))
        self._preview = self.lienzo.canvas.create_rectangle(
            px, py, px, py, outline="#d11", dash=(3, 2), width=2)

    def _motion_anadir(self, event):
        inst = self.instancia_activa
        x, y = self.lienzo.a_mapa(event)
        gv0, gh0 = self._cruce_inicio
        x0, y0 = self.lienzo.a_pantalla(self.modelo.pos_ctrl_abs(inst, gv0),
                                        self.modelo.pos_ctrl_abs(inst, gh0))
        gv, gh = self.modelo.cruce_ctrl(inst, x, y, self.margen_mapa())
        if gv and gh:
            x1, y1 = self.lienzo.a_pantalla(self.modelo.pos_ctrl_abs(inst, gv),
                                            self.modelo.pos_ctrl_abs(inst, gh))
        else:
            x1 = self.lienzo.canvas.canvasx(event.x)
            y1 = self.lienzo.canvas.canvasy(event.y)
        self.lienzo.canvas.coords(self._preview, x0, y0, x1, y1)

    def _release_anadir(self, event):
        if self._preview is not None:
            self.lienzo.canvas.delete(self._preview)
            self._preview = None
        if self._cruce_inicio is None:
            return
        m = self.modelo
        inst = self.instancia_activa
        x, y = self.lienzo.a_mapa(event)
        gv0, gh0 = self._cruce_inicio
        self._cruce_inicio = None
        gv, gh = m.cruce_ctrl(inst, x, y, self.margen_mapa())

        if gv is None or gh is None:
            messagebox.showwarning("Fuera de un cruce",
                                   "Has soltado fuera de un cruce de guías de control. "
                                   "Inténtalo de nuevo.")
            return
        if gv["id"] == gv0["id"]:
            messagebox.showwarning("Anchura cero",
                                   "Misma guía vertical: el control tendría anchura 0.")
            return
        if gh["id"] == gh0["id"]:
            messagebox.showwarning("Altura cero",
                                   "Misma guía horizontal: el control tendría altura 0.")
            return

        tid = inst["tipo"]
        grupo = m.nombre_tipo(tid)
        # Nombre por defecto: <grupo><n>, como en el XML de ejemplo (Tribuna1...).
        base = f"{grupo}{len(m.controles_tipo(tid)) + 1}"
        # Tamano real del recuadro, para que las vistas previas sean fieles.
        ancho = abs(m.guia_ctrl(gv["id"])["rel"] - m.guia_ctrl(gv0["id"])["rel"])
        alto = abs(m.guia_ctrl(gh["id"])["rel"] - m.guia_ctrl(gh0["id"])["rel"])

        if self.modo == "total":
            # El total no cuelga del grupo: se guarda su rectangulo respecto al origen
            # y sale igual en todos. No tiene parametros propios (su texto lo calcula
            # la aplicacion de arbitraje, y la fuente y el color son los del parcial).
            if m.hay_total():
                messagebox.showinfo("El mapa ya tiene total",
                                    "La etiqueta del total es única para todo el mapa.")
                self.set_modo("grupo")
                return
            x = min(m.guia_ctrl(gv0["id"])["rel"], m.guia_ctrl(gv["id"])["rel"])
            y = min(m.guia_ctrl(gh0["id"])["rel"], m.guia_ctrl(gh["id"])["rel"])
            t = m.poner_total(x, y, ancho, alto, nombre="Total")
            m.seleccionar("control", t["id"])
            self.set_modo("grupo")
            m.seleccionar("control", t["id"])
            self.redibujar()
            self.decir("Etiqueta de total definida: queda anclada a esas cuatro guías "
                       "de control, así que se mueve y se redimensiona arrastrándolas. "
                       "Es la misma para todos los grupos; en los parciales donde no "
                       "la quieras, desmárcala en el parcial.")
            return
        if self.modo == "etiqueta":
            r = DialogoContenido(self.root, nombre=base, param=m.param_etiqueta(),
                                 contenido=m.contenido_etiqueta(),
                                 estilos=m.catalogos.estilos, lados=m.catalogos.lados,
                                 tam_control=(ancho, alto),
                                 lado_parcial=inst.get("param", {}).get("lado"),
                                 ruta_grafico=m.ruta_grafico,
                                 carpeta_graficos=m.carpeta_graficos).resultado
            if r is None:
                return
            nombre, contenido, param = r["nombre"], r["contenido"], r["param"]
        else:
            pz = inst.get("param", {})
            r = DialogoAccion(self.root, nombre=base, param=m.param_accion(),
                              estilos=m.catalogos.estilos,
                              tam_control=(ancho, alto),
                              lados=m.catalogos.lados,
                              lado_parcial=pz.get("lado"),
                              color_v=pz.get("color_v", 255),
                              ruta_grafico=m.ruta_grafico,
                              carpeta_graficos=m.carpeta_graficos).resultado
            if r is None:
                return
            nombre, param, contenido = r["nombre"], r["param"], r["contenido"]

        c = m.anadir_control(tid, self.modo, nombre, gv0["id"], gv["id"],
                             gh0["id"], gh["id"], contenido, param)
        m.seleccionar("control", c["id"])
        self.redibujar()
        que = NOMBRE_CLASE.get(self.modo, "Elemento")
        self.decir(f"{que} añadido a '{grupo}'. Sigues en MODO {que.upper()} "
                   f"(Esc para salir).")

    # ------------------------------------------------------------------ ELIMINAR
    def eliminar(self):
        if self.modelo.seleccion is None:
            return
        m = self.modelo
        clase, ident = m.seleccion

        if clase == "col":
            # Con la simetria activada, las dos guias de la pareja se borran juntas:
            # si no, quedaria un lado del campo sin su reflejo.
            n_guias, dep = m.dependientes_guia_col(ident)
            aviso = "Esta guía y su simétrica se eliminarán.\n" if n_guias > 1 else ""
            if (dep or n_guias > 1) and not messagebox.askyesno(
                    "Eliminar guía de colocación",
                    f"{aviso}{len(dep)} colocación(es) de grupo usan esta guía como "
                    f"origen y se eliminarán.\n¿Continuar?"):
                return
            m.eliminar_guia_col(ident)
        elif clase == "inst":
            m.eliminar_instancia(ident)
        elif clase == "ctrl":
            if m.es_guia_cero(ident):
                messagebox.showinfo(
                    "Eje del origen",
                    "Esa guía es uno de los dos ejes del origen del grupo y no se "
                    "puede eliminar: el resto del mapa la necesita como referencia.\n\n"
                    "Las guías de control que dibujes tú sí se pueden mover y borrar.")
                return
            dep = m.dependientes_guia_ctrl(ident)
            hay_total = any(c.get("clase") == "total" for c in dep)
            aviso_total = ("\n\nUno de ellos es la etiqueta del TOTAL, que es única "
                           "para todo el mapa: desaparecerá de todos los grupos."
                           if hay_total else "")
            if dep and not messagebox.askyesno(
                    "Eliminar guía de control",
                    f"Esta guía define {len(dep)} elemento(s) del grupo (en todas sus "
                    f"copias) que también se eliminarán.{aviso_total}\n¿Continuar?"):
                return
            m.eliminar_guia_ctrl(ident)
        elif clase == "control":
            c = m.control(ident)
            if c is not None and c["clase"] == "total" and not messagebox.askyesno(
                    "Eliminar la etiqueta del total",
                    "La etiqueta del total es única para todo el mapa: se eliminará "
                    "de todos los grupos.\n¿Continuar?"):
                return
            m.eliminar_control(ident)

        self.vista.refrescar_grupos()
        self.redibujar()

    # -------------------------------------------------------------------- RATON
    def _elegir_candidato(self, event, clases):
        """Elige un elemento entre los que hay bajo el cursor. Si se vuelve a hacer
        clic casi en el mismo punto, pasa al SIGUIENTE de la pila, de modo que a base
        de clics se recorren todos los que estan superpuestos."""
        candidatos = self.lienzo.candidatos(event, clases)
        if not candidatos:
            self._ultimo_clic = None
            return None, None, None

        x, y = event.x, event.y
        mismo_punto = (self._ultimo_clic is not None
                       and abs(self._ultimo_clic[0] - x) <= 3
                       and abs(self._ultimo_clic[1] - y) <= 3)
        idx = 0
        if mismo_punto and self.modelo.seleccion is not None:
            actuales = [i for i, c in enumerate(candidatos)
                        if (c[0], c[1]) == self.modelo.seleccion]
            if actuales:
                idx = (actuales[0] + 1) % len(candidatos)
        self._ultimo_clic = (x, y)

        if len(candidatos) > 1:
            self.decir(f"{len(candidatos)} elementos superpuestos aquí: seleccionado "
                       f"{candidatos[idx][1]}. Vuelve a hacer clic en el mismo punto "
                       f"para el siguiente.")
        return candidatos[idx]

    def _on_press(self, event):
        if self._modo_colocar:
            self._press_colocar(event)
            return
        if self.modo in MODOS_DIBUJO:
            self._press_anadir(event)
            return
        self._press_seleccion(event)

    def _press_seleccion(self, event):
        m = self.modelo
        clase, ident, inst_id = self._elegir_candidato(event, self._clases_pickables())
        cx = self.lienzo.canvas.canvasx(event.x)
        cy = self.lienzo.canvas.canvasy(event.y)

        if clase == "control":
            # Activar otra colocacion cambia las guias de control visibles, asi que
            # entonces hay que redibujar; si ya estaba activa, basta con el resalte.
            cambio = m.activar(inst_id)
            if cambio:
                self.vista.refrescar_grupos()
            self.seleccionar("control", ident, redibujar=cambio)
            c = m.control(ident)
            que = NOMBRE_CLASE.get(c["clase"], "Elemento")
            self.decir(f"{que} '{c.get('nombre', '')}' seleccionado. Doble clic para "
                       f"renombrarlo o cambiar sus parámetros.")

        elif clase == "inst":
            cambio = m.activar(ident)
            if cambio:
                self.vista.refrescar_grupos()
            self.seleccionar("inst", ident, redibujar=cambio)

        elif clase == "ctrl":
            gk = m.guia_ctrl(ident)
            if m.es_guia_cero(ident):
                # Es uno de los ejes del origen: su posicion no es un dato libre.
                m.seleccionar("ctrl", ident)
                self.redibujar()
                self.decir("Esa guía es un eje del origen del grupo y no se mueve. "
                           "Para desplazar el grupo, arrastra su guía de colocación.")
                return
            pos = m.pos_ctrl_abs(self.instancia_activa, gk) * self.lienzo.escala
            off = (cx - pos) if gk["orient"] == "v" else (cy - pos)
            self._arrastre = {"clase": "ctrl", "id": ident, "off": off}
            self.seleccionar("ctrl", ident)

        elif clase == "col":
            g = m.guia_col(ident)
            pos = g["pos"] * self.lienzo.escala
            off = (cx - pos) if g["orient"] == "v" else (cy - pos)
            self._arrastre = {"clase": "col", "id": ident, "off": off}
            self.seleccionar("col", ident)

        else:
            # Clic en zona vacia: deselecciona y DESACTIVA el grupo activo.
            habia_activa = m.instancia_activa is not None
            m.limpiar_seleccion()
            m.instancia_activa = None
            if habia_activa:
                self.redibujar()      # desaparecen las guias de control
            else:
                self.lienzo.refrescar_seleccion()
            self._modo_pan = True
            self.lienzo.canvas.scan_mark(event.x, event.y)

    def _on_motion(self, event):
        if self.modo in MODOS_DIBUJO and self._cruce_inicio:
            self._motion_anadir(event)
            return
        if self._modo_pan:
            self.lienzo.canvas.scan_dragto(event.x, event.y, gain=1)
            return
        if self._arrastre is None:
            return

        m = self.modelo
        cx = self.lienzo.canvas.canvasx(event.x)
        cy = self.lienzo.canvas.canvasy(event.y)
        if self._arrastre["clase"] == "col":
            g = m.guia_col(self._arrastre["id"])
            coord = cx if g["orient"] == "v" else cy
            m.mover_guia_col(g, (coord - self._arrastre["off"]) / self.lienzo.escala)
        else:
            gk = m.guia_ctrl(self._arrastre["id"])
            coord = cx if gk["orient"] == "v" else cy
            m.mover_guia_ctrl(gk, self.instancia_activa,
                              (coord - self._arrastre["off"]) / self.lienzo.escala)
        self.lienzo.repintar_vectores()

    def _on_release(self, event):
        if self.modo in MODOS_DIBUJO and (self._cruce_inicio is not None
                                          or self._preview is not None):
            self._release_anadir(event)
            return
        if self._modo_pan:
            self._modo_pan = False
            return
        if self._arrastre is not None:
            self._arrastre = None
            self.redibujar()

    # --------------------------------------------------------------- DOBLE CLIC
    def _on_double(self, event):
        # Doble clic sobre una guia: escribir su posicion exacta en pixeles.
        # Doble clic sobre un elemento: editar sus parametros.
        if self._modo_colocar or self.modo not in ("grupo", "control"):
            return
        self._arrastre = None
        self._modo_pan = False
        # Actua sobre lo que ya haya seleccionado el clic anterior; asi, con elementos
        # superpuestos, se edita exactamente el que se ve resaltado.
        candidatos = self.lienzo.candidatos(event, self._clases_pickables())
        elegido = next((c for c in candidatos
                        if (c[0], c[1]) == self.modelo.seleccion), None)
        if elegido is None:
            elegido = candidatos[0] if candidatos else (None, None, None)
        clase, ident, inst_id = elegido

        if clase == "col":
            self._editar_guia_col(ident)
        elif clase == "ctrl":
            self._editar_guia_ctrl(ident)
        elif clase == "inst":
            self._editar_parcial(ident)
        elif clase == "control":
            self._editar_control(ident, inst_id)

    def _editar_guia_col(self, ident):
        g = self.modelo.guia_col(ident)
        eje = "X" if g["orient"] == "v" else "Y"
        valor = simpledialog.askfloat(
            "Posición de la guía de colocación",
            f"Guía {ident} ({eje}) — posición en el mapa, en píxeles:",
            initialvalue=round(g["pos"], 2), parent=self.root)
        if valor is None:
            return
        self.modelo.mover_guia_col(g, valor)
        self.modelo.seleccionar("col", ident)
        self.redibujar()
        self.decir(f"Guía {ident} colocada en {eje} = {valor:g} px.")

    def _editar_guia_ctrl(self, ident):
        if self.modelo.instancia_activa is None:
            return
        gk = self.modelo.guia_ctrl(ident)
        if self.modelo.es_guia_cero(ident):
            self.decir("Esa guía es un eje del origen del grupo: su distancia al "
                       "origen es siempre 0 y no se edita.")
            return
        sentido = "derecha" if gk["orient"] == "v" else "abajo"
        valor = simpledialog.askfloat(
            "Distancia de la guía de control",
            f"Guía {ident} — distancia al origen del grupo, en píxeles\n"
            f"(positivo = hacia la {sentido}):",
            initialvalue=round(gk["rel"], 2), parent=self.root)
        if valor is None:
            return
        # Por el modelo, no tocando "rel" a mano: si la guía enmarca la etiqueta del
        # total, hay que arrastrar a la vez las de los demás grupos.
        movidas = self.modelo.colocar_guia_ctrl(gk, valor)
        self.modelo.seleccionar("ctrl", ident)
        self.redibujar()
        self.decir(f"Guía {ident} a {valor:g} px del origen."
                   + (f" La etiqueta del total se ha ajustado en "
                      f"{len(movidas)} grupo(s) más." if movidas else ""))

    def _editar_parcial(self, ident):
        # Se editan los parametros del parcial y, de paso, el grupo al que pertenece
        # (nombre y "Comun"), ya que el grupo no tiene otro sitio donde editarse.
        m = self.modelo
        inst = m.instancia(ident)
        t = m.tipo(inst["tipo"])
        param = dict(m.param_zona())
        param.update(inst.get("param", {}))
        r = DialogoZona(self.root, nombre=inst.get("nombre", ""), param=param,
                        inv=inst.get("inv", False), lados=m.catalogos.lados,
                        arbitros=m.catalogos.arbitros, estilos=m.catalogos.estilos,
                        grupo_nombre=t["nombre"], grupo_comun=t.get("comun", False),
                        grupos_existentes=[g["nombre"] for g in m.tipos],
                        geom_total=m.geom_total()).resultado
        if r is None:
            return
        espejo = m.renombrar_inst(inst, r["nombre"])
        inst["inv"] = r["inv"]
        inst["param"] = r["param"]
        t["nombre"] = r["grupo_nombre"]
        t["comun"] = r["grupo_comun"]
        m.seleccionar("inst", ident)
        self.vista.refrescar_grupos()
        self.redibujar()
        if espejo is not None:
            self.decir(f"Su colocación simétrica pasa a llamarse "
                       f"'{espejo['nombre']}'.")

    def _editar_control(self, ident, inst_id):
        m = self.modelo
        c = m.control(ident)
        if c["clase"] == "total":
            # La etiqueta del total es una sola para todo el mapa, pero el estilo y el
            # desplazamiento son de cada grupo (Arbitraje_TotalGrupoAcciones), asi que
            # se editan los de la copia sobre la que se ha hecho doble clic. Si no se
            # sabe de que colocacion es, se usa el grupo activo.
            inst = m.instancia(inst_id) if inst_id else None
            if inst is None:
                inst = m.instancia(m.instancia_activa) if m.instancia_activa else None
            if inst is None:
                self.decir("Haz doble clic sobre la etiqueta del total de una "
                           "colocación: su tipo de letra es del grupo que la dibuja.")
                return
            tid = inst["tipo"]
            r = DialogoTotal(self.root, nombre=c.get("nombre", ""),
                             grupo_nombre=m.nombre_tipo(tid),
                             estilos=m.catalogos.estilos,
                             total_estilo=m.estilo_total(tid),
                             total_d=m.desp_total(tid),
                             geom_total=m.geom_total()).resultado
            if r is None:
                return
            c["nombre"] = r["nombre"]
            t = m.tipo(tid)
            t["total_estilo"] = r["total_estilo"]
            t["total_d"] = r["total_d"]
            m.seleccionar("control", ident)
            self.redibujar()
            self.decir(f"Etiqueta de total '{c['nombre']}' actualizada en el grupo "
                       f"'{m.nombre_tipo(tid)}'.")
            return

        if c["clase"] == "etiqueta":
            param = dict(m.param_etiqueta())
            param.update(c.get("param", {}))
            inst = m.instancia(inst_id) if inst_id else None
            r = DialogoContenido(self.root, contenido=c["contenido"],
                                 nombre=c.get("nombre", ""), param=param,
                                 estilos=m.catalogos.estilos, lados=m.catalogos.lados,
                                 tam_control=m.tam_control(c),
                                 lado_parcial=(inst or {}).get("param", {}).get("lado"),
                                 ruta_grafico=m.ruta_grafico,
                                 carpeta_graficos=m.carpeta_graficos).resultado
        else:
            param = dict(m.param_accion())
            param.update(c.get("param", {}))
            pz = ((m.instancia(inst_id) if inst_id else None) or {}).get("param", {})
            r = DialogoAccion(self.root, nombre=c.get("nombre", ""), param=param,
                              estilos=m.catalogos.estilos, contenido=c["contenido"],
                              tam_control=m.tam_control(c),
                              lados=m.catalogos.lados,
                              lado_parcial=pz.get("lado"),
                              color_v=pz.get("color_v", 255),
                              ruta_grafico=m.ruta_grafico,
                              carpeta_graficos=m.carpeta_graficos).resultado
        if r is None:
            return
        antiguo = c.get("nombre", "")
        c["nombre"] = r["nombre"]
        c["contenido"] = r["contenido"]
        c["param"] = r["param"]
        m.seleccionar("control", ident)
        self.redibujar()
        que = NOMBRE_CLASE.get(c["clase"], "Elemento")
        if antiguo != r["nombre"]:
            self.decir(f"{que} renombrado: '{antiguo}' → '{r['nombre']}'.")
        else:
            self.decir(f"{que} '{r['nombre']}' actualizado.")