"""Editor generico de una tabla de referencia (lados, arbitros, estilos)."""
import tkinter as tk
from tkinter import colorchooser, messagebox, simpledialog, ttk

from ...modelo.constantes import ID_MINIMO_CATALOGO
from ..apariencia import FUENTE
from ..fuentes import color_de_estilo, familias_disponibles, fuente_de_estilo
from .base import _DialogoBase

# Valores admitidos en Arbitraje_EstiloFuente.estilo_fuente. La columna es
# VARCHAR(10), asi que la negrita cursiva va junta y sin espacio.
ESTILOS_FUENTE = ("", "bold", "italic", "bolditalic", "underline")

# Tamano con el que se dibuja la muestra del estilo seleccionado.
PX_MUESTRA = 28


def _tipo_base(tipo):
    """El tipo puede llevar sus opciones detras: 'lista:a|b|c'."""
    return str(tipo).split(":", 1)[0]


def _opciones(tipo):
    tipo = str(tipo)
    return tipo.split(":", 1)[1].split("|") if ":" in tipo else []


class DialogoCatalogo(_DialogoBase):
    """Editor generico de una tabla de referencia (lados, arbitros, estilos).

    columnas: lista de (clave, etiqueta, tipo), con tipo:
        "int", "float", "str"  -> se teclea el valor
        "fuente"               -> se elige entre las familias instaladas
        "color"                -> selector de color
        "lista:a|b|c"          -> se elige entre esos valores
    Los tres ultimos existen porque un estilo de fuente tecleado a mano (una familia
    que no esta instalada, un estilo que Tk no entiende) se dibuja igual que el de
    por defecto, y parece que el estilo no se aplica.

    Con `muestra_fuente`, cada fila se previsualiza con su propia fuente.

    `id_minimo` es el valor mas pequeno que admite la columna ID: por defecto 1,
    porque es la clave primaria de la tabla y no puede ser ni 0 ni negativa.

    Con `id_automatico` el ID no se teclea: es la posicion en la lista y se renumera
    solo al anadir, eliminar o mover una fila. Lo usan los catalogos cuyos
    identificadores tienen que ir seguidos y sin huecos, como los totales generales,
    que reservan los primeros ID_GRUPO_ACCIONES.
    """

    def __init__(self, padre, titulo, columnas, filas, muestra_fuente=False,
                 id_minimo=ID_MINIMO_CATALOGO, id_automatico=False):
        super().__init__(padre)
        self.title(titulo)
        self.resultado = None
        self.transient(padre)
        self.resizable(False, False)
        self.columnas = columnas
        self.id_minimo = int(id_minimo)
        self.id_automatico = bool(id_automatico)
        self.filas = [dict(f) for f in filas]   # copia editable
        if self.id_automatico:
            self._renumerar()

        m = ttk.Frame(self, padding=10)
        m.pack(fill=tk.BOTH, expand=True)
        claves = [c[0] for c in columnas]
        self.tabla = ttk.Treeview(m, columns=claves, show="headings", height=8, selectmode="browse")
        for clave, etq, _ in columnas:
            self.tabla.heading(clave, text=etq)
            self.tabla.column(clave, width=110, anchor="w")
        self.tabla.grid(row=0, column=0, columnspan=4, sticky="nswe")
        self.tabla.bind("<Double-1>", self._editar_celda)
        self._repintar()

        ttk.Button(m, text="Añadir fila", command=self._anadir).grid(row=1, column=0, pady=6,
                                                                     sticky="w")
        ttk.Button(m, text="Eliminar fila", command=self._eliminar).grid(row=1, column=1, pady=6,
                                                                         sticky="w")
        if self.id_automatico:
            ttk.Button(m, text="Subir", width=7,
                       command=lambda: self._mover(-1)).grid(row=1, column=2, pady=6)
            ttk.Button(m, text="Bajar", width=7,
                       command=lambda: self._mover(1)).grid(row=1, column=3, pady=6,
                                                            sticky="w")
            ayuda = ("Doble clic en una celda para editarla. El ID no se edita: "
                     f"es la posición en la lista, desde el {self.id_minimo}.")
        else:
            ayuda = (f"Doble clic en una celda para editarla. "
                     f"El ID debe ser {self.id_minimo} o mayor.")
        ttk.Label(m, text=ayuda, foreground="#666"
                  ).grid(row=2, column=0, columnspan=4, sticky="w", pady=(0, 4))

        # Muestra del estilo seleccionado: asi se ve al momento si la fuente elegida
        # existe y como queda, sin tener que cerrar y asignarla a una etiqueta.
        self.muestra = None
        if muestra_fuente:
            marco = ttk.LabelFrame(m, text="Muestra del estilo seleccionado", padding=6)
            marco.grid(row=3, column=0, columnspan=4, sticky="we", pady=(4, 0))
            self.muestra = tk.Label(marco, text="AaBbCc 0123 ÁÉÍÓÚÑ", bg="white",
                                    anchor="center", height=2)
            self.muestra.pack(fill=tk.X)
            self.tabla.bind("<<TreeviewSelect>>", lambda e: self._refrescar_muestra())
            self._refrescar_muestra()

        bot = ttk.Frame(m)
        bot.grid(row=4, column=0, columnspan=4, sticky="e", pady=(8, 0))
        ttk.Button(bot, text="Aceptar", command=self._aceptar).pack(side=tk.LEFT, padx=3)
        ttk.Button(bot, text="Cancelar", command=self._cancelar).pack(side=tk.LEFT)
        self._finalizar()

    def _repintar(self):
        self.tabla.delete(*self.tabla.get_children())
        for i, fila in enumerate(self.filas):
            self.tabla.insert("", "end", iid=str(i),
                              values=[fila.get(c[0], "") for c in self.columnas])

    def _nuevo_id(self):
        """Primer identificador libre a partir del minimo del catalogo (nunca 0 ni
        negativo, porque el ID es la clave primaria de la tabla)."""
        usados = set()
        for f in self.filas:
            try:
                usados.add(int(f.get("id")))
            except (TypeError, ValueError):
                pass
        n = self.id_minimo
        while n in usados:
            n += 1
        return n

    def _renumerar(self):
        """El ID pasa a ser la posicion en la lista, sin huecos."""
        for n, fila in enumerate(self.filas, self.id_minimo):
            fila["id"] = n

    def _mover(self, paso):
        """Sube o baja la fila seleccionada. Como el ID es la posicion, esto es lo
        que permite decidir en que orden reservan los identificadores."""
        sel = self.tabla.selection()
        if not sel:
            return
        i = int(sel[0])
        j = i + paso
        if not 0 <= j < len(self.filas):
            return
        self.filas[i], self.filas[j] = self.filas[j], self.filas[i]
        self._renumerar()
        self._repintar()
        self.tabla.selection_set(str(j))
        self._refrescar_muestra()

    def _anadir(self):
        """La fila nueva sale ya con valores utilizables: una fila vacia se dibuja
        igual que la de por defecto y parece que el estilo no hace nada."""
        fila = {}
        for clave, _, tipo in self.columnas:
            base = _tipo_base(tipo)
            if clave == "id":
                fila["id"] = self._nuevo_id()
            elif base in ("int", "float"):
                fila[clave] = 0
            elif base == "color":
                fila[clave] = "#000000"
            elif base == "fuente":
                familias = familias_disponibles()
                fila[clave] = FUENTE if FUENTE in familias else (familias[0] if familias
                                                                 else FUENTE)
            elif base == "lista":
                opciones = _opciones(tipo)
                fila[clave] = opciones[0] if opciones else ""
            else:
                fila[clave] = ""
        self.filas.append(fila)
        if self.id_automatico:
            self._renumerar()
        self._repintar()
        self.tabla.selection_set(str(len(self.filas) - 1))
        self._refrescar_muestra()

    def _eliminar(self):
        sel = self.tabla.selection()
        if not sel:
            return
        idx = int(sel[0])
        # La primera fila es la que se usa como valor por defecto (Catalogos.estilo_defecto),
        # asi que borrarla cambia lo que hereda todo lo que no tenga estilo propio.
        if idx == 0 and len(self.filas) > 1:
            if not messagebox.askyesno(
                    "Eliminar",
                    "Vas a eliminar la primera fila del catálogo, que es la que se usa "
                    "como valor por defecto. ¿Seguro?", parent=self):
                return
        del self.filas[idx]
        if self.id_automatico:
            self._renumerar()
        self._repintar()
        self._refrescar_muestra()

    def _editar_celda(self, event):
        fila_id = self.tabla.identify_row(event.y)
        col = self.tabla.identify_column(event.x)
        if not fila_id or not col:
            return
        idx = int(fila_id)
        cidx = int(col[1:]) - 1
        clave, etq, tipo = self.columnas[cidx]
        if clave == "id" and self.id_automatico:
            messagebox.showinfo(
                "El ID no se edita",
                "En este catálogo el ID es la posición en la lista: los "
                "identificadores tienen que ir seguidos y sin huecos. Usa «Subir» y "
                "«Bajar» para cambiar el orden.", parent=self)
            return
        actual = self.filas[idx].get(clave, "")
        base = _tipo_base(tipo)
        if base == "int" and clave == "id":
            # Sin minvalue a proposito: el que trae simpledialog avisa en ingles
            # ("The allowed minimum value is 1"), porque el texto esta escrito a fuego
            # en la biblioteca estandar de Python y no se puede traducir. La
            # comprobacion la hace _id_valido(), que avisa en español.
            v = simpledialog.askinteger(
                etq, f"{etq} (mínimo {self.id_minimo}):",
                initialvalue=max(self.id_minimo, int(actual or self.id_minimo)),
                parent=self)
        elif base == "int":
            v = simpledialog.askinteger(etq, f"{etq}:", initialvalue=int(actual or 0), parent=self)
        elif base == "float":
            v = simpledialog.askfloat(etq, f"{etq}:", initialvalue=float(actual or 0), parent=self)
        elif base == "color":
            v = colorchooser.askcolor(color=str(actual) or "#000000", title=etq,
                                      parent=self)[1]
        elif base == "fuente":
            v = self._elegir(etq, familias_disponibles(), str(actual))
        elif base == "lista":
            v = self._elegir(etq, _opciones(tipo), str(actual))
        else:
            v = simpledialog.askstring(etq, f"{etq}:", initialvalue=str(actual), parent=self)
        if v is None:
            return
        if clave == "id" and not self._id_valido(v):
            return
        if clave == "id" and any(f.get("id") == v
                                 for j, f in enumerate(self.filas) if j != idx):
            messagebox.showwarning(
                "Identificador repetido",
                f"Ya hay otra fila con el ID {v}. El ID es la clave primaria de la "
                f"tabla, así que tiene que ser distinto en cada fila.", parent=self)
            return
        self.filas[idx][clave] = v
        self._repintar()
        self.tabla.selection_set(str(idx))
        self._refrescar_muestra()

    def _elegir(self, etq, opciones, actual):
        """Pequeno dialogo para elegir de una lista cerrada. Devuelve None si se
        cancela, igual que los simpledialog."""
        if not opciones:
            return simpledialog.askstring(etq, f"{etq}:", initialvalue=actual, parent=self)
        d = tk.Toplevel(self)
        d.title(etq)
        d.transient(self)
        d.resizable(False, False)
        elegido = {"v": None}
        var = tk.StringVar(value=actual if actual in opciones else opciones[0])
        marco = ttk.Frame(d, padding=10)
        marco.pack(fill=tk.BOTH, expand=True)
        ttk.Label(marco, text=f"{etq}:").pack(anchor="w")
        combo = ttk.Combobox(marco, textvariable=var, values=list(opciones),
                             state="readonly", width=32)
        combo.pack(pady=6)
        def aceptar():
            elegido["v"] = var.get()
            d.destroy()
        bot = ttk.Frame(marco)
        bot.pack(anchor="e")
        ttk.Button(bot, text="Aceptar", command=aceptar).pack(side=tk.LEFT, padx=3)
        ttk.Button(bot, text="Cancelar", command=d.destroy).pack(side=tk.LEFT)
        d.bind("<Return>", lambda e: aceptar())
        d.bind("<Escape>", lambda e: d.destroy())
        combo.focus_set()
        d.grab_set()
        d.wait_window(d)
        self.grab_set()   # el dialogo de la tabla vuelve a ser el modal
        return elegido["v"]

    def _refrescar_muestra(self):
        if self.muestra is None:
            return
        sel = self.tabla.selection()
        if not sel:
            self.muestra.config(text="(selecciona una fila)", fg="#888",
                                font=fuente_de_estilo(None, 12))
            return
        estilo = self.filas[int(sel[0])]
        px = int(estilo.get("tamano_fuente") or 0) or PX_MUESTRA
        self.muestra.config(text="AaBbCc 0123 ÁÉÍÓÚÑ",
                            font=fuente_de_estilo(estilo, min(px, PX_MUESTRA * 2)),
                            fg=color_de_estilo(estilo))

    def _id_valido(self, valor):
        """Avisa y devuelve False si el identificador no llega al minimo del catalogo."""
        try:
            entero = int(valor)
        except (TypeError, ValueError):
            entero = None
        if entero is None or entero < self.id_minimo:
            messagebox.showwarning(
                "Identificador no válido",
                f"El ID {valor} no vale. El ID es la clave primaria de la tabla "
                f"(INT UNSIGNED), así que tiene que ser un entero de "
                f"{self.id_minimo} en adelante: ni 0 ni negativo.", parent=self)
            return False
        return True

    def _aceptar(self):
        if self.id_automatico:
            self._renumerar()
        # El ID es la clave primaria de la tabla: con uno repetido, o con un 0 o un
        # negativo, la base de datos rechazaria el script entero. Mejor no dejar salir
        # del dialogo asi.
        malos = sorted({f.get("id") for f in self.filas
                        if not isinstance(f.get("id"), int)
                        or f.get("id") < self.id_minimo}, key=str)
        if malos:
            messagebox.showwarning(
                "Identificadores no válidos",
                f"Hay filas con el ID {', '.join(map(str, malos))}.\n\n"
                f"El ID es la clave primaria de la tabla, así que tiene que ser un "
                f"entero de {self.id_minimo} en adelante: ni 0 ni negativo. Corrígelo "
                f"(doble clic en la celda ID) o elimina la fila.\n\nSi quieres salir "
                f"sin guardar los cambios, usa Cancelar.", parent=self)
            self._marcar(malos)
            return
        ids = [f.get("id") for f in self.filas]
        repes = sorted({i for i in ids if ids.count(i) > 1}, key=str)
        if repes:
            messagebox.showwarning(
                "Identificadores repetidos",
                f"Hay más de una fila con el ID {', '.join(map(str, repes))}.\n\n"
                f"El ID es la clave primaria de la tabla, así que tiene que ser "
                f"distinto en cada fila. Corrígelo (doble clic en la celda ID) o "
                f"elimina la fila que sobre.\n\nSi quieres salir sin guardar los "
                f"cambios, usa Cancelar.", parent=self)
            self._marcar(repes)
            return
        self.resultado = self.filas
        self.destroy()

    def _marcar(self, repes):
        """Deja seleccionadas las filas que repiten identificador, para no tener que
        buscarlas a ojo en una tabla larga."""
        culpables = [str(i) for i, f in enumerate(self.filas) if f.get("id") in repes]
        if culpables:
            self.tabla.selection_set(culpables)
            self.tabla.see(culpables[0])
            self._refrescar_muestra()


