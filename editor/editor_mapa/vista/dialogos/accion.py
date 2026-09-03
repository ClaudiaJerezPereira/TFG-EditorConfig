"""Dialogo de los parametros de un boton (Arbitraje_TipoAcciones)."""
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from ...modelo.catalogos import color_lado
from ...modelo.constantes import TIPOS_ACCION
from ...modelo.geometria import reparto_icono
from ..apariencia import (ALTO_MUESTRA, ANCHO_MUESTRA, COL_BOTON, COL_MARCA_BOOL,
                          FUENTE, IMG_POS_ETIQUETA, MARCA_BOOL, Spin as _Spin)
from ..fuentes import (cabe_texto, color_de_estilo, familia_valida, fuente_de_estilo,
                       rasgos_de_estilo, tam_automatico)
from ..imagenes import RESAMPLE
from .base import _DialogoBase


def etiquetas_estilo(estilos):
    """Texto con el que aparece cada estilo en el desplegable.

    La descripcion de Arbitraje_EstiloFuente puede estar vacia (en los datos de
    ejemplo, el estilo 0 lo esta) o repetida, y entonces el desplegable muestra una
    linea en blanco o dos iguales y no se sabe cual se esta asignando. En esos casos
    se anade el identificador."""
    repes = {}
    for e in estilos:
        d = str(e.get("descripcion", "")).strip()
        repes[d] = repes.get(d, 0) + 1
    etiquetas = []
    for e in estilos:
        d = str(e.get("descripcion", "")).strip()
        etiquetas.append(d if d and repes[d] == 1 else f"{d or '(sin nombre)'} [{e['id']}]")
    return etiquetas


def resumen_estilo(estilo):
    """Como se dibuja el estilo elegido, en una linea: la descripcion sola no dice
    nada, y asi se ve antes de aceptar."""
    if not estilo:
        return "Sin estilo: se usa la fuente de por defecto."
    familia = str(estilo.get("nombre_fuente") or "").strip()
    real = familia_valida(familia)
    negrita, cursiva, subrayado = rasgos_de_estilo(estilo)
    rasgos = [n for n, v in (("negrita", negrita), ("cursiva", cursiva),
                             ("subrayado", subrayado)) if v] or ["normal"]
    tam = int(estilo.get("tamano_fuente") or 0)
    partes = [real, " ".join(rasgos), f"{tam} px" if tam else "tamaño automático",
              color_de_estilo(estilo)]
    texto = "Fuente: " + " · ".join(partes)
    if familia and real.lower() != familia.lower():
        texto += f"\n«{familia}» no está instalada: se dibuja con {real}."
    return texto


