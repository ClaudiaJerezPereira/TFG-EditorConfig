"""Vista del mapa: dibuja el modelo sobre un Canvas de tkinter.

Solo LEE del modelo; no lo modifica nunca. El zoom (la escala) es cosa suya: el
modelo trabaja siempre en pixeles del mapa.
"""
import os
import tkinter as tk

from PIL import ImageTk

from ..modelo.geometria import MARGEN_TEXTO, reparto_icono
from .apariencia import (BORDE_CLASE, COL_BOTON, COL_COLOCACION, COL_CONTROL,
                         COL_DESBORDE, COL_EJE, COL_ETQ_CAMPO, COL_ETQ_GRAFICO,
                         COL_ETQ_TEXTO, COL_MARCA_BOOL, COL_ORIGEN, COL_SEL,
                         COL_TOTAL, FUENTE, MARCA_BOOL)
from .fuentes import (cabe_texto, color_de_estilo, fuente_de_estilo, tam_automatico,
                      tamano_de_estilo)
from .imagenes import RESAMPLE, escalada


class VistaLienzo:
    """Dibuja el mapa, las guias y los controles."""

    def __init__(self, padre, modelo):
        self.modelo = modelo
        self.escala = 1.0
        self.imagen_original = None    # imagen PIL del campo
        self._img_fondo = None         # PhotoImage del fondo (hay que conservarla)
        self._img_tk = []              # referencias vivas de los iconos

        marco = tk.Frame(padre)
        marco.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(marco, bg="gray85", highlightthickness=0)
        vs = tk.Scrollbar(marco, orient=tk.VERTICAL, command=self.canvas.yview)
        hs = tk.Scrollbar(marco, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vs.grid(row=0, column=1, sticky="ns")
        hs.grid(row=1, column=0, sticky="we")
        marco.rowconfigure(0, weight=1)
        marco.columnconfigure(0, weight=1)

        # Que hay que repintar cuando cambia la seleccion:
        #   (clase, id) -> [(tag, opcion_de_color, color_normal, grosor_normal), ...]
        # Se rellena al dibujar, para poder resaltar sin volver a dibujarlo todo.
        self._resaltables = {}

    # --------------------------------------------------------------- CONVERSIONES
    def a_mapa(self, event):
        """Coordenadas del evento en pixeles del MAPA."""
        return (self.canvas.canvasx(event.x) / self.escala,
                self.canvas.canvasy(event.y) / self.escala)

    def a_pantalla(self, x, y):
        return x * self.escala, y * self.escala

    def centro_visible(self):
        """Centro de la parte visible, en pixeles del mapa."""
        cx = self.canvas.canvasx(self.canvas.winfo_width() / 2) / self.escala
        cy = self.canvas.canvasy(self.canvas.winfo_height() / 2) / self.escala
        return cx, cy

    def punto_mapa(self, sx, sy):
        """Punto del mapa que hay debajo de un punto de la ventana."""
        return (self.canvas.canvasx(sx) / self.escala,
                self.canvas.canvasy(sy) / self.escala)

    def anclar(self, punto, sx, sy):
        """Desplaza la vista para que ese punto del mapa quede en (sx, sy) de la
        ventana. Es lo que mantiene quieto lo que estas mirando al hacer zoom."""
        ancho, alto = self.dim_escaladas()
        if not ancho or not alto:
            return
        izq = punto[0] * self.escala - sx
        arriba = punto[1] * self.escala - sy
        self.canvas.xview_moveto(min(max(izq / ancho, 0.0), 1.0))
        self.canvas.yview_moveto(min(max(arriba / alto, 0.0), 1.0))

    def dim_escaladas(self):
        if self.imagen_original is None:
            return 0, 0
        return (int(self.imagen_original.width * self.escala),
                int(self.imagen_original.height * self.escala))

    def cargar_imagen(self, img):
        self.imagen_original = img
        self.escala = 1.0

    def es_sel(self, clase, ident):
        return self.modelo.esta_seleccionado(clase, ident)

    def _resaltable(self, clase, ident, tag, opcion, color, grosor=None):
        self._resaltables.setdefault((clase, ident), []).append(
            (tag, opcion, color, grosor))

    def refrescar_seleccion(self):
        """Repinta SOLO el resalte, sin redibujar el mapa.

        Cambiar de elemento seleccionado no cambia nada del dibujo salvo el color y
        el grosor de dos elementos, y redibujar obliga a reescalar la imagen del
        campo entera (1920x1080), que se nota al hacer clic."""
        for clave, items in self._resaltables.items():
            sel = (clave == self.modelo.seleccion)
            for tag, opcion, color, grosor in items:
                cfg = {opcion: COL_SEL if sel else color}
                if grosor is not None:
                    cfg["width"] = 3 if sel else grosor
                try:
                    self.canvas.itemconfigure(tag, **cfg)
                except tk.TclError:
                    pass    # el elemento ya no esta dibujado

    # -------------------------------------------------------------------- DIBUJO
    def redibujar(self):
        m = self.modelo
        self.canvas.delete("all")
        self._img_tk = []
        self._resaltables = {}
        if self.imagen_original is None:
            return
        ancho, alto = self.dim_escaladas()
        self._img_fondo = ImageTk.PhotoImage(
            self.imagen_original.resize((ancho, alto), RESAMPLE))
        self.canvas.create_image(0, 0, anchor="nw", image=self._img_fondo)
        self.canvas.config(scrollregion=(0, 0, ancho, alto))

        # 0) Eje de simetria, para ver de un vistazo respecto a que se refleja todo.
        if m.simetria and m.eje() is not None:
            x = m.eje() * self.escala
            self.canvas.create_line(x, 0, x, alto, fill=COL_EJE, width=2, dash=(8, 6),
                                    tags=("eje",))

        # 1) Guias de colocacion (absolutas).
        for g in m.guias_col:
            self._guia_col(g, ancho, alto)

        # 2) Guias de control del grupo activo (relativas a su origen).
        if m.instancia_activa is not None:
            inst = m.instancia(m.instancia_activa)
            for gk in m.guias_ctrl_tipo(inst["tipo"]):
                self._guia_ctrl(inst, gk, ancho, alto)

        # 3) Origenes y controles de cada colocacion, mas la etiqueta del total
        #    (que es del mapa: la misma en todos los grupos que la muestran).
        for inst in m.instancias:
            self._origen(inst)
            for c in m.elementos_inst(inst):
                self.dibujar_control(inst, c)

        # 4) Los circulos de origen, siempre por encima de los controles. Son mucho
        # mas pequenos que estos, asi que apenas tapan nada, y si no se quedan
        # escondidos debajo de un boton y no hay forma de pinchar el grupo.
        # Al subirlos tambien pasan a ser el primer candidato de candidatos(), que
        # recorre los elementos de arriba abajo.
        self.canvas.tag_raise("instancia")

    def _guia_col(self, g, ancho, alto):
        sel = self.es_sel("col", g["id"])
        color = COL_SEL if sel else COL_COLOCACION
        grosor = 3 if sel else 1
        p = g["pos"] * self.escala
        if g["orient"] == "v":
            self.canvas.create_line(p, 0, p, alto, fill=color, width=grosor,
                                    tags=("colocacion", g["id"]))
        else:
            self.canvas.create_line(0, p, ancho, p, fill=color, width=grosor,
                                    tags=("colocacion", g["id"]))
        self._resaltable("col", g["id"], g["id"], "fill", COL_COLOCACION, 1)

    def _guia_ctrl(self, inst, gk, ancho, alto):
        sel = self.es_sel("ctrl", gk["id"])
        color = COL_SEL if sel else COL_CONTROL
        grosor = 3 if sel else 1
        # Los ejes del origen se dibujan con puntos mas finos: no son guias que se
        # puedan mover, y asi no se confunden con las que dibuja el usuario.
        trazo = (2, 4) if gk.get("cero") else (6, 4)
        p = self.modelo.pos_ctrl_abs(inst, gk) * self.escala
        if gk["orient"] == "v":
            self.canvas.create_line(p, 0, p, alto, fill=color, width=grosor,
                                    dash=trazo, tags=("ctrlguia", gk["id"]))
        else:
            self.canvas.create_line(0, p, ancho, p, fill=color, width=grosor,
                                    dash=trazo, tags=("ctrlguia", gk["id"]))
        self._resaltable("ctrl", gk["id"], gk["id"], "fill", COL_CONTROL, 1)

    def geometria_origen(self, inst):
        """Varias colocaciones pueden compartir el MISMO cruce. Para poder verlas y
        pincharlas por separado, cada una se dibuja con un radio distinto y su nombre
        escalonado."""
        hermanas = self.modelo.hermanas(inst)
        idx = hermanas.index(inst)
        return 6 + 4 * idx, -12 - 14 * idx

    def _origen(self, inst):
        m = self.modelo
        ox, oy = m.origen(inst)
        x, y = self.a_pantalla(ox, oy)
        r, dy = self.geometria_origen(inst)
        sel = self.es_sel("inst", inst["id"])
        activa = (inst["id"] == m.instancia_activa)
        color = COL_SEL if sel else COL_ORIGEN
        self.canvas.create_oval(x - r, y - r, x + r, y + r, outline=color,
                                fill="#e9d5f0", width=3 if (sel or activa) else 2,
                                tags=("instancia", inst["id"], f'{inst["id"]}_marca'))
        # Un solo distintivo: "(espejo)" si la creo la simetria y "(reflejado)" si la
        # ha dado la vuelta el usuario. Y no se repite lo que ya diga el nombre, que
        # es lo que hacia que saliera "(reflejado) (reflejado) (espejo)".
        marcas = ["(activo)"] if activa else []
        if inst.get("auto"):
            marcas.append("(espejo)")
        elif inst.get("inv"):
            marcas.append("(reflejado)")
        nombre = inst.get("nombre") or m.nombre_tipo(inst["tipo"])
        bajo = nombre.lower()
        etiqueta = "  ".join([nombre] + [t for t in marcas if t not in bajo])
        self.canvas.create_text(x + r + 4, y + dy, text=etiqueta, anchor="w",
                                fill=color, font=(FUENTE, 9, "bold"),
                                tags=("instancia", inst["id"], f'{inst["id"]}_lbl'))
        self._resaltable("inst", inst["id"], f'{inst["id"]}_marca', "outline",
                         COL_ORIGEN, 3 if activa else 2)
        self._resaltable("inst", inst["id"], f'{inst["id"]}_lbl', "fill", COL_ORIGEN)

    # ------------------------------------------------------- CONTENIDO DE UN CONTROL
    def rect_pantalla(self, inst, c):
        x1, y1, x2, y2 = self.modelo.rect_control(inst, c)
        return (x1 * self.escala, y1 * self.escala,
                x2 * self.escala, y2 * self.escala)

    def texto_control(self, c):
        """Texto que se dibuja dentro de un elemento.

        Una etiqueta externa no tiene texto que mostrar aqui: su valor lo pone el
        partido, asi que se dibuja su identificador entre comillas angulares para
        que se vea que es dinamico. Las imagenes web tampoco se pueden dibujar."""
        cont = c["contenido"]
        tipo = cont.get("tipo", 1)
        valor = str(cont.get("valor", ""))
        if cont.get("externa"):
            return f"«{valor}»"
        if tipo == 3:
            return f"web: {os.path.basename(valor)}"
        if tipo == 2:
            return os.path.basename(valor)
        return valor

    def estilo_control(self, c, inst=None):
        # El total no tiene estilo propio en el control: es del GRUPO que lo dibuja
        # (Arbitraje_TotalGrupoAcciones.FK_ESTILO_FUENTE), asi que sale igual en todas
        # las colocaciones de ese grupo.
        cat = self.modelo.catalogos
        if c["clase"] == "total" and inst is not None:
            return cat.estilo(self.modelo.estilo_total(inst["tipo"]))
        return cat.estilo(c.get("param", {}).get("estilo"))

    def lado_control(self, c, inst=None):
        """De donde sale el color de fondo de cada elemento. El tono y la saturacion
        vienen siempre del lado del parcial que lo dibuja (Arbitraje_ZonaAcciones):
        la vista de etiquetas las une con la zona por el grupo, y de Partido_Lado saca
        color_h y color_s. La intensidad (color_v) es propia de la etiqueta, y del
        parcial en los botones y el total."""
        pz = (inst or {}).get("param", {})
        if c["clase"] == "etiqueta":
            return pz.get("lado"), c.get("param", {}).get("color_v", 255)
        return pz.get("lado"), pz.get("color_v", 255)

    def relleno_control(self, c, inst=None):
        """El color real lo dan el lado y la intensidad, igual que en el arbitraje.
        Sin catalogo de lados, se recurre a los colores de respaldo."""
        ident, color_v = self.lado_control(c, inst)
        col = self.modelo.catalogos.color(ident, color_v)
        if col:
            return col
        if c["clase"] == "boton":
            return COL_BOTON
        if c["clase"] == "total":
            return COL_TOTAL
        cont = c["contenido"]
        if cont.get("tipo", 1) in (2, 3):
            return COL_ETQ_GRAFICO
        if cont.get("externa"):
            return COL_ETQ_CAMPO
        return COL_ETQ_TEXTO

    def contenido_control(self, c, inst=None):
        """Que se pinta dentro: (texto, color, ruta_imagen, img_pos). Para los botones
        lo decide el tipo de accion de Arbitraje_TipoAcciones; para las etiquetas, el
        campo tipo de Arbitraje_Etiqueta."""
        p = c.get("param", {})
        if c["clase"] != "boton":
            cont = c["contenido"]
            # tipo 2 es una imagen local: se dibuja. tipo 3 se descarga de la web al
            # arrancar el arbitraje, asi que aqui solo se puede anunciar.
            if cont.get("tipo", 1) == 2 and not cont.get("externa"):
                return None, None, self.modelo.ruta_grafico(cont.get("valor", "")), "todo"
            return (self.texto_control(c),
                    color_de_estilo(self.estilo_control(c, inst)), None, "")
        tipo = p.get("tipo_accion", "click")
        if tipo == "nulo":
            return None, None, None, ""
        if tipo == "graf":
            return None, None, self.modelo.ruta_grafico(p.get("directorio", "")), "todo"
        # El icono no es exclusivo de 'click'. En las ediciones reales hay controles
        # 'bool' con su icono al lado de la marca (2026: 'Ardillas en despensa',
        # 'Refrigerador 1 vacio'), asi que se dibuja siempre que haya imagen y
        # posicion. Lo unico que el esquema ata a 'click' es el significado de
        # img_pos ("posicion del icono con respecto al numero").
        icono = self.modelo.ruta_grafico(p.get("directorio", ""))
        pos = p.get("img_pos", "") if icono else ""
        if tipo == "bool":
            return MARCA_BOOL, COL_MARCA_BOOL, icono if pos else None, pos
        return (self.texto_control(c),
                color_de_estilo(self.estilo_control(c, inst)),
                icono if pos else None, pos)

    def huecos_control(self, x1, y1, x2, y2, pos):
        if pos == "todo":
            return (x1, y1, x2, y2), None
        return reparto_icono(x1, y1, x2, y2, pos)

    def desp_control(self, c, inst=None):
        """Desplazamiento vertical del texto dentro del control: tipo_d en los botones,
        etiqueta_d en las etiquetas y zona_d (del grupo) en el total."""
        p = c.get("param", {})
        if c["clase"] == "total":
            d = self.modelo.desp_total(inst["tipo"]) if inst is not None else 0
        elif c["clase"] == "boton":
            d = p.get("tipo_d", 0)
        else:
            d = p.get("desp", 0)
        return float(d or 0) * self.escala

    def fuente_control(self, c, ancho, alto, inst=None, texto=None):
        """Prioridad: tamano propio del contenido > tamano del estilo de fuente >
        ajuste automatico al hueco. El tamano se guarda en pixeles del MAPA, asi que
        se multiplica por la escala para que siga al zoom."""
        estilo = self.estilo_control(c, inst)
        if texto is None:
            texto = self.texto_control(c)
        tam = c["contenido"].get("tam") or tamano_de_estilo(estilo)
        if tam:
            return fuente_de_estilo(estilo, max(1, int(round(float(tam) * self.escala))))
        return fuente_de_estilo(estilo, tam_automatico(estilo, texto, ancho, alto))

    def texto_cabe(self, c, ancho, alto, inst=None, texto=None):
        """¿El texto se sale del control con el estilo elegido? Solo puede pasar
        cuando el tamano es fijo; con el ajuste automatico siempre cabe."""
        estilo = self.estilo_control(c, inst)
        tam = c["contenido"].get("tam") or tamano_de_estilo(estilo)
        if not tam:
            return True
        if texto is None:
            texto = self.texto_control(c)
        return cabe_texto(estilo, texto, float(tam) * self.escala, ancho, alto)

    def ancla_texto(self, c, r_txt, inst=None):
        """Punto y anclaje del texto dentro de su hueco, segun la justificacion (solo
        las etiquetas la tienen; lo demas va centrado)."""
        x1, y1, x2, y2 = r_txt
        cy = (y1 + y2) / 2 + self.desp_control(c, inst)
        just = c.get("param", {}).get("justif", "c") if c["clase"] == "etiqueta" else "c"
        if just == "l":
            return x1 + MARGEN_TEXTO, cy, "w"
        if just == "r":
            return x2 - MARGEN_TEXTO, cy, "e"
        return (x1 + x2) / 2, cy, "center"

    def dibujar_control(self, inst, c):
        x1, y1, x2, y2 = self.rect_pantalla(inst, c)
        sel = self.es_sel("control", c["id"])
        texto, color, ruta, pos = self.contenido_control(c, inst)
        r_ico, r_txt = self.huecos_control(x1, y1, x2, y2, pos)

        # Un borde rojo discontinuo avisa de que el texto se sale del control.
        desborda = bool(texto) and r_txt is not None and not self.texto_cabe(
            c, r_txt[2] - r_txt[0], r_txt[3] - r_txt[1], inst, texto)
        base = BORDE_CLASE.get(c["clase"], "#333")
        borde = COL_SEL if sel else (COL_DESBORDE if desborda else base)
        grosor = 3 if sel else (2 if desborda else 1)
        rect_tag = f'{c["id"]}_{inst["id"]}_rect'
        txt_tag = f'{c["id"]}_{inst["id"]}_txt'
        ico_tag = f'{c["id"]}_{inst["id"]}_ico'
        tags = ("control", c["id"], f'ori:{inst["id"]}')
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.relleno_control(c, inst),
                                     outline=borde, width=grosor,
                                     dash=(4, 3) if desborda and not sel else (),
                                     tags=tags + (rect_tag,))
        self._resaltable("control", c["id"], rect_tag, "outline", base,
                         2 if desborda else 1)

        if r_ico is not None and ruta:
            img = escalada(ruta, r_ico[2] - r_ico[0] - 2, r_ico[3] - r_ico[1] - 2)
            if img is not None:
                ph = ImageTk.PhotoImage(img)
                self._img_tk.append(ph)   # hay que conservar la referencia
                self.canvas.create_image((r_ico[0] + r_ico[2]) / 2,
                                         (r_ico[1] + r_ico[3]) / 2,
                                         image=ph, tags=tags + (ico_tag,))
        if texto and r_txt is not None:
            tx, ty, ancla = self.ancla_texto(c, r_txt, inst)
            self.canvas.create_text(tx, ty, text=texto, fill=color, anchor=ancla,
                                    font=self.fuente_control(c, r_txt[2] - r_txt[0],
                                                             r_txt[3] - r_txt[1],
                                                             inst, texto),
                                    tags=tags + (txt_tag,))

    # --------------------------------------------------------- ARRASTRE (SIN REDIBUJAR)
    def repintar_vectores(self):
        """Recoloca lo vectorial sin reescalar la imagen de fondo. Se usa al arrastrar:
        las imagenes solo se mueven, su tamano se recalcula al soltar."""
        m = self.modelo
        ancho, alto = self.dim_escaladas()
        for g in m.guias_col:
            p = g["pos"] * self.escala
            if g["orient"] == "v":
                self.canvas.coords(g["id"], p, 0, p, alto)
            else:
                self.canvas.coords(g["id"], 0, p, ancho, p)
        if m.instancia_activa is not None:
            inst = m.instancia(m.instancia_activa)
            for gk in m.guias_ctrl_tipo(inst["tipo"]):
                p = m.pos_ctrl_abs(inst, gk) * self.escala
                if gk["orient"] == "v":
                    self.canvas.coords(gk["id"], p, 0, p, alto)
                else:
                    self.canvas.coords(gk["id"], 0, p, ancho, p)
        for inst in m.instancias:
            ox, oy = m.origen(inst)
            x, y = self.a_pantalla(ox, oy)
            r, dy = self.geometria_origen(inst)
            self.canvas.coords(f'{inst["id"]}_marca', x - r, y - r, x + r, y + r)
            self.canvas.coords(f'{inst["id"]}_lbl', x + r + 4, y + dy)
            for c in m.elementos_inst(inst):
                x1, y1, x2, y2 = self.rect_pantalla(inst, c)
                self.canvas.coords(f'{c["id"]}_{inst["id"]}_rect', x1, y1, x2, y2)
                _, _, _, pos = self.contenido_control(c, inst)
                r_ico, r_txt = self.huecos_control(x1, y1, x2, y2, pos)
                if r_txt is not None:
                    tx, ty, _ = self.ancla_texto(c, r_txt, inst)
                    self.canvas.coords(f'{c["id"]}_{inst["id"]}_txt', tx, ty)
                if r_ico is not None:
                    self.canvas.coords(f'{c["id"]}_{inst["id"]}_ico',
                                       (r_ico[0] + r_ico[2]) / 2,
                                       (r_ico[1] + r_ico[3]) / 2)

    # ------------------------------------------------------------ LOCALIZAR ELEMENTOS
    def candidatos(self, event, clases):
        """TODOS los elementos seleccionables bajo el cursor, del que esta mas arriba
        al que esta mas abajo, sin repetir. Asi, si dos se solapan (dos origenes en el
        mismo cruce, una guia sobre otra...), no se pierde el de debajo."""
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        tol = 5
        solapados = self.canvas.find_overlapping(cx - tol, cy - tol, cx + tol, cy + tol)
        lista = []
        for item in reversed(solapados):
            tags = self.canvas.gettags(item)
            cand = None
            if "control" in tags and "control" in clases:
                inst_id = next((t.split(":", 1)[1] for t in tags
                                if t.startswith("ori:")), None)
                cand = ("control", tags[1], inst_id)
            elif "instancia" in tags and "inst" in clases:
                cand = ("inst", tags[1], tags[1])
            elif "ctrlguia" in tags and "ctrl" in clases:
                cand = ("ctrl", tags[1], None)
            elif "colocacion" in tags and "col" in clases:
                cand = ("col", tags[1], None)
            if cand is not None and cand not in lista:
                lista.append(cand)
        return lista