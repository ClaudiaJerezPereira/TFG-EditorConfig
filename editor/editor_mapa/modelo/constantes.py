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

# Identificador minimo admitido en los catalogos. El ID es la clave primaria de su
# tabla (INT UNSIGNED) y tiene que empezar en 1: ni 0 ni negativo. No obliga a que el
# primero sea el 1 ni a que vayan seguidos (un lado puede ser el 547): solo a que
# ninguno baje de ahi.
#
# Los LADOS no son una excepcion. En Partido_Lado el numero es solo la clave primaria
# de la fila: no identifica a un equipo concreto ni reserva el 0 para nada. Lo "comun"
# (las acciones cuyo valor afecta a todos los lados, para que el arbitraje refresque
# los parciales de todos y no solo el del equipo tocado) no es un lado, sino una marca
# del grupo: Arbitraje_GrupoAcciones.comun, que se activa con la casilla «Común» del
# dialogo del grupo. Por eso un partido puede tener los lados que haga falta (dos
# equipos, o cuatro robots enfrentandose a la vez) y cualquiera de ellos puede
# pertenecer a un grupo comun.
ID_MINIMO = 1


# Catalogos cuyo ID no se teclea: es la posicion en la lista, renumerada sola.
# Los TOTALES (General_Resultado) comparten numeracion con Arbitraje_GrupoAcciones y
# tienen que ocupar las primeras posiciones sin huecos, porque los grupos del editor
# empiezan justo despues. Si el ID fuera libre, un hueco o un salto dejaria un
# identificador de grupo pisado o perdido.
CATALOGOS_ID_AUTOMATICO = ("totales",)