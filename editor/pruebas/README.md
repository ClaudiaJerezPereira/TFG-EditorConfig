# Pruebas automáticas del editor

Se lanzan todas de una vez desde la carpeta `editor`:

```bash
python3 pruebas/ejecutar_todas.py
```

Cada prueba se ejecuta en su propio proceso, porque algunas sustituyen `tkinter`
y `PIL` por dobles y no deben contaminar a las demás. El resumen final dice
cuántas han pasado; cualquier fallo devuelve un código de salida distinto de 0.

Se pueden lanzar por separado, que es lo cómodo mientras se depura:

```bash
python3 pruebas/prueba_modelo.py
```

## Qué comprueba cada una

| Archivo | Qué comprueba |
|---|---|
| `prueba_estructura.py` | Que todos los módulos se importan y que el modelo y la persistencia no necesitan interfaz gráfica |
| `prueba_modelo.py` | Guías, grupos, simetría, la etiqueta del total, los catálogos y la ida y vuelta al XML |
| `prueba_sql.py` | El script SQL generado: columnas, comillas, claves ajenas y primarias |
| `prueba_seleccion.py` | El reparto de responsabilidades entre modelo, vista y controlador |
| `comprobar_nombres.py` | Que no se usa ningún nombre sin definir en todo el paquete |
| `comprobar_atributos.py` | Que el controlador solo llama a métodos y atributos que existen |

`ejemplo_mapa.py` no es una prueba: construye el mapa de ejemplo (dos grupos, un
botón por nivel, etiquetas fija y externa, y la etiqueta del total mostrada en un
grupo y oculta en el otro) que usan `prueba_sql.py` y las demás.

## Por qué se puede probar casi todo sin interfaz

El modelo y la persistencia no importan `tkinter` ni `PIL`, así que se pueden
construir mapas por código y comprobar el resultado. Lo que sí necesita interfaz
se prueba de dos maneras indirectas: `prueba_estructura.py` sustituye `tkinter` y
`PIL` por objetos falsos para al menos cargar los módulos de la vista, y
`comprobar_atributos.py` analiza el código del controlador con `ast` para detectar
llamadas a métodos que no existen, que es el error típico al renombrar algo del
modelo y olvidarse de la vista.

Lo que no se puede comprobar así (que un diálogo se vea bien, que un arrastre
responda) hay que probarlo a mano.

## El SQL no se ejecuta

No hay servidor MariaDB en el entorno de pruebas, así que `prueba_sql.py` valida
el texto generado: que cada `INSERT` tenga tantos valores por fila como columnas
declara, que los paréntesis y las comillas cierren, que ni las comas ni los
puntos y coma acaben dentro de un comentario, y que las claves ajenas apunten a
filas insertadas antes en el propio script.

Eso caza casi todo, pero **no sustituye a cargar el script de verdad**. Antes de
entregar conviene ejecutarlo contra la base de datos, cambiando en
`base_datos/crear_ACCIONES.sql` la línea del `SOURCE` por el archivo generado:

```bash
cd base_datos && ./crear_ACCIONES.sh
```

## La etiqueta del total

Es lo que más veces ha cambiado, así que tiene sus propios bloques:

- `prueba_modelo.py`, `prueba_total()`: la etiqueta es única para todo el mapa,
  cada parcial decide si la muestra (`mostrar_puntos`), el estilo y el
  desplazamiento son del grupo, y un grupo deja de contar en
  `grupos_con_total()` cuando ninguno de sus parciales la muestra.
- `prueba_modelo.py`, `prueba_total_en_el_xml()`: la etiqueta viaja en el XML
  como un elemento `<total>` propio, fuera de los grupos; cada parcial guarda
  solo `MOSTRAR_PUNTOS` y el desplazamiento se lee del grupo (`TOTAL_D`).
- `prueba_modelo.py`, `prueba_total_anclado()`: la etiqueta cuelga de cuatro
  guías de control reales, cambia de tamaño al mover cualquiera de ellas, se
  mantiene igual en todos los grupos, desaparece si se borra una de sus guías y
  sobrevive a la ida y vuelta al XML sin duplicarlas.
- `prueba_sql.py`: se genera una fila de `Arbitraje_TotalGrupoAcciones` por
  grupo que la muestre y ninguna para los demás, y `Arbitraje_ZonaAcciones`
  lleva `mostrar_puntos` y ya no lleva guías del total.

## Los catálogos

- `prueba_modelo.py`, `prueba_ids_catalogos()`: los árbitros y los estilos no
  admiten el ID `0` ni negativos, los lados sí conservan el `0` del lado común,
  y un XML antiguo con identificadores inválidos se abre pero avisa.
- `prueba_modelo.py`, `prueba_catalogos_en_el_xml()`: los cuatro catálogos viajan
  en el XML, los totales generales se renumeran `1..N` al leerlos y un `VOLCAR`
  guardado por una versión anterior se completa solo.
- `prueba_sql.py`: los totales generales ocupan los primeros
  `ID_GRUPO_ACCIONES` y los grupos del editor empiezan detrás; al definir un
  total más, todos se corren un puesto.