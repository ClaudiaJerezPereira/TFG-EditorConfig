"""Constantes del dominio.

Aqui solo hay conceptos de la base de datos de arbitraje (tipos de accion,
posiciones de icono, justificaciones...). Nada relacionado con la interfaz:
los colores, las fuentes y los textos de ayuda estan en el paquete `vista`.

Las clases de elemento que puede contener un grupo son "boton"
(Arbitraje_TipoAcciones), "etiqueta" (Arbitraje_Etiqueta) y "total" (la etiqueta
con la suma de puntos de la zona, Arbitraje_ZonaAcciones).
"""

# Texto que se dibuja dentro de la etiqueta del total. Su valor real lo calcula
# la aplicacion de arbitraje sumando los puntos de la zona.
TEXTO_TOTAL = "TOTAL"

# Tipos de control de Arbitraje_TipoAccion:
#   nulo  : no muestra nada
#   click : el valor se incrementa al pulsar; muestra el numero
#   texto : el valor se teclea (para numeros altos)
#   bool  : marcar si o no
#   graf  : muestra un dibujo distinto segun el valor
TIPOS_ACCION = ["nulo", "click", "texto", "bool", "graf"]

# Justificacion del texto de una etiqueta (Arbitraje_Etiqueta.justificacion).
# Los valores son los mismos que usa img_pos: "w" (izquierda) y "e" (derecha).
# La vista Arbitraje_VistaAuxEtiquetas los intercambia cuando el parcial esta
# reflejado, asi que tienen que ser esas letras y no "l"/"r".
JUSTIFICACIONES = {"w": "izquierda", "c": "centro", "e": "derecha"}

# Arbitraje_Etiqueta.tipo: que se hace con el campo "valor".
TIPOS_ETIQUETA = {1: "texto", 2: "imagen", 3: "imagen web"}

# Identificadores de VistaPartido_EtiquetasPartido que puede mostrar una etiqueta
# externa (externa = TRUE). El valor de la etiqueta es uno de estos, y la vista lo
# resuelve para cada lado del partido. Son sugerencias: la lista real depende de la
# base de datos de partidos, asi que el usuario puede escribir otro.
CAMPOS_PARTIDO = ["DORSAL", "NOMBRE", "LOGO"]

# VistaPartido_EtiquetasPartido.ID_ETIQUETA es VARCHAR(10): el identificador de una
# etiqueta externa no puede ser mas largo.
MAX_ID_PARTIDO = 10

# Holgura (px) para considerar que dos guias verticales ya son simetricas entre si.
TOL_SIMETRIA = 3.0

# Los catalogos del editor, en el orden en que se vuelcan.
NOMBRES_CATALOGOS = ("totales", "lados", "arbitros", "estilos")

# Catalogos que se vuelcan a la base de datos al exportar el SQL: todos.
# Los LADOS tambien: aunque Partido_Lado pueda venir ya creada (por la base de datos
# de partidos o por eurobot_DATOS.sql), sus nombres y sus colores son de la edicion,
# asi que los pone el editor. Por eso su volcado es un INSERT ... ON DUPLICATE KEY
# UPDATE: anade los lados que falten y actualiza los que ya esten, en vez de abortar
# por clave repetida (ver sql_io.insert_lados). Lo mismo vale para los TOTALES
# (General_Resultado), que tambien pueden venir de la base de datos de partidos.
CATALOGOS_VOLCADOS = NOMBRES_CATALOGOS

# Identificador minimo admitido en cada catalogo. El ID es la clave primaria de su
# tabla (INT UNSIGNED) y tiene que empezar en 1: ni 0 ni negativo. No obliga a que el
# primero sea el 1, solo a que ninguno baje de ahi.
#
# Los LADOS son la excepcion, y por eso el minimo va por catalogo y no en una sola
# constante. No es que la tabla los cree otro script (desde que se vuelcan, los crea
# este editor), sino que en Partido_Lado el 0 es un valor con significado propio:
# FK_LADO = 0 marca los parciales "comunes", los de las acciones que puntuan a los dos
# equipos, y 1 y 2 son los dos equipos del partido. Ese convenio esta grabado en la
# aplicacion de arbitraje (las vistas filtran por FK_LADO = 1 y FK_LADO = 2) y en
# Arbitraje_AuxEtiquetasPartido, asi que renumerar los lados romperia el partido.
ID_MINIMO_CATALOGO = 1
ID_MINIMO = {
    "totales": ID_MINIMO_CATALOGO,
    "lados": 0,
    "arbitros": ID_MINIMO_CATALOGO,
    "estilos": ID_MINIMO_CATALOGO,
}


# Catalogos cuyo ID no se teclea: es la posicion en la lista, renumerada sola.
# Los TOTALES (General_Resultado) comparten numeracion con Arbitraje_GrupoAcciones y
# tienen que ocupar las primeras posiciones sin huecos, porque los grupos del editor
# empiezan justo despues. Si el ID fuera libre, un hueco o un salto dejaria un
# identificador de grupo pisado o perdido.
CATALOGOS_ID_AUTOMATICO = ("totales",)