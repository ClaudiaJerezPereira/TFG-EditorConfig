"""Dialogo de un parcial: la colocacion de un grupo (Arbitraje_ZonaAcciones)."""
import tkinter as tk
from tkinter import messagebox, ttk

from ..apariencia import FUENTE, Spin as _Spin
from .base import _DialogoBase


class DialogoZona(_DialogoBase):
    """Parametros de una colocacion (parcial). Tabla Arbitraje_ZonaAcciones.

    Tambien se editan aqui el nombre del GRUPO al que pertenece el parcial y si es
    comun (Arbitraje_GrupoAcciones.comun: la marca con la que el arbitraje sabe que al
    tocar una accion tiene que refrescar los parciales de todos los lados y no solo el
    del equipo tocado), porque el grupo no tiene otro sitio donde editarse. Del total, lo unico
    que decide el parcial es si lo muestra
    (Arbitraje_ZonaAcciones.mostrar_puntos); su tipo de letra y su desplazamiento
    son del grupo y se editan con doble clic sobre la propia etiqueta.
    """

    def __init__(self, padre, nombre="", param=None, inv=False,
                 lados=None, arbitros=None, estilos=None,
                 grupo_nombre="", grupo_comun=False,
                 grupos_existentes=None, geom_total=None):
        super().__init__(padre)
        self.title("Parámetros del parcial (zona)")
        self.resultado = None
        self.transient(padre)
        self.resizable(False, False)
        param = param or {}
        self.lados = lados or []
        self.arbitros = arbitros or []
        self.estilos = estilos or []
        self.grupo_actual = grupo_nombre
        self.grupos_existentes = grupos_existentes or []

        self.var_grupo = tk.StringVar(value=grupo_nombre)
        self.var_comun = tk.BooleanVar(value=bool(grupo_comun))
        self.var_nombre = tk.StringVar(value=nombre)
        self.var_lado = tk.StringVar(value=self._nombre_por_id(self.lados, param.get("lado"), "nombre"))
        self.var_arbitro = tk.StringVar(
            value=self._nombre_por_id(self.arbitros, param.get("arbitro"), "nombre", permitir_ninguno=True))
        self.var_reflejar = tk.BooleanVar(value=bool(inv))
        self.var_defecto = tk.StringVar(value=str(int(param.get("valor_defecto", 0))))
        self.var_colorv = tk.StringVar(value=str(int(param.get("color_v", 255))))
        self.var_mostrar_total = tk.BooleanVar(value=bool(param.get("mostrar_puntos", True)))
        # De la etiqueta del total, el parcial solo decide si la muestra. Su geometria
        # es unica para todo el mapa (modo Total) y su tipo de letra y desplazamiento
        # son del grupo (Arbitraje_TotalGrupoAcciones): las dos cosas se editan con
        # doble clic sobre la etiqueta. Aqui solo se informa de como ha quedado.
        self.geom_total = geom_total

        # --- Grupo al que pertenece el parcial (Arbitraje_GrupoAcciones) ---
        # Se edita aqui porque afecta a TODAS las colocaciones de este grupo.
        gf = ttk.LabelFrame(self, text="Grupo (afecta a todas sus colocaciones)", padding=10)
        gf.pack(fill=tk.X, padx=10, pady=(10, 0))
        ttk.Label(gf, text="Nombre del grupo:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(gf, textvariable=self.var_grupo, width=24).grid(row=0, column=1, sticky="we",
                                                                  pady=2)
        ttk.Checkbutton(gf, text="Común (el valor de un lado afecta a todos los lados)",
                        variable=self.var_comun).grid(row=1, column=0, columnspan=2,
                                                      sticky="w", pady=(4, 0))

        m = ttk.Frame(self, padding=10)
        m.pack(fill=tk.BOTH, expand=True)

        def combo(r, texto, var, valores):
            ttk.Label(m, text=texto).grid(row=r, column=0, sticky="w", pady=3)
            ttk.Combobox(m, textvariable=var, values=valores, state="readonly",
                         width=20).grid(row=r, column=1, columnspan=3, sticky="we", pady=3)

        ttk.Label(m, text="Nombre del parcial:").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(m, textvariable=self.var_nombre, width=30).grid(row=0, column=1, columnspan=3,
                                                                  sticky="we", pady=3)
        combo(1, "Lado:", self.var_lado, [l["nombre"] for l in self.lados])
        combo(2, "Árbitro:", self.var_arbitro,
              ["(ninguno)"] + [a["nombre"] for a in self.arbitros])

        ttk.Label(m, text="Valor por defecto:").grid(row=3, column=0, sticky="w", pady=3)
        _Spin(m, from_=0, to=9999, width=7, textvariable=self.var_defecto).grid(row=3, column=1,
                                                                                sticky="w", pady=3)
        ttk.Label(m, text="Intensidad color (0-255):").grid(row=3, column=2, sticky="e", pady=3)
        _Spin(m, from_=0, to=255, width=6, textvariable=self.var_colorv).grid(row=3, column=3,
                                                                              sticky="w", pady=3)
        ttk.Checkbutton(m, text="Reflejar en horizontal", variable=self.var_reflejar
                        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(6, 3))

        ttk.Separator(m, orient="horizontal").grid(row=5, column=0, columnspan=4, sticky="we",
                                                   pady=8)
        ttk.Label(m, text="Etiqueta del total:",
                  font=(FUENTE, 9, "bold")).grid(row=6, column=0, columnspan=4, sticky="w")
        hay_total = bool(self.geom_total and (self.geom_total[2] or self.geom_total[3]))
        if hay_total:
            x, y, w, h = (int(round(v)) for v in self.geom_total)
            texto = (f"X={x}, Y={y}, ancho={w}, alto={h} (píxeles respecto al origen "
                     f"del grupo).\n"
                     f"Es la misma para todos los grupos. Su tipo de letra y su "
                     f"desplazamiento se editan\ncon doble clic sobre la propia "
                     f"etiqueta; aquí solo se elige si este parcial la muestra.")
        else:
            texto = ("El mapa no tiene etiqueta de total.\n"
                     "Para añadirla, activa el modo TOTAL y arrastra entre dos cruces de "
                     "guías; valdrá para todos los grupos.")
        ttk.Label(m, text=texto, foreground="#444", justify="left"
                  ).grid(row=7, column=0, columnspan=4, sticky="w", pady=(2, 4))
        chk = ttk.Checkbutton(m, text="Mostrar la etiqueta del total en este parcial",
                              variable=self.var_mostrar_total)
        chk.grid(row=8, column=0, columnspan=4, sticky="w", pady=(0, 4))
        if not hay_total:
            chk.state(["disabled"])

        bot = ttk.Frame(m)
        bot.grid(row=9, column=0, columnspan=4, sticky="e", pady=(12, 0))
        ttk.Button(bot, text="Aceptar", command=self._aceptar).pack(side=tk.LEFT, padx=3)
        ttk.Button(bot, text="Cancelar", command=self._cancelar).pack(side=tk.LEFT)
        self._finalizar()

    def _aceptar(self):
        nombre = self.var_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Falta el nombre", "Escribe un nombre para el parcial.",
                                   parent=self)
            return
        grupo = self.var_grupo.get().strip()
        if not grupo:
            messagebox.showwarning("Falta el grupo", "El grupo debe tener un nombre.", parent=self)
            return
        if grupo != self.grupo_actual and grupo in self.grupos_existentes:
            messagebox.showwarning("Nombre repetido",
                                   f"Ya existe un grupo llamado '{grupo}'.", parent=self)
            return

        self.resultado = {
            "nombre": nombre, "inv": bool(self.var_reflejar.get()),
            "grupo_nombre": grupo, "grupo_comun": bool(self.var_comun.get()),
            "param": {
                "lado": self._id_por_nombre(self.lados, self.var_lado.get(), "nombre"),
                "arbitro": self._id_por_nombre(self.arbitros, self.var_arbitro.get(), "nombre",
                                               ninguno=True),
                "valor_defecto": self._entero(self.var_defecto),
                "color_v": max(0, min(255, self._entero(self.var_colorv, 255))),
                "mostrar_puntos": bool(self.var_mostrar_total.get()),
            }}
        self.destroy()