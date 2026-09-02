"""Piezas comunes del volcado a SQL.

El formato de los INSERT es el mismo que el de los eurobot_ACCIONES_<anio>.sql
escritos a mano. Aqui estan los catalogos y los ayudantes que comparte todo el
volcado; el script completo de una edicion lo arma sql_mapa. Modulo sin interfaz.
"""

SEPARADOR = "#" * 79


def texto_sql(valor):
    """Literal de cadena para MySQL: las comillas simples se duplican."""
    limpio = str(valor if valor is not None else "")
    return "'" + limpio.replace("\\", "\\\\").replace("'", "''") + "'"


def insert_totales(totales):
    """General_Resultado: los totales generales del partido.

    Comparten numeracion con Arbitraje_GrupoAcciones y ocupan 1..N; los grupos del
    editor empiezan en N+1. Como Partido_Lado, la tabla puede venir ya creada y con
    datos (la trae la base de datos de partidos), asi que se vuelca con
    INSERT ... ON DUPLICATE KEY UPDATE en vez de abortar por clave repetida.
    """
    if not totales:
        return []
    lineas = [SEPARADOR,
              "INSERT INTO General_Resultado (",
              "        ID_RESULTADO,",
              "        nombre) VALUES"]
    filas = [f'    ({int(t["id"]):3d}, {texto_sql(t.get("nombre", ""))})'
             for t in sorted(totales, key=lambda t: t["id"])]
    lineas.append(",\n".join(filas))
    lineas += ["    ON DUPLICATE KEY UPDATE",
               "        nombre = VALUES(nombre);"]
    return lineas


def insert_lados(lados):
    """Partido_Lado: los lados del partido, con el tono y la saturacion de su color.

    La tabla puede existir y estar llena antes de este script: en la base de datos
    completa la trae la de partidos, y en la construccion autonoma la rellena
    eurobot_DATOS.sql, que se ejecuta antes. Por eso el volcado no es un INSERT a
    secas, que abortaria por clave repetida, sino un INSERT ... ON DUPLICATE KEY
    UPDATE: anade los lados que falten y actualiza el nombre y el color de los que ya
    esten, que es justo lo que cambia de una edicion a otra.
    """
    if not lados:
        return []
    lineas = [SEPARADOR,
              "INSERT INTO Partido_Lado (",
              "        ID_LADO,",
              "        nombre,",
              "        color_h,",
              "        color_s) VALUES"]
    filas = [f'    ({int(l["id"]):3d}, {texto_sql(l.get("nombre", "")):<12}, '
             f'{float(l.get("color_h", 0)):5.3f}, {float(l.get("color_s", 0)):5.3f})'
             for l in sorted(lados, key=lambda l: l["id"])]
    lineas.append(",\n".join(filas))
    lineas += ["    ON DUPLICATE KEY UPDATE",
               "        nombre  = VALUES(nombre),",
               "        color_h = VALUES(color_h),",
               "        color_s = VALUES(color_s);"]
    return lineas


def insert_arbitros(arbitros):
    """Arbitraje_ListaArbitros: los arbitros entre los que se reparten los parciales."""
    if not arbitros:
        return []
    lineas = [SEPARADOR,
              "INSERT INTO Arbitraje_ListaArbitros (",
              "        ID_ARBITRO,",
              "        nombre,",
              "        descripcion) VALUES"]
    filas = [f'    ({int(a["id"])}, {texto_sql(a.get("nombre", ""))}, '
             f'{texto_sql(a.get("descripcion", ""))})'
             for a in sorted(arbitros, key=lambda a: a["id"])]
    lineas.append(",\n".join(filas) + ";")
    return lineas


def insert_estilos(estilos):
    """Arbitraje_EstiloFuente: tipo de letra de cada control. El tamano 0 se reserva
    para los controles que no muestran texto (graficos)."""
    if not estilos:
        return []
    lineas = [SEPARADOR,
              "INSERT INTO Arbitraje_EstiloFuente (",
              "        ID_ESTILO_FUENTE,",
              "        descripcion,",
              "        nombre_fuente,",
              "        estilo_fuente,",
              "        tamano_fuente,",
              "        color_fuente) VALUES"]
    filas = [f'    ({int(e["id"]):3d}, {texto_sql(e.get("descripcion", "")):<14}, '
             f'{texto_sql(e.get("nombre_fuente", "")):<18}, '
             f'{texto_sql(e.get("estilo_fuente", "")):<8}, '
             f'{int(e.get("tamano_fuente", 0)):4d}, '
             f'{texto_sql(e.get("color_fuente", "#000000"))})'
             for e in sorted(estilos, key=lambda e: e["id"])]
    lineas.append(",\n".join(filas) + ";")
    return lineas