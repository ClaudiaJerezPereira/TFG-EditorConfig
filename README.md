# TFG — Configuración de la aplicación de arbitraje de Eurobot

Este repositorio contiene las dos piezas con las que se define la interfaz de
recuento de puntos de una edición de Eurobot: la **base de datos** que describe
esos controles y el **editor gráfico** con el que se dibujan sobre la imagen del
campo de juego.

La idea es que cada año no haya que reescribir a mano el script SQL de la
competición: se abre la imagen del campo en el editor, se colocan encima los
botones y las etiquetas, y el editor genera el script equivalente.

## Qué hay en cada carpeta

| Carpeta | Contenido |
|---|---|
| `editor/` | El editor de mapas: código, pruebas y ejemplos. **Ver [`editor/README.md`](editor/README.md)** |
| `base_datos/` | Los scripts SQL: estructura, datos comunes y los de cada edición |
| `documentacion/` | Diagramas y capturas del diseño |

## La base de datos

Se llama `eurobot_ACCIONES` y se monta con tres scripts que se ejecutan siempre
en este orden:

| Script | Qué aporta |
|---|---|
| `eurobot_ACCIONES.sql` | La estructura: tablas, claves y vistas. Es la misma todos los años |
| `eurobot_DATOS.sql` | Los datos comunes que normalmente vendrían de la base de datos de partidos: los dos lados mínimos para sus claves ajenas y unos partidos simulados. Los nombres y colores definitivos de los lados, y los totales generales, los pone el script de la edición |
| `eurobot_ACCIONES_<año>.sql` | Los datos de **una edición** concreta: sus grupos, guías, botones, etiquetas y parciales |

Los encadena `crear_ACCIONES.sql`, que borra la base de datos y la vuelve a crear
desde cero. Como script de edición carga `arbitraje.sql`, que es el que produce el
editor con «Exportar SQL»:

```bash
cd base_datos && ./crear_ACCIONES.sh     # Linux
crear_ACCIONES.bat                       # Windows
```

Los dos lanzadores usan el usuario `admin/admin`; cámbialo dentro si el tuyo es
otro. **`SOURCE` usa rutas relativas, así que hay que ejecutarlos desde
`base_datos/`.**

Para cargar otra edición, se cambia la última línea de `crear_ACCIONES.sql`:

```sql
SOURCE ./eurobot_ACCIONES_2026.sql
```

Están incluidos los scripts escritos a mano de las ediciones **2025** y **2026**,
que son la referencia de la que salió el formato del volcado. Ojo: el de 2026
marca los parciales comunes con `FK_LADO = 0`, un convenio que ya no existe, así
que hay que revisarlo antes de cargarlo.

## El editor

Se ejecuta desde `editor/`:

```bash
cd editor && python3 EditorMapa.py
```

Requiere Python 3.12, `tkinter` y `Pillow` (`pip install pillow`).

El editor trabaja sobre un archivo XML propio y, con «Exportar SQL», produce el
`eurobot_ACCIONES_<año>.sql` de esa edición. Toda la explicación —la organización
del código, la correspondencia entre lo que se dibuja y las tablas, y cómo se
generan los identificadores— está en **[`editor/README.md`](editor/README.md)**,
y las pruebas automáticas en
[`editor/pruebas/README.md`](editor/pruebas/README.md).

## Cómo se relacionan las dos piezas

```
   imagen del campo
          │
          ▼
   editor  ──►  arbitraje.xml            (formato de trabajo, se guarda y se reabre)
          │
          └──►  eurobot_ACCIONES_<año>.sql
                          │
                          ▼
   eurobot_ACCIONES.sql + eurobot_DATOS.sql + ese script
                          │
                          ▼
                  base de datos eurobot_ACCIONES
                          │
                          ▼
              aplicación de arbitraje (fuera de este repositorio)
```

El XML es la referencia con la que se sigue trabajando; el SQL se regenera a
partir de él cada vez que haga falta. Los ejemplos de `editor/graficos/` sí se
versionan, para poder comparar de un vistazo qué cambia en el script cuando se
toca el editor.