def menu_catalogos(padre, al_elegir):
    """Menu para elegir que tabla de referencia se edita.

    `al_elegir` recibe la clave del catalogo: 'lados', 'arbitros' o 'estilos'.
    """
    menu = tk.Toplevel(padre)
    menu.title("Catálogos")
    menu.transient(padre)
    menu.resizable(False, False)
    m = ttk.Frame(menu, padding=12)
    m.pack(fill=tk.BOTH, expand=True)
    ttk.Label(m, text="Tablas de referencia de la base de datos:"
              ).pack(anchor="w", pady=(0, 8))

    def abrir(cual):
        menu.destroy()
        al_elegir(cual)

    ttk.Button(m, text="Totales generales (General_Resultado)", width=38,
               command=lambda: abrir("totales")).pack(pady=2)
    ttk.Button(m, text="Lados (Partido_Lado)", width=38,
               command=lambda: abrir("lados")).pack(pady=2)
    ttk.Button(m, text="Árbitros (Arbitraje_ListaArbitros)", width=38,
               command=lambda: abrir("arbitros")).pack(pady=2)
    ttk.Button(m, text="Estilos de fuente (Arbitraje_EstiloFuente)", width=38,
               command=lambda: abrir("estilos")).pack(pady=2)
    ttk.Label(m, text="Los cuatro se vuelcan a la base de datos con el\n"
                      "botón «Exportar SQL».\n\n"
                      "Los totales generales reservan los primeros\n"
                      "identificadores de grupo: los grupos que dibujes\n"
                      "empiezan justo detrás y se corren si añades otro.\n\n"
                      "En los lados, el ID 0 es el lado común (acciones\n"
                      "que puntúan a los dos equipos).",
              foreground="#666", justify="left").pack(anchor="w", pady=(6, 0))
    ttk.Button(m, text="Cerrar", command=menu.destroy).pack(pady=(10, 0))
    menu.grab_set()