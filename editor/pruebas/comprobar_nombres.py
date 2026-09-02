"""Detecta nombres usados y no definidos en cada modulo.

Aproximacion estatica: recoge todo lo que el modulo define (imports, funciones,
clases, asignaciones y parametros, en cualquier ambito) y lo resta de los nombres
que lee. No sustituye a ejecutar el programa, pero basta para cazar los imports
que se olvidan al partir un archivo en varios.
"""
import ast
import builtins
import sys
from pathlib import Path

IGNORAR = set(dir(builtins)) | {"__file__", "__name__", "__doc__", "self", "cls"}


def definidos(arbol):
    nombres = set()
    for n in ast.walk(arbol):
        if isinstance(n, ast.Import):
            for a in n.names:
                nombres.add((a.asname or a.name).split(".")[0])
        elif isinstance(n, ast.ImportFrom):
            for a in n.names:
                nombres.add(a.asname or a.name)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            nombres.add(n.name)
            args = getattr(n, "args", None)
            if args:
                for a in (list(args.args) + list(args.posonlyargs) +
                          list(args.kwonlyargs)):
                    nombres.add(a.arg)
                for a in (args.vararg, args.kwarg):
                    if a:
                        nombres.add(a.arg)
        elif isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            nombres.add(n.id)
        elif isinstance(n, ast.ExceptHandler) and n.name:
            nombres.add(n.name)
        elif isinstance(n, (ast.Lambda,)):
            for a in list(n.args.args) + list(n.args.kwonlyargs):
                nombres.add(a.arg)
            for a in (n.args.vararg, n.args.kwarg):
                if a:
                    nombres.add(a.arg)
        elif isinstance(n, ast.comprehension):
            for x in ast.walk(n.target):
                if isinstance(x, ast.Name):
                    nombres.add(x.id)
        elif isinstance(n, ast.Global):
            nombres.update(n.names)
    return nombres


def revisar(ruta):
    arbol = ast.parse(ruta.read_text(encoding="utf-8"), filename=str(ruta))
    conocidos = definidos(arbol) | IGNORAR
    faltan = {}
    for n in ast.walk(arbol):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
            if n.id not in conocidos:
                faltan.setdefault(n.id, n.lineno)
    return faltan


def main(raiz):
    total = 0
    for ruta in sorted(Path(raiz).rglob("*.py")):
        faltan = revisar(ruta)
        if faltan:
            total += len(faltan)
            print(f"{ruta}:")
            for nombre, linea in sorted(faltan.items(), key=lambda x: x[1]):
                print(f"    línea {linea}: {nombre}")
    print("Sin nombres sueltos." if not total else f"{total} nombre(s) sin definir.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