class DialogoAccion(_DialogoBase):
    """Parametros de un control de accion (un boton). Tabla Arbitraje_TipoAcciones.

    Todo lo que afecta al aspecto del boton (tipo de accion, estilo de fuente, icono
    y su posicion, desplazamiento vertical) se ve en la vista previa, que dibuja el
    control a su tamano real. El "valor de ejemplo" no es un dato del arbitraje: sirve
    para comprobar como queda el boton con el numero mas largo que vaya a mostrar, ya
    que con una cifra el texto puede ser mucho mayor que con tres.
    """

    def __init__(self, padre, nombre="", param=None, estilos=None,
                 contenido=None, tam_control=None,
                 lados=None, lado_parcial=None, color_v=255,
                 ruta_grafico=None, carpeta_graficos=None):
        super().__init__(padre)
        self.title("Parámetros del control")
        self.resultado = None
        self.transient(padre)
        self.resizable(False, False)
        param = param or {}
        self.estilos = estilos or []
        self.contenido = dict(contenido or {"modo": "texto", "valor": "0", "tam": None})
        # Tamano del boton en pixeles del mapa; si no se conoce, uno orientativo.
        self.tam_control = tam_control or (90, 60)
        # El fondo de un boton no es suyo: sale del parcial que lo dibuja (el lado da
        # el tono y la saturacion, y su color_v la intensidad). Aqui no se edita, pero
        # la vista previa tiene que pintarlo igual que el mapa y que el arbitraje.
        self.lados = lados or []
        self.lado_parcial = lado_parcial
        self.color_v = color_v
        # Con que resolver el nombre del icono para dibujarlo, y cual es la carpeta de
        # graficos (la unica de la que se admiten imagenes, igual que en las etiquetas:
        # en Arbitraje_TipoAcciones.directorio solo va el nombre del archivo).
        self._resolver = ruta_grafico or (lambda n: n)
        self._carpeta = carpeta_graficos or (lambda: ".")

        self.var_nombre = tk.StringVar(value=nombre)
        self.var_tipo = tk.StringVar(value=param.get("tipo_accion", "click"))
        self.var_accion = tk.StringVar(value=param.get("accion", nombre))
        # El desplegable trabaja con etiquetas, no con la descripcion a secas, para
        # que dos estilos nunca se vean iguales en la lista.
        self._etq_estilo = etiquetas_estilo(self.estilos)
        self._estilo_por_etq = dict(zip(self._etq_estilo, self.estilos))
        self.var_estilo = tk.StringVar(value=self._etq_de_id(param.get("estilo")))
        self.var_publicar = tk.BooleanVar(value=param.get("publicar", True))
        vm = param.get("valor_maximo")
        self.var_vmax = tk.StringVar(value="" if vm is None else str(int(vm)))
        self.var_desp = tk.StringVar(value=str(int(param.get("tipo_d", 0))))
        self.var_imgpos = tk.StringVar(value=IMG_POS_ETIQUETA.get(param.get("img_pos", ""),
                                                                  "(ninguna)"))
        self.var_dir = tk.StringVar(value=param.get("directorio", ""))
        self.var_muestra = tk.StringVar(value=str(self.contenido.get("valor", "0")))

        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill=tk.BOTH, expand=True)
        m = ttk.Frame(cuerpo, padding=10)
        m.grid(row=0, column=0, sticky="nw")
        ttk.Separator(cuerpo, orient="vertical").grid(row=0, column=1, sticky="ns", pady=8)

        def fila(r, texto):
            etq = ttk.Label(m, text=texto)
            etq.grid(row=r, column=0, sticky="w", pady=3)
            return etq

        fila(0, "Nombre:")
        ttk.Entry(m, textvariable=self.var_nombre, width=28).grid(row=0, column=1, columnspan=2,
                                                                  sticky="we", pady=3)
        fila(1, "Tipo de acción:")
        ttk.Combobox(m, textvariable=self.var_tipo, values=TIPOS_ACCION, state="readonly",
                     width=12).grid(row=1, column=1, sticky="w", pady=3)
        ttk.Label(m, text="(click, texto, bool, graf, nulo)", foreground="#666"
                  ).grid(row=1, column=2, sticky="w")
        fila(2, "Descripción de la acción:")
        ttk.Entry(m, textvariable=self.var_accion, width=28).grid(row=2, column=1, columnspan=2,
                                                                  sticky="we", pady=3)
        fila(3, "Estilo de fuente:")
        ttk.Combobox(m, textvariable=self.var_estilo, values=self._etq_estilo,
                     state="readonly",
                     width=18).grid(row=3, column=1, columnspan=2, sticky="we", pady=3)
        fila(4, "Valor máximo:")
        ttk.Entry(m, textvariable=self.var_vmax, width=10).grid(row=4, column=1, sticky="w", pady=3)
        ttk.Label(m, text="(vacío = sin límite)", foreground="#666").grid(row=4, column=2,
                                                                          sticky="w")
        fila(5, "Desplazamiento vertical:")
        _Spin(m, from_=-50, to=50, width=6, textvariable=self.var_desp).grid(row=5, column=1,
                                                                             sticky="w", pady=3)
        ttk.Checkbutton(m, text="Publicar en estadísticas", variable=self.var_publicar
                        ).grid(row=6, column=0, columnspan=2, sticky="w", pady=(6, 3))

        ttk.Separator(m, orient="horizontal").grid(row=7, column=0, columnspan=3, sticky="we",
                                                   pady=8)
        self.titulo_icono = ttk.Label(m, text="Icono (junto al valor; en 'graf' ocupa "
                                             "todo el control):",
                                      font=(FUENTE, 9, "bold"))
        self.titulo_icono.grid(row=8, column=0, columnspan=3, sticky="w")
        self.etq_imgpos = fila(9, "Posición del icono:")
        self.combo_imgpos = ttk.Combobox(m, textvariable=self.var_imgpos,
                                         values=list(IMG_POS_ETIQUETA.values()),
                                         state="readonly", width=12)
        self.combo_imgpos.grid(row=9, column=1, sticky="w", pady=3)
        self.etq_dir = fila(10, "Icono (nombre del archivo):")
        self.entrada_dir = ttk.Entry(m, textvariable=self.var_dir, width=22)
        self.entrada_dir.grid(row=10, column=1, sticky="we", pady=3)
        self.boton_dir = ttk.Button(m, text="Examinar...", command=self._buscar)
        self.boton_dir.grid(row=10, column=2, sticky="w", padx=4)

        # --- Panel derecho: vista previa a tamano real ---
        vp = ttk.Frame(cuerpo, padding=10)
        vp.grid(row=0, column=2, sticky="nw")
        ttk.Label(vp, text="Vista previa", font=(FUENTE, 9, "bold")).pack(anchor="w")
        ttk.Label(vp, text="Valor de ejemplo:").pack(anchor="w", pady=(8, 0))
        ttk.Entry(vp, textvariable=self.var_muestra, width=12).pack(anchor="w", pady=2)
        ttk.Label(vp, text="Prueba con el valor más largo que\npueda alcanzar la acción.",
                  foreground="#666", justify="left").pack(anchor="w")
        self.lienzo = tk.Canvas(vp, width=ANCHO_MUESTRA, height=ALTO_MUESTRA,
                                bg="#f4f4f4", highlightthickness=1,
                                highlightbackground="#bbb")
        self.lienzo.pack(anchor="w", pady=8)
        self.aviso = ttk.Label(vp, text="", foreground="#b00", justify="left", wraplength=200)
        self.aviso.pack(anchor="w")
        self.escala_vp = ttk.Label(vp, text="", foreground="#666")
        self.escala_vp.pack(anchor="w")
        # Que fuente se esta asignando realmente, no solo su descripcion.
        self.detalle_estilo = ttk.Label(vp, text="", foreground="#666", justify="left",
                                        wraplength=200)
        self.detalle_estilo.pack(anchor="w", pady=(4, 0))
        # El fondo no se toca aqui (es del parcial), pero conviene decir de donde sale.
        lado = self._lado_actual()
        ttk.Label(vp, text=f"Fondo: lado «{(lado or {}).get('nombre', 'sin lado')}», "
                           f"intensidad {int(self.color_v)}.\n"
                           f"Se cambia en el parcial (doble clic en el origen).",
                  foreground="#666", justify="left").pack(anchor="w")

        for var in (self.var_muestra, self.var_estilo, self.var_imgpos, self.var_dir,
                    self.var_desp, self.var_tipo):
            var.trace_add("write", lambda *a: self._refrescar_muestra())
        self._img_tk = []
        self._refrescar_muestra()

        bot = ttk.Frame(m)
        bot.grid(row=11, column=0, columnspan=3, sticky="e", pady=(12, 0))
        ttk.Button(bot, text="Aceptar", command=self._aceptar).pack(side=tk.LEFT, padx=3)
        ttk.Button(bot, text="Cancelar", command=self._cancelar).pack(side=tk.LEFT)
        self._finalizar()

    # --- Vista previa ---
    def _etq_de_id(self, ident):
        for etq, e in self._estilo_por_etq.items():
            if e["id"] == ident:
                return etq
        return self._etq_estilo[0] if self._etq_estilo else ""

    def _estilo_actual(self):
        est = self._estilo_por_etq.get(self.var_estilo.get())
        if est is not None:
            return est
        return self.estilos[0] if self.estilos else None

    def _fondo(self):
        """Mismo criterio que en el mapa: tono y saturacion del lado del parcial e
        intensidad (color_v) del propio parcial. Sin catalogo de lados, el color de
        respaldo."""
        return color_lado(self._lado_actual(), self.color_v) or COL_BOTON

    def _refrescar_muestra(self):
        if not hasattr(self, "lienzo"):
            return
        self.lienzo.delete("all")
        self._img_tk = []
        (x1, y1, x2, y2), k, (ancho, alto) = self._marco_muestra()
        self.lienzo.create_rectangle(x1, y1, x2, y2, fill=self._fondo(), outline="#333")
        self.escala_vp.config(text=self._rotulo_escala(ancho, alto, k))

        tipo = self.var_tipo.get()
        self._icono_activo(tipo)
        estilo = self._estilo_actual()
        # Se actualiza antes de las salidas anticipadas: aunque el tipo de accion no
        # dibuje texto, conviene ver que estilo lleva asignado el boton.
        if hasattr(self, "detalle_estilo"):
            self.detalle_estilo.config(text=resumen_estilo(estilo))
        desp = self._entero(self.var_desp) * k
        if tipo == "nulo":
            self.aviso.config(text="")
            return
        if tipo == "graf":
            self._pintar_imagen(self.var_dir.get().strip(), x1, y1, x2, y2)
            self.aviso.config(text="" if self.var_dir.get().strip()
                              else "Tipo 'graf' sin imagen: el control saldría vacío.")
            return

        # El icono se dibuja en cualquier tipo que muestre valor, no solo en 'click':
        # las ediciones 2025 y 2026 tienen controles 'bool' con su icono.
        ruta = self.var_dir.get().strip()
        pos = next((k2 for k2, v in IMG_POS_ETIQUETA.items() if v == self.var_imgpos.get()), "")
        r_ico, r_txt = reparto_icono(x1, y1, x2, y2, pos if ruta else "")
        if r_ico:
            self._pintar_imagen(ruta, *r_ico)
        texto = MARCA_BOOL if tipo == "bool" else self.var_muestra.get()
        color = COL_MARCA_BOOL if tipo == "bool" else color_de_estilo(estilo)

        tw = r_txt[2] - r_txt[0]
        th = r_txt[3] - r_txt[1]
        tam_est = int((estilo or {}).get("tamano_fuente") or 0)
        if tam_est > 0:
            px = max(1, int(round(tam_est * k)))
            # El aviso se calcula con las medidas REALES, no con las de la vista previa.
            cabe = cabe_texto(estilo, texto, tam_est, tw / k, th / k)
        else:
            px = tam_automatico(estilo, texto, tw, th)
            cabe = True
        self.lienzo.create_text((r_txt[0] + r_txt[2]) / 2, (r_txt[1] + r_txt[3]) / 2 + desp,
                                text=texto, fill=color, font=fuente_de_estilo(estilo, px))
        if not cabe:
            self.aviso.config(text=f"El texto «{texto}» no cabe con el estilo elegido "
                                   f"({tam_est} px). Usa un estilo menor o agranda el botón.")
        elif tam_est <= 0:
            self.aviso.config(text="El estilo no tiene tamaño: el texto se ajusta al hueco.")
        else:
            self.aviso.config(text="")

    def _icono_activo(self, tipo):
        """Que campos del icono tienen sentido segun el tipo:

        - 'nulo' no genera ningun control en la aplicacion, asi que no se dibuja nada.
        - 'graf' usa la imagen como contenido y ocupa el control entero, asi que su
          posicion no aplica.
        - 'click', 'texto' y 'bool' muestran un valor y pueden llevar icono al lado
          (en las ediciones reales hay 'bool' con icono).
        """
        usa_imagen = tipo != "nulo"
        usa_pos = tipo not in ("nulo", "graf")
        gris, negro = "#999", ""
        self.titulo_icono.config(foreground=negro if usa_imagen else gris)
        self.combo_imgpos.config(state="readonly" if usa_pos else "disabled")
        self.etq_imgpos.config(foreground=negro if usa_pos else gris)
        estado = "normal" if usa_imagen else "disabled"
        self.entrada_dir.config(state=estado)
        self.boton_dir.config(state=estado)
        self.etq_dir.config(foreground=negro if usa_imagen else gris)

    def _pintar_imagen(self, nombre, x1, y1, x2, y2):
        """`nombre` es lo que se guarda en la tabla: el archivo, sin directorio."""
        w = max(1, int(x2 - x1) - 2)
        h = max(1, int(y2 - y1) - 2)
        img = None
        ruta = self._resolver(str(nombre or "").strip())
        if ruta:
            try:
                img = Image.open(ruta).convert("RGBA").resize((w, h), RESAMPLE)
            except Exception:
                img = None
        if img is None:
            self.lienzo.create_rectangle(x1, y1, x2, y2, outline="#999", dash=(3, 2))
            self.lienzo.create_text((x1 + x2) / 2, (y1 + y2) / 2, text="?", fill="#999")
            return
        ph = ImageTk.PhotoImage(img)
        self._img_tk.append(ph)
        self.lienzo.create_image((x1 + x2) / 2, (y1 + y2) / 2, image=ph)

    def _buscar(self):
        """El icono se coge de la carpeta de graficos del editor y de ninguna otra: en
        Arbitraje_TipoAcciones.directorio solo cabe el nombre del archivo, porque el
        directorio raiz lo pone la configuracion de la aplicacion de arbitraje. Una
        imagen de otro sitio no se podria dibujar ni aqui ni en el arbitraje."""
        carpeta = self._carpeta()
        ruta = filedialog.askopenfilename(
            parent=self, title="Icono del control", initialdir=carpeta,
            filetypes=[("PNG", "*.png"), ("Todos", "*.*")])
        if not ruta:
            return
        if os.path.normcase(os.path.dirname(os.path.abspath(ruta))) != \
                os.path.normcase(os.path.abspath(carpeta)):
            messagebox.showwarning(
                "El icono tiene que estar en la carpeta de gráficos",
                f"«{os.path.basename(ruta)}» está en otra carpeta.\n\nEn la base de "
                f"datos solo se guarda el nombre del archivo, así que los iconos de "
                f"los controles tienen que estar en:\n\n{carpeta}\n\nCópialo ahí y "
                f"vuelve a elegirlo.", parent=self)
            return
        self.var_dir.set(os.path.basename(ruta))

    def _aceptar(self):
        nombre = self.var_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Falta el nombre", "Escribe un nombre para el control.",
                                   parent=self)
            return
        vm = self.var_vmax.get().strip()
        try:
            valor_maximo = int(vm) if vm else None
        except ValueError:
            messagebox.showwarning("Valor máximo no válido",
                                   "Debe ser un número entero, o vacío para 'sin límite'.",
                                   parent=self)
            return
        tipo_d = self._entero(self.var_desp)
        img_pos = next((k for k, v in IMG_POS_ETIQUETA.items() if v == self.var_imgpos.get()), "")
        contenido = dict(self.contenido)
        contenido["valor"] = self.var_muestra.get()
        self.resultado = {"nombre": nombre, "contenido": contenido, "param": {
            "tipo_accion": self.var_tipo.get(),
            "accion": self.var_accion.get().strip() or nombre,
            "estilo": (self._estilo_actual() or {}).get("id", 0),
            "publicar": bool(self.var_publicar.get()),
            "valor_maximo": valor_maximo,
            "img_pos": img_pos,
            # Solo el nombre, aunque el campo traiga una ruta de un archivo antiguo.
            "directorio": os.path.basename(self.var_dir.get().strip()),
            "tipo_d": tipo_d,
        }}
        self.destroy()