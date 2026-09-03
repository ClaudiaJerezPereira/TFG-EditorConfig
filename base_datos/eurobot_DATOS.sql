START TRANSACTION;

-- Cuando creamos la base de datos de acciones sin crear la de partidos,
-- necesitamos incluir algunos datos para que funcione correctamente. En este
-- script se añaden dichos datos. Si construyeramos la base de datos completa
-- no sería necesario añadir estos datos, ya que vendrían añadidos en la
-- base de datos de partidos.


###############################################################################
###############################################################################
--
-- Los TOTALES generales (General_Resultado) ya no se crean aquí: los define el
-- catálogo «Totales generales» del editor de mapas y los vuelca el script de la
-- edición, que se ejecuta después. Así el número de totales y los identificadores
-- que reservan en Arbitraje_GrupoAcciones salen siempre del mismo sitio.
--

--
-- Los lados, con el mínimo imprescindible para que las claves ajenas de este
-- script (Arbitraje_AuxEtiquetasPartido.FK_LADO) tengan a qué apuntar: los dos
-- equipos del partido simulado.
--
-- ID_LADO es sólo la clave primaria de la fila y empieza en 1, como en las demás
-- tablas: no hay ningún lado con significado propio. Las acciones cuyo valor
-- afecta a todos los lados (las que puntúan a ambos equipos) no se marcan con un
-- lado, sino con Arbitraje_GrupoAcciones.comun, que es lo que la aplicación de
-- arbitraje consulta para saber si tiene que refrescar los parciales de todos los
-- lados o sólo el del equipo tocado. Por eso un partido puede tener los lados que
-- haga falta, y no forzosamente dos.
--
-- Los nombres y los colores definitivos los pone el script de la edición que
-- genera el editor de mapas, que se ejecuta después y vuelca Partido_Lado con
-- INSERT ... ON DUPLICATE KEY UPDATE (por eso estas filas no estorban).
--
INSERT INTO Partido_Lado (
        ID_LADO, 
        nombre,
        color_h,
        color_s) VALUES
    (1, 'Amarillo', 0.122, 0.919),
    (2, 'Azul'    , 0.559, 0.519);

--
-- NOTA: Estos datos serían una simulación de lo que obtendríamos de la
-- vista de etiquetas del partido. En este caso, estamos simulando el
-- partido con ID = 1, cuyos equipos son "Minerva Genius" y "Blueberries"
-- con dorsales 112 y 137.
--
INSERT INTO Arbitraje_AuxEtiquetasPartido(
        ID_PARTIDO,
        ID_ETIQUETA,
        FK_LADO,
        tipo,
        valor) VALUES
    ( 1, "DORSAL", 1, 1, 112),
    ( 1, "DORSAL", 2, 1, 137),
    ( 1, "NOMBRE", 1, 1, "Minerva Genius"),
    ( 1, "NOMBRE", 2, 1, "Blueberries"),
    ( 1, "LOGO",   1, 2, "logo1.png"),
    ( 1, "LOGO",   2, 2, "logo2.png"),
    ( 2, "DORSAL", 1, 1, 145),
    ( 2, "DORSAL", 2, 1, 123),
    ( 2, "NOMBRE", 1, 1, "Sanifest"),
    ( 2, "NOMBRE", 2, 1, "Redwire"),
    ( 2, "LOGO",   1, 2, "logo3.png"),
    ( 2, "LOGO",   2, 2, "logo4.png");

COMMIT;