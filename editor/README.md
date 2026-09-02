# Editor de mapas de arbitraje

Herramienta para dibujar sobre la imagen del campo de juego los botones,
etiquetas y totales que después usa la aplicación de arbitraje, y generar con
ello la configuración que se vuelca en la base de datos.

## Cómo se ejecuta

```bash
python3 EditorMapa.py
```

Requiere Python 3.12, `tkinter` y `Pillow` (`pip install pillow`).

Las pruebas automáticas se lanzan con:

```bash
python3 pruebas/ejecutar_todas.py
```

El editor lee y escribe la versión 3 del XML, que es la que hay en `graficos/`.
Los archivos guardados con versiones anteriores (etiqueta del total definida
parcial a parcial con `ZONA_X/Y/W/H`, etiquetas con `CONTENIDO`/`TEXTO`/`CAMPO`,
grupos con `FAMILIA`) ya no se convierten al abrirlos.

## Organización del código (Modelo - Vista - Controlador)

```
EditorMapa.py              punto de entrada: solo arranca la aplicación
editor_mapa/
    modelo/                los datos del mapa y sus reglas
        constantes.py      conceptos de la base de datos (tipos de acción...)
        catalogos.py       totales generales, lados, árbitros y estilos
        geometria.py       cálculos en píxeles del mapa
        mapa.py            ModeloMapa: estado del documento y operaciones
    persistencia/          llevar el modelo a un archivo y traerlo de vuelta
        xml_io.py          formato de trabajo del editor (VERSION 3)
        sql_io.py          volcado de los catálogos
        sql_mapa.py        volcado del mapa completo a la base de datos
    vista/                 todo lo que se ve, y lo único que sabe de tkinter
        apariencia.py      colores, textos y tamaños
        fuentes.py         medidas de texto
        imagenes.py        carga y cacheo de iconos
        lienzo.py          dibujo del mapa
        ventana.py         barra de herramientas, lienzo y barra de estado
        dialogos/          un diálogo por tabla de la base de datos
    controlador/
        principal.py       traduce las acciones del usuario en cambios del modelo
graficos/                  la imagen del campo de juego y los ejemplos
                           (arbitraje.xml y su SQL generado)
pruebas/                   comprobaciones automáticas (ver pruebas/README.md)
```

**El modelo y la persistencia no importan `tkinter` ni `PIL`.** Se pueden usar y
probar sin interfaz gráfica, que es lo que permite comprobar la lógica del editor
de forma automática. El modelo trabaja siempre en píxeles del mapa; la escala del
zoom es cosa de la vista.

Reparto de responsabilidades:

- El **modelo** no sabe que existe una pantalla: ni dibuja, ni pregunta, ni avisa.
  Guarda las guías, los grupos, los controles y las colocaciones, y aplica las
  reglas del dominio (la simetría, la etiqueta del total, los identificadores).
- La **vista** solo lee del modelo. Dibuja, mide texto y recoge lo que el usuario
  teclea en los diálogos, pero no decide nada.
- El **controlador** es el único que conoce a los dos. Guarda lo puramente
  transitorio (el modo de trabajo, el arrastre en curso, el rectángulo que se está
  trazando), que ni se dibuja ni se guarda en el XML.

La **selección** está en el modelo (`modelo.seleccion`), junto con el grupo y la
colocación activos: la vista necesita conocerla para resaltar, y así no depende del
controlador. El flujo de un clic es siempre el mismo:

| Acción | Controlador | Modelo | Vista |
|---|---|---|---|
| Clic en un elemento | decide cuál es | `seleccionar()` | `refrescar_seleccion()` |
| Clic en vacío | ve que no hay nada | `limpiar_seleccion()` | `refrescar_seleccion()` |
| Arrastre | guarda el desfase | no se toca | `repintar_vectores()` |
| Soltar | aplica el cambio | mueve la guía | `redibujar()` |

`refrescar_seleccion()` repinta solo el color y el grosor de lo resaltado, sin
reescalar la imagen del campo, que es lo caro.

## Correspondencia con la base de datos

| Elemento del editor | Tabla |
|---|---|
| Guía de colocación | `Guia_GrupoX` / `Guia_GrupoY` |
| Guía de control | `Guia_ControlX` / `Guia_ControlY` |
| Grupo | `Arbitraje_GrupoAcciones` |
| Botón | `Arbitraje_TipoAcciones` |
| Etiqueta | `Arbitraje_Etiqueta` |
| Parcial (colocación) | `Arbitraje_ZonaAcciones` |
| Etiqueta del total | `Arbitraje_TotalGrupoAcciones` |
| Catálogos | `General_Resultado`, `Partido_Lado`, `Arbitraje_ListaArbitros`, `Arbitraje_EstiloFuente` |

## Los catálogos

Cuatro tablas de referencia se editan desde el botón «Catálogos» y se vuelcan con
el resto del script:

| Catálogo | Tabla | ID |
|---|---|---|
| Totales generales | `General_Resultado` | automático, `1..N` sin huecos |
| Lados | `Partido_Lado` | desde `0` |
| Árbitros | `Arbitraje_ListaArbitros` | desde `1` |
| Estilos de fuente | `Arbitraje_EstiloFuente` | desde `1` |

El ID es la clave primaria de su tabla (`INT UNSIGNED`), así que no admite ni el
`0` ni los negativos. La única excepción son los **lados**: en `Partido_Lado` el
número significa algo por sí mismo (`0` es el lado común, el de las acciones que
puntúan a los dos equipos, y `1` y `2` son los dos equipos del partido), y ese
convenio lo dan por hecho `Arbitraje_AuxEtiquetasPartido` y la aplicación de
arbitraje. El mínimo de cada catálogo está en `ID_MINIMO`, en
`modelo/constantes.py`.

En los **totales generales** el ID ni siquiera se teclea: es la posición en la
lista, y se renumera solo al añadir, borrar o reordenar filas (botones «Subir» y
«Bajar»). Tiene que ir seguido y sin huecos porque comparte numeración con
`Arbitraje_GrupoAcciones`, y un hueco dejaría un identificador de grupo pisado.

`General_Resultado` y `Partido_Lado` se vuelcan con `INSERT ... ON DUPLICATE KEY
UPDATE`, no con un `INSERT` a secas: las dos se declaran `CREATE TABLE IF NOT
EXISTS` porque en el sistema completo vienen de la base de datos de partidos, así
que pueden llegar ya con filas.

## Volcado a la base de datos

El botón «Exportar SQL» genera el script de datos de la edición, el equivalente a
los `eurobot_ACCIONES_<año>.sql` escritos a mano. Se ejecuta después de
`eurobot_ACCIONES.sql` (estructura) y `eurobot_DATOS.sql` (datos comunes).

Los identificadores se asignan de forma determinista: las guías de colocación se
numeran por posición; las de control, por su distancia al origen dentro de cada
grupo; los botones y las etiquetas, dentro de su grupo. Los grupos no empiezan en
el 1: los primeros identificadores los reservan los totales generales
(`General_Resultado`), que se definen en su propio catálogo, así que con **N**
totales el primer grupo es el **N+1**. Añadir un total corre todos los grupos un
puesto.

Un detalle que no se deduce del XML y queda documentado en `sql_mapa.py`: una
pareja de parciales simétricos comparte `ID_ZONA_ACCIONES` y se distingue por
`FK_LADO`.

Antes de escribir el archivo se comprueba lo que la base de datos rechazaría
(estilos o lados que no están en el catálogo, grupos sin colocar, textos que no
caben en su columna) y se avisa de ello.

## Etiquetas

Una etiqueta se sitúa con guías de control del grupo, igual que un botón, y se
guarda como **una sola fila** de `Arbitraje_Etiqueta` aunque su grupo esté
colocado varias veces: la vista `Arbitraje_VistaAuxEtiquetas` la reparte por
todas las colocaciones, aplicando el desplazamiento y el reflejo de cada una y
tomando el color de fondo del lado de esa colocación. Por eso la etiqueta no
tiene lado propio; de ella sale solo la intensidad (`color_v`).

