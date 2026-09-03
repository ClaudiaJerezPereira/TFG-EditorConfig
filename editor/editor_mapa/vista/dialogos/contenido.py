"""Dialogo del contenido y los parametros de una etiqueta (Arbitraje_Etiqueta)."""
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from ...modelo.catalogos import color_lado
from ...modelo.constantes import (CAMPOS_PARTIDO, JUSTIFICACIONES, MAX_ID_PARTIDO,
                                  TIPOS_ETIQUETA)
from ...modelo.geometria import MARGEN_TEXTO
from ..apariencia import (ALTO_MUESTRA, ANCHO_MUESTRA, COL_ETQ_TEXTO, FUENTE,
                          Spin as _Spin)
from ..fuentes import cabe_texto, color_de_estilo, fuente_de_estilo, tam_automatico
from ..imagenes import RESAMPLE
from .base import _DialogoBase


class DialogoContenido(_DialogoBase):
    """Dialogo modal para definir el contenido de una etiqueta (Arbitraje_Etiqueta).

    El contenido son tres datos de esa tabla:
      - externa : de donde sale el valor. False, de la propia tabla (etiqueta fija,
                  p.ej. "TOTAL PUNTOS"); True, de VistaPartido_EtiquetasPartido, y
                  entonces el valor es el identificador del dato (p.ej. "DORSAL").
      - tipo    : 1 texto, 2 imagen, 3 imagen web.
      - valor   : el texto, el nombre de la imagen o ese identificador.
    """

    def __init__(self, padre, contenido=None, nombre="", titulo="Contenido de la etiqueta",
                 param=None, estilos=None, lados=None, tam_control=None, lado_parcial=None,
                 ruta_grafico=None, carpeta_graficos=None):
        super().__init__(padre)
        self.title(titulo)
        self.resultado = None
        self.transient(padre)
        self.resizable(False, False)
        # Tamano real del recuadro (px del mapa) y lado del parcial, para la vista previa.
        self.tam_control = tam_control or (120, 40)
        self.lado_parcial = lado_parcial
        # Con que resolver el nombre de una imagen para poder dibujarla, y cual es la
        # carpeta de graficos (la unica de la que se admiten imagenes).
        self._resolver = ruta_grafico or (lambda n: n)
        self._carpeta = carpeta_graficos or (lambda: ".")

        contenido = contenido or {"externa": False, "tipo": 1, "valor": "", "tam": None}
        externa_ini = bool(contenido.get("externa"))
        tipo_ini = int(contenido.get("tipo", 1) or 1)
        valor_ini = str(contenido.get("valor", ""))

        # Parametros que corresponden a la tabla Arbitraje_Etiqueta.
        param = param or {}
        self.estilos = estilos or []
        self.lados = lados or []

        self.var_nombre = tk.StringVar(value=nombre)
        self.var_externa = tk.BooleanVar(value=externa_ini)
        self.var_tipo = tk.StringVar(value=TIPOS_ETIQUETA.get(tipo_ini, "texto"))
        self.var_valor = tk.StringVar(value=valor_ini)

        # Tamano de la fuente. None = automatico (se ajusta al tamano del recuadro).
        tam_ini = contenido.get("tam")
        self.var_auto = tk.BooleanVar(value=(tam_ini is None))
        self.var_tam = tk.StringVar(value=str(int(tam_ini)) if tam_ini else "12")

        # Variables de los parametros SQL de la etiqueta.
        self._estilo_nombres = [e["descripcion"] for e in self.estilos]
        self.var_estilo = tk.StringVar(value=self._nombre_por_id(self.estilos, param.get("estilo"),
                                                                 "descripcion"))
        self.var_justif = tk.StringVar(value=JUSTIFICACIONES.get(param.get("justif", "c"), "centro"))
        self.var_colorv = tk.StringVar(value=str(int(param.get("color_v", 255))))
        self.var_desp = tk.StringVar(value=str(int(param.get("desp", 0))))

        # El nombre identifica al elemento en el XML (p.ej. NOMBRE="Tribuna1").
        cab = ttk.Frame(self, padding=(10, 10, 10, 0))
        cab.pack(fill=tk.X)
        ttk.Label(cab, text="Nombre:").pack(side=tk.LEFT)
        self.e_nombre = ttk.Entry(cab, textvariable=self.var_nombre, width=28)
        self.e_nombre.pack(side=tk.LEFT, padx=6)

        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill=tk.BOTH, expand=True)
        marco = ttk.Frame(cuerpo, padding=10)
        marco.grid(row=0, column=0, sticky="nw")
        ttk.Separator(cuerpo, orient="vertical").grid(row=0, column=1, sticky="ns", pady=8)

        # --- Panel derecho: parametros para la base de datos (Arbitraje_Etiqueta) ---
        par = ttk.Frame(cuerpo, padding=10)
        par.grid(row=0, column=2, sticky="nw")
        ttk.Label(par, text="Parámetros de la etiqueta", font=(FUENTE, 9, "bold")
                  ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))
        ttk.Label(par, text="Estilo de fuente:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Combobox(par, textvariable=self.var_estilo, values=self._estilo_nombres,
                     state="readonly", width=18).grid(row=1, column=1, sticky="we", pady=2)
        # El lado ya no es de la etiqueta: la vista la une con Arbitraje_ZonaAcciones
        # por el grupo, asi que el tono lo pone el parcial que la dibuja.
        lado = next((l for l in self.lados if l["id"] == self.lado_parcial), None)
        ttk.Label(par, text=f"Fondo: lado «{(lado or {}).get('nombre', 'sin lado')}» "
                            f"del parcial.\nSolo la intensidad es de la etiqueta.",
                  foreground="#666", justify="left"
                  ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(2, 4))
        ttk.Label(par, text="Justificación:").grid(row=4, column=0, sticky="w", pady=2)
        ttk.Combobox(par, textvariable=self.var_justif, values=list(JUSTIFICACIONES.values()),
                     state="readonly", width=18).grid(row=4, column=1, sticky="we", pady=2)
        ttk.Label(par, text="Intensidad color (0-255):").grid(row=5, column=0, sticky="w", pady=2)
        _Spin(par, from_=0, to=255, width=6, textvariable=self.var_colorv
              ).grid(row=5, column=1, sticky="w", pady=2)
        ttk.Label(par, text="Desplazamiento vertical:").grid(row=6, column=0, sticky="w", pady=2)
        _Spin(par, from_=-50, to=50, width=6, textvariable=self.var_desp
              ).grid(row=6, column=1, sticky="w", pady=2)
        ttk.Label(par, text="(ajuste fino del texto en el recuadro)",
                  foreground="#666").grid(row=7, column=0, columnspan=2, sticky="w")

        # --- Vista previa a tamano real ---
        ttk.Separator(par, orient="horizontal").grid(row=8, column=0, columnspan=2,
                                                     sticky="we", pady=8)
        ttk.Label(par, text="Vista previa", font=(FUENTE, 9, "bold")
                  ).grid(row=9, column=0, columnspan=2, sticky="w")
        self.lienzo = tk.Canvas(par, width=ANCHO_MUESTRA, height=ALTO_MUESTRA,
                                bg="#f4f4f4", highlightthickness=1, highlightbackground="#bbb")
        self.lienzo.grid(row=10, column=0, columnspan=2, sticky="w", pady=6)
        self.aviso = ttk.Label(par, text="", foreground="#b00", justify="left", wraplength=220)
        self.aviso.grid(row=11, column=0, columnspan=2, sticky="w")
        self.escala_vp = ttk.Label(par, text="", foreground="#666")
        self.escala_vp.grid(row=12, column=0, columnspan=2, sticky="w")

        # --- Contenido: externa, tipo y valor (los tres campos de la tabla) ---
        self.chk_externa = ttk.Checkbutton(
            marco, text="Valor externo (depende del partido)",
            variable=self.var_externa, command=self._actualizar)
        self.chk_externa.grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(marco, text="Sin marcar, el valor es fijo y se escribe aquí.\n"
                              "Marcado, es el identificador del dato del partido\n"
                              "(VistaPartido_EtiquetasPartido).",
                  foreground="#666", justify="left"
                  ).grid(row=1, column=0, columnspan=2, sticky="w", padx=(20, 0), pady=(0, 8))

        ttk.Label(marco, text="Tipo:").grid(row=2, column=0, sticky="w", pady=2)
        self.c_tipo = ttk.Combobox(marco, textvariable=self.var_tipo,
                                   values=list(TIPOS_ETIQUETA.values()),
                                   state="readonly", width=14)
        self.c_tipo.grid(row=2, column=1, sticky="w", pady=2)

        self.etq_valor = ttk.Label(marco, text="Valor:")
        self.etq_valor.grid(row=3, column=0, sticky="w", pady=(8, 2))
        self.c_valor = ttk.Combobox(marco, textvariable=self.var_valor,
                                    values=CAMPOS_PARTIDO, width=32)
        self.c_valor.grid(row=4, column=0, columnspan=2, sticky="we")
        self.b_ruta = ttk.Button(marco, text="Examinar...", command=self._buscar_imagen)
        self.b_ruta.grid(row=5, column=0, sticky="w", pady=(4, 0))
        self.ayuda_valor = ttk.Label(marco, text="", foreground="#666", justify="left",
                                     wraplength=280)
        self.ayuda_valor.grid(row=5, column=1, sticky="w", pady=(4, 0))

        # --- Tamano de la fuente (solo para texto fijo y campo de base de datos) ---
        ttk.Separator(marco, orient="horizontal").grid(row=6, column=0, columnspan=2,
                                                       sticky="we", pady=(12, 6))
        self.marco_tam = ttk.Frame(marco)
        self.marco_tam.grid(row=7, column=0, columnspan=2, sticky="w")
        self.chk_auto = ttk.Checkbutton(self.marco_tam, text="Tamaño automático",
                                        variable=self.var_auto, command=self._actualizar)
        self.chk_auto.pack(side=tk.LEFT)
        ttk.Label(self.marco_tam, text="  Tamaño (px):").pack(side=tk.LEFT)
        self.spin_tam = _Spin(self.marco_tam, from_=4, to=200, width=5,
                              textvariable=self.var_tam)
        self.spin_tam.pack(side=tk.LEFT, padx=4)

        botones = ttk.Frame(marco)
        botones.grid(row=8, column=0, columnspan=2, sticky="e", pady=(14, 0))
        ttk.Button(botones, text="Aceptar", command=self._aceptar).pack(side=tk.LEFT, padx=3)
        ttk.Button(botones, text="Cancelar", command=self._cancelar).pack(side=tk.LEFT)

        self._img_tk = []
        for var in (self.var_valor, self.var_tam, self.var_estilo, self.var_justif,
                    self.var_colorv, self.var_desp):
            var.trace_add("write", lambda *a: self._refrescar_muestra())
        self.var_tipo.trace_add("write", lambda *a: self._actualizar())
        self._actualizar()
        self._finalizar(self.c_valor)

    # --- Vista previa ---
    def _estilo_actual(self):
        for e in self.estilos:
            if e.get("descripcion") == self.var_estilo.get():
                return e
        return self.estilos[0] if self.estilos else None

    def _tipo_actual(self):
        for num, nombre in TIPOS_ETIQUETA.items():
            if nombre == self.var_tipo.get():
                return num
        return 1

    def _valor_actual(self):
        """Lo que se ve en el recuadro. Una etiqueta externa no tiene texto real: su
        valor lo pone el partido, asi que se muestra su identificador."""
        valor = self.var_valor.get()
        if self.var_externa.get():
            return f"«{valor}»"
        if self._tipo_actual() == 3:
            return f"web: {os.path.basename(valor)}"
        if self._tipo_actual() == 2:
            return os.path.basename(valor)
        return valor

    def _refrescar_muestra(self):
        if not hasattr(self, "lienzo"):
            return
        self.lienzo.delete("all")
        self._img_tk = []
        (x1, y1, x2, y2), k, (ancho, alto) = self._marco_muestra()
        w, h = x2 - x1, y2 - y1
        fondo = color_lado(self._lado_actual(), self._entero(self.var_colorv, 255)) or COL_ETQ_TEXTO
        self.lienzo.create_rectangle(x1, y1, x2, y2, fill=fondo, outline="#888")
        self.escala_vp.config(text=self._rotulo_escala(ancho, alto, k))

        if self._tipo_actual() == 2 and not self.var_externa.get():
            ruta = self._resolver(self.var_valor.get().strip())
            img = None
            if ruta:
                try:
                    img = Image.open(ruta).convert("RGBA").resize(
                        (max(1, int(w) - 2), max(1, int(h) - 2)), RESAMPLE)
                except Exception:
                    img = None
            if img is None:
                self.lienzo.create_text((x1 + x2) / 2, (y1 + y2) / 2, text="?", fill="#999")
                self.aviso.config(text="" if not ruta else "No se puede abrir la imagen.")
            else:
                ph = ImageTk.PhotoImage(img)
                self._img_tk.append(ph)
                self.lienzo.create_image((x1 + x2) / 2, (y1 + y2) / 2, image=ph)
                self.aviso.config(text="")
            return

        estilo = self._estilo_actual()
        texto = self._valor_actual()
        just = next((c for c, v in JUSTIFICACIONES.items() if v == self.var_justif.get()), "c")
        tam = None if self.var_auto.get() else self._entero(self.var_tam, 0)
        if not tam:
            tam = int((estilo or {}).get("tamano_fuente") or 0)
        if tam > 0:
            px = max(1, int(round(tam * k)))
            cabe = cabe_texto(estilo, texto, tam, w / k, h / k)
        else:
            px = tam_automatico(estilo, texto, w, h)
            cabe = True
        # La justificacion decide desde que borde se mide el texto.
        if just == "w":
            tx, anchor = x1 + MARGEN_TEXTO, "w"
        elif just == "e":
            tx, anchor = x2 - MARGEN_TEXTO, "e"
        else:
            tx, anchor = (x1 + x2) / 2, "center"
        self.lienzo.create_text(tx, (y1 + y2) / 2 + self._entero(self.var_desp) * k,
                                text=texto, anchor=anchor, fill=color_de_estilo(estilo),
                                font=fuente_de_estilo(estilo, px))
        if not cabe:
            self.aviso.config(text=f"El texto no cabe con el tamaño elegido ({tam} px). "
                                   f"Reduce el tamaño o agranda la etiqueta.")
        else:
            self.aviso.config(text="")

    def _actualizar(self):
        externa, tipo = self.var_externa.get(), self._tipo_actual()
        # Con valor externo, el "valor" es el identificador de la vista y se elige de
        # la lista; si es fijo y una imagen, se busca el archivo con Examinar.
        self.c_valor.config(values=CAMPOS_PARTIDO if externa else [])
        self.etq_valor.config(text="Identificador del dato:" if externa
                              else ("Nombre de la imagen:" if tipo in (2, 3) else "Texto:"))
        self.b_ruta.config(state="normal" if (tipo == 2 and not externa) else "disabled")
        if externa:
            ayuda = (f"El identificador tiene que existir en la vista del partido "
                     f"(máximo {MAX_ID_PARTIDO} caracteres). La aplicación pone un "
                     f"valor por cada lado, así que la misma etiqueta muestra el dato "
                     f"del equipo de cada parcial.")
        elif tipo == 2:
            ayuda = (f"Solo se guarda el nombre del archivo: el directorio lo pone la "
                     f"configuración de la aplicación de arbitraje. La imagen tiene que "
                     f"estar en {self._carpeta()}")
        elif tipo == 3:
            ayuda = ("La imagen se descarga al arrancar el arbitraje, así que aquí no "
                     "se puede dibujar; se guarda solo su nombre o dirección.")
        else:
            ayuda = "Texto que se mostrará tal cual, con la fuente del estilo elegido."
        self.ayuda_valor.config(text=ayuda)
        # El tamano de la letra solo interviene si se dibuja texto.
        hay_texto = externa or tipo == 1 or tipo == 3
        self.chk_auto.config(state="normal" if hay_texto else "disabled")
        self.spin_tam.config(state="normal" if (hay_texto and not self.var_auto.get())
                             else "disabled")
        self._refrescar_muestra()

    def _buscar_imagen(self):
        """Las imagenes se cogen de la carpeta de graficos del editor y de ninguna otra:
        en la tabla solo cabe el nombre del archivo, asi que una imagen de otro sitio
        no se podria dibujar ni aqui ni en el arbitraje."""
        carpeta = self._carpeta()
        ruta = filedialog.askopenfilename(
            parent=self, title="Selecciona la imagen de la etiqueta",
            initialdir=carpeta,
            filetypes=[("Imagenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos", "*.*")])
        if not ruta:
            return
        if os.path.normcase(os.path.dirname(os.path.abspath(ruta))) != \
                os.path.normcase(os.path.abspath(carpeta)):
            messagebox.showwarning(
                "La imagen tiene que estar en la carpeta de gráficos",
                f"«{os.path.basename(ruta)}» está en otra carpeta.\n\nEn la base de "
                f"datos solo se guarda el nombre del archivo, así que las imágenes de "
                f"las etiquetas tienen que estar en:\n\n{carpeta}\n\nCópiala ahí y "
                f"vuelve a elegirla.", parent=self)
            return
        self.var_valor.set(os.path.basename(ruta))

    def _aceptar(self):
        externa, tipo = self.var_externa.get(), self._tipo_actual()
        valor = self.var_valor.get().strip()
        if not valor:
            que = ("el identificador del dato del partido" if externa
                   else ("el nombre de la imagen" if tipo in (2, 3) else "el texto"))
            messagebox.showwarning("Falta el valor", f"Escribe {que}.", parent=self)
            return
        if externa and len(valor) > MAX_ID_PARTIDO:
            messagebox.showwarning(
                "Identificador demasiado largo",
                f"«{valor}» tiene {len(valor)} caracteres y la vista del partido admite "
                f"{MAX_ID_PARTIDO} como máximo.", parent=self)
            return
        tam = None
        if (externa or tipo != 2) and not self.var_auto.get():
            try:
                tam = float(self.var_tam.get().replace(",", "."))
            except ValueError:
                tam = 0
            if tam <= 0:
                messagebox.showwarning("Tamaño no válido",
                                       "El tamaño de la fuente debe ser un número mayor que 0, "
                                       "o marca 'Tamaño automático'.", parent=self)
                return
        nombre = self.var_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Falta el nombre",
                                   "Escribe un nombre; identifica al elemento en el XML.",
                                   parent=self)
            return
        # Parametros SQL de la etiqueta.
        justif = next((k for k, v in JUSTIFICACIONES.items() if v == self.var_justif.get()), "c")
        try:
            color_v = max(0, min(255, int(float(self.var_colorv.get()))))
        except ValueError:
            color_v = 255
        try:
            desp = int(float(self.var_desp.get()))
        except ValueError:
            desp = 0
        param = {
            "estilo": self._id_por_nombre(self.estilos, self.var_estilo.get(), "descripcion"),
            "justif": justif, "color_v": color_v, "desp": desp,
        }
        self.resultado = {"nombre": nombre,
                          "contenido": {"externa": externa, "tipo": tipo,
                                        "valor": valor, "tam": tam},
                          "param": param}
        self.destroy()