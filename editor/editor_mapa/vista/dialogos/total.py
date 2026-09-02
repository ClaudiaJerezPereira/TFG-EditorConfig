"""Dialogo de la etiqueta del total (Arbitraje_TotalGrupoAcciones)."""
import tkinter as tk
from tkinter import messagebox, ttk

from ..apariencia import FUENTE, Spin as _Spin
from .base import _DialogoBase


class DialogoTotal(_DialogoBase):
    """Etiqueta con el total de puntos. Tabla Arbitraje_TotalGrupoAcciones.

    La etiqueta es una sola para todo el mapa: su rectangulo (X, Y, ancho, alto
    respecto al origen) es el mismo en todos los grupos y no se edita aqui, sino
    dibujandola de nuevo en el modo Total. Lo que si es de cada grupo son el tipo de
    letra y el desplazamiento vertical del texto, que son los dos campos propios de
    la tabla; por eso se editan sobre la copia en la que se ha hecho doble clic y el
    dialogo dice a que grupo pertenece.

    El nombre no llega a la base de datos (la tabla no tiene columna de nombre y el
    texto que se dibuja siempre es TOTAL): es solo para reconocerla en el editor.
    """

    def __init__(self, padre, nombre="", grupo_nombre="", estilos=None,
                 total_estilo=None, total_d=0, geom_total=None):
        super().__init__(padre)
        self.title("Etiqueta del total")
        self.resultado = None
        self.transient(padre)
        self.resizable(False, False)
        self.estilos = estilos or []

        self.var_nombre = tk.StringVar(value=nombre)
        self.var_estilo = tk.StringVar(
            value=self._nombre_por_id(self.estilos, total_estilo, "descripcion"))
        self.var_zd = tk.StringVar(value=str(int(total_d or 0)))

        m = ttk.Frame(self, padding=12)
        m.pack(fill=tk.BOTH, expand=True)

        ttk.Label(m, text="Nombre de la etiqueta:").grid(row=0, column=0, sticky="w",
                                                         pady=3)
        e = ttk.Entry(m, textvariable=self.var_nombre, width=28)
        e.grid(row=0, column=1, sticky="we", pady=3)
        ttk.Label(m, text="Solo sirve para reconocerla en el editor: el texto que se "
                          "dibuja\nen el arbitraje es siempre el total de puntos de "
                          "la zona.",
                  foreground="#666", justify="left").grid(row=1, column=0, columnspan=2,
                                                          sticky="w", pady=(0, 8))

        ttk.Separator(m, orient="horizontal").grid(row=2, column=0, columnspan=2,
                                                   sticky="we", pady=(0, 8))
        ttk.Label(m, text=f"Grupo «{grupo_nombre}»", font=(FUENTE, 9, "bold")
                  ).grid(row=3, column=0, columnspan=2, sticky="w")
        ttk.Label(m, text="El tipo de letra y el desplazamiento son de este grupo: "
                          "cambian en todas\nsus colocaciones, y cada grupo puede "
                          "tener los suyos.",
                  foreground="#444", justify="left").grid(row=4, column=0, columnspan=2,
                                                          sticky="w", pady=(2, 6))

        ttk.Label(m, text="Estilo de fuente:").grid(row=5, column=0, sticky="w", pady=3)
        ttk.Combobox(m, textvariable=self.var_estilo,
                     values=[s["descripcion"] for s in self.estilos],
                     state="readonly", width=25).grid(row=5, column=1, sticky="we",
                                                      pady=3)
        ttk.Label(m, text="Desplazamiento vertical del texto:").grid(row=6, column=0,
                                                                     sticky="w", pady=3)
        _Spin(m, from_=-50, to=50, width=6, textvariable=self.var_zd
              ).grid(row=6, column=1, sticky="w", pady=3)

        ttk.Separator(m, orient="horizontal").grid(row=7, column=0, columnspan=2,
                                                   sticky="we", pady=8)
        x, y, w, h = (int(round(v)) for v in (geom_total or (0, 0, 0, 0)))
        ttk.Label(m, text=f"Posición: X={x}, Y={y}, ancho={w}, alto={h} (píxeles "
                          f"respecto al origen\ndel grupo). Es la misma en todos los "
                          f"grupos; para cambiarla, elimina la\netiqueta y vuelve a "
                          f"dibujarla en el modo Total. En cada parcial se elige\nsi "
                          f"se muestra, y de él salen también el color y su "
                          f"intensidad.",
                  foreground="#444", justify="left").grid(row=8, column=0, columnspan=2,
                                                          sticky="w")

        bot = ttk.Frame(m)
        bot.grid(row=9, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(bot, text="Aceptar", command=self._aceptar).pack(side=tk.LEFT, padx=3)
        ttk.Button(bot, text="Cancelar", command=self._cancelar).pack(side=tk.LEFT)
        self._finalizar(e)

    def _aceptar(self):
        nombre = self.var_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Falta el nombre",
                                   "Escribe un nombre para la etiqueta del total.",
                                   parent=self)
            return
        try:
            zd = int(float(self.var_zd.get()))
        except ValueError:
            zd = 0
        self.resultado = {
            "nombre": nombre,
            # Arbitraje_TotalGrupoAcciones: los dos campos propios del grupo.
            "total_estilo": self._id_por_nombre(self.estilos, self.var_estilo.get(),
                                                "descripcion"),
            "total_d": zd}
        self.destroy()