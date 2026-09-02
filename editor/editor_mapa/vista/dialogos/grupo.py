"""Dialogo de un grupo (Arbitraje_GrupoAcciones)."""
import tkinter as tk
from tkinter import messagebox, ttk

from .base import _DialogoBase


class DialogoGrupo(_DialogoBase):
    """Nombre y parametros de un grupo. Tabla Arbitraje_GrupoAcciones.

    Un grupo puede contener botones y etiquetas (el total es unico para todo el
    mapa): no hay grupos de una clase u otra, sino un unico tipo de grupo con los
    elementos que haga falta.
    """

    def __init__(self, padre, nombre="", comun=False, existentes=None):
        super().__init__(padre)
        self.title("Grupo")
        self.resultado = None
        self.transient(padre)
        self.resizable(False, False)
        self.actual = nombre
        self.existentes = existentes or []

        self.var_nombre = tk.StringVar(value=nombre)
        self.var_comun = tk.BooleanVar(value=bool(comun))

        m = ttk.Frame(self, padding=12)
        m.pack(fill=tk.BOTH, expand=True)
        ttk.Label(m, text="Nombre del grupo\n(ej.: Despensa, Nido, Termómetro, Granero):"
                  ).grid(row=0, column=0, sticky="w")
        e = ttk.Entry(m, textvariable=self.var_nombre, width=30)
        e.grid(row=1, column=0, sticky="we", pady=(4, 8))
        ttk.Checkbutton(m, text="Común (el valor de un lado afecta a ambos lados)",
                        variable=self.var_comun).grid(row=2, column=0, sticky="w")
        ttk.Label(m, text="Un grupo puede llevar botones y etiquetas; el total es\n"
                          "común a todo el mapa.",
                  foreground="#666").grid(row=3, column=0, sticky="w", pady=(6, 0))
        bot = ttk.Frame(m)
        bot.grid(row=4, column=0, sticky="e", pady=(12, 0))
        ttk.Button(bot, text="Aceptar", command=self._aceptar).pack(side=tk.LEFT, padx=3)
        ttk.Button(bot, text="Cancelar", command=self._cancelar).pack(side=tk.LEFT)
        self._finalizar(e)

    def _aceptar(self):
        nombre = self.var_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Nombre vacío", "Escribe un nombre para el grupo.", parent=self)
            return
        if nombre != self.actual and nombre in self.existentes:
            messagebox.showwarning("Nombre repetido",
                                   f"Ya existe un grupo llamado '{nombre}'.", parent=self)
            return
        self.resultado = {"nombre": nombre, "comun": bool(self.var_comun.get())}
        self.destroy()