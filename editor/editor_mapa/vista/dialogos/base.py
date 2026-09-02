"""Base comun de los dialogos modales del editor."""
import tkinter as tk

from ..apariencia import ALTO_MUESTRA, ANCHO_MUESTRA


class _DialogoBase(tk.Toplevel):
    """Base para los dialogos modales: centra, captura Enter/Escape y espera."""

    def _finalizar(self, foco=None):
        self.bind("<Return>", lambda e: self._aceptar())
        self.bind("<Escape>", lambda e: self._cancelar())
        if foco is not None:
            foco.focus_set()
        self.grab_set()
        self.wait_window(self)

    @staticmethod
    def _nombre_por_id(catalogo, ident, campo, permitir_ninguno=False):
        for fila in catalogo:
            if fila["id"] == ident:
                return fila[campo]
        if permitir_ninguno:
            return "(ninguno)"
        return catalogo[0][campo] if catalogo else ""

    @staticmethod
    def _id_por_nombre(catalogo, nombre, campo, ninguno=False):
        for fila in catalogo:
            if fila[campo] == nombre:
                return fila["id"]
        return None if ninguno else (catalogo[0]["id"] if catalogo else 0)

    @staticmethod
    def _entero(var, d=0):
        """Entero de una variable de tkinter, o `d` si lo que hay no es un numero.

        Los Entry y los Spinbox admiten cualquier cosa mientras se teclea (incluso
        quedarse vacios), asi que leerlos sin red rompe la vista previa a media
        edicion."""
        try:
            return int(float(var.get()))
        except (TypeError, ValueError):
            return d

    def _lado_actual(self):
        """Lado del parcial que dibuja el elemento. El tono y la saturacion del fondo
        salen siempre de ahi (Partido_Lado), no del propio elemento."""
        return next((l for l in getattr(self, "lados", [])
                     if l["id"] == getattr(self, "lado_parcial", None)), None)

    def _marco_muestra(self):
        """Recuadro (x1, y1, x2, y2), escala `k` y tamano real con los que dibujar el
        elemento en el lienzo de vista previa.

        Se dibuja a tamano real salvo que no quepa en el hueco; en ese caso se reduce
        todo por igual, para que se siga viendo si el texto cabe o no."""
        ancho, alto = self.tam_control
        k = min(1.0, (ANCHO_MUESTRA - 12) / max(1, ancho),
                (ALTO_MUESTRA - 12) / max(1, alto))
        w, h = ancho * k, alto * k
        x1 = (ANCHO_MUESTRA - w) / 2
        y1 = (ALTO_MUESTRA - h) / 2
        return (x1, y1, x1 + w, y1 + h), k, (ancho, alto)

    @staticmethod
    def _rotulo_escala(ancho, alto, k):
        """Texto con el tamano real del elemento, avisando si la muestra va reducida."""
        return (f"{ancho:g} × {alto:g} px"
                + ("" if k == 1.0 else f"  (reducido al {k:.0%})"))

    def _cancelar(self):
        self.resultado = None
        self.destroy()