Su contenido son tres campos de esa tabla:

- `externa`: si es `FALSE`, el valor está en la propia tabla (etiqueta fija, por
  ejemplo `TOTAL PUNTOS`). Si es `TRUE`, el valor es el identificador de un dato
  del partido en `VistaPartido_EtiquetasPartido` (`DORSAL`, `NOMBRE`, `LOGO`),
  que da un valor por lado: la misma etiqueta muestra el dato del equipo de cada
  parcial.
- `tipo`: 1 texto, 2 imagen, 3 imagen web.
- `valor`: el texto, el nombre de la imagen o ese identificador. De las imágenes
  se guarda solo el nombre (la columna admite 50 caracteres): el directorio lo
  pone la configuración de la aplicación de arbitraje, y el editor las busca
  junto a la imagen del mapa para poder dibujarlas.

La justificación usa las mismas letras que `img_pos`, `"w"` y `"e"`, porque la
vista las intercambia cuando el parcial está reflejado.

## Imágenes: solo el nombre del archivo

Ni las etiquetas de imagen (`Arbitraje_Etiqueta.valor`) ni los iconos de los
botones (`Arbitraje_TipoAcciones.directorio`) guardan una ruta: **solo el nombre
del archivo**. El directorio raíz lo pone el XML de configuración de la
aplicación de arbitraje, así que una ruta escrita aquí no la encontraría ningún
otro ordenador, y en el caso de las etiquetas ni siquiera cabría (la columna
admite 50 caracteres).

Por eso el «Examinar...» de los dos diálogos abre `graficos/` y rechaza las
imágenes de otras carpetas: hay que copiarlas ahí primero. Al leer un XML que
traiga una ruta se conserva solo el nombre, y al exportar el SQL se avisa si
alguna se ha colado.

## La etiqueta del total

Un grupo puede contener botones y etiquetas mezclados. La etiqueta del total no
es un elemento más: en el editor es **única para todo el mapa**. Cuelga de cuatro
guías de control, una pareja vertical y otra horizontal, y esas cuatro guías
existen en **todos** los grupos a la misma distancia del origen: al arrastrar una
en cualquier grupo, las de los demás la siguen, de modo que la etiqueta se
redimensiona a la vez en todo el mapa y no se puede descuadrar grupo a grupo.

En la base de datos ese dato se reparte en dos sitios:

- `Arbitraje_TotalGrupoAcciones` guarda **una fila por grupo** (relación 1 a 1
  con `Arbitraje_GrupoAcciones`) con las guías que enmarcan la etiqueta
  (`FK_GUIA_X1..Y2`), el tipo de letra (`FK_ESTILO_FUENTE`) y el desplazamiento
  vertical del texto (`zona_d`). Si un grupo **no tiene fila**, no muestra el
  total en ninguna de sus zonas; por eso el editor solo escribe los grupos en los
  que algún parcial la muestra (`ModeloMapa.grupos_con_total`).
- `Arbitraje_ZonaAcciones.mostrar_puntos` dice si **esa zona concreta** la
  dibuja. La vista `Arbitraje_VistaAuxParciales` exige las dos cosas, así que un
  parcial marcado cuyo grupo no tenga fila tampoco la muestra.

Ese reparto se nota en la interfaz: el tipo de letra y el desplazamiento se
editan con doble clic **sobre la propia etiqueta**, y cambian en todas las
colocaciones del grupo al que pertenece la copia que se ha pinchado; la casilla
«Mostrar la etiqueta del total en este parcial», en cambio, está en el diálogo
del parcial y solo afecta a esa colocación.

El nombre de la etiqueta no llega a la base de datos (`TotalGrupoAcciones` no
tiene columna de nombre y el texto que dibuja el arbitraje es siempre el total de
puntos): sirve solo para reconocerla en el editor.

Como la geometría vive en las guías, borrar una de las cuatro deja la etiqueta
sin definir y por eso la elimina de todo el mapa; el editor avisa antes. Al
exportar, `ModeloMapa.preparar_total` solo repone las que le falten a algún grupo
creado después de dibujarla.