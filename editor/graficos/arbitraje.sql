START TRANSACTION;

-- Datos de esta edición, generados por el editor de mapas.
-- Se ejecuta después de eurobot_ACCIONES.sql (estructura) y de
-- eurobot_DATOS.sql (datos comunes a todas las ediciones).
--
-- Los cuatro catálogos se vuelcan aquí. General_Resultado y Partido_Lado van con
-- ON DUPLICATE KEY UPDATE porque la tabla puede venir ya creada y con datos
-- (la trae la base de datos de partidos, o eurobot_DATOS.sql en la
-- construcción autónoma): así se añaden los lados que falten y se actualizan
-- el nombre y el color de los que ya estén, que es lo que cambia cada año.

###############################################################################
INSERT INTO General_Resultado (
        ID_RESULTADO,
        nombre) VALUES
    (  1, 'TOTAL PUNTOS'),
    (  2, 'Total robot')
    ON DUPLICATE KEY UPDATE
        nombre = VALUES(nombre);

###############################################################################
INSERT INTO Partido_Lado (
        ID_LADO,
        nombre,
        color_h,
        color_s) VALUES
    (  1, 'Amarillo'  , 0.122, 0.919),
    (  2, 'Azul'      , 0.559, 0.519)
    ON DUPLICATE KEY UPDATE
        nombre  = VALUES(nombre),
        color_h = VALUES(color_h),
        color_s = VALUES(color_s);

###############################################################################
INSERT INTO Arbitraje_ListaArbitros (
        ID_ARBITRO,
        nombre,
        descripcion) VALUES
    (1, 'Juan', 'equipo amarillo'),
    (2, 'Carol', 'equipo azul');

###############################################################################
INSERT INTO Arbitraje_EstiloFuente (
        ID_ESTILO_FUENTE,
        descripcion,
        nombre_fuente,
        estilo_fuente,
        tamano_fuente,
        color_fuente) VALUES
    (  1, 'Normal'      , 'Arial'           , 'bold'  ,   20, '#000000'),
    (  2, 'Fina'        , 'Ink Free'        , 'underline',   27, '#f5010a');

###############################################################################
-- Los primeros grupos son los totales generales (General_Resultado):
-- reservan los identificadores 1..2 y los grupos
-- del editor empiezan justo después.
INSERT INTO Arbitraje_GrupoAcciones (
        ID_GRUPO_ACCIONES,
        nombre) VALUES
    (  1, 'TOTAL PUNTOS'),
    (  2, 'Total robot' );

-- Y después, los grupos definidos con el editor.
INSERT INTO Arbitraje_GrupoAcciones (
        ID_GRUPO_ACCIONES,
        nombre,
        comun) VALUES
    (  3, 'Nido'    , FALSE),
    (  4, 'Despensa', FALSE);


###############################################################################
INSERT INTO Guia_GrupoX (
        ID_GUIA,
        posicion) VALUES
    (  1,   462),
    (  2,   500),
    (  3,   501),
    (  4,   726),
    (  5,  1194),
    (  6,  1419),
    (  7,  1420),
    (  8,  1458);

###############################################################################
INSERT INTO Guia_GrupoY (
        ID_GUIA,
        posicion) VALUES
    (  1,   207),
    (  2,   574);

###############################################################################
INSERT INTO Guia_ControlX (
        FK_GRUPO_ACCIONES,
        ID_GUIA,
        posicion) VALUES
    (  3,   1,   -81),
    (  3,   2,     0),
    (  3,   3,   117),

    (  4,   1,   -81),
    (  4,   2,     0),
    (  4,   3,   111);

###############################################################################
INSERT INTO Guia_ControlY (
        FK_GRUPO_ACCIONES,
        ID_GUIA,
        posicion) VALUES
    (  3,   1,     0),
    (  3,   2,    77),
    (  3,   3,   148),

    (  4,   1,   -97),
    (  4,   2,     0),
    (  4,   3,    77),
    (  4,   4,   178);

###############################################################################
-- Etiqueta con el total de puntos (Arbitraje_TotalGrupoAcciones): una
-- fila por grupo, con las guías que la enmarcan dentro de ese grupo. Los
-- grupos que no aparecen aquí no muestran el total en ninguna zona.
INSERT INTO Arbitraje_TotalGrupoAcciones (
        FK_GRUPO_ACCIONES,
        FK_ESTILO_FUENTE,
        FK_GUIA_X1,
        FK_GUIA_X2,
        FK_GUIA_Y1,
        FK_GUIA_Y2,
        zona_d) VALUES
    (  3,  1,   1,   2,   1,   2,   0),    # Nido
    (  4,  1,   1,   2,   2,   3,   0);    # Despensa

###############################################################################
INSERT INTO Arbitraje_TipoAcciones (
        ID_TIPO_ACCIONES,
        FK_GRUPO_ACCIONES,
        FK_ESTILO_FUENTE,
        FK_TIPO_ACCION,
        publicar,
        valor_maximo,
        img_pos,
        directorio,
        accion,
        FK_GUIA_X1,
        FK_GUIA_X2,
        FK_GUIA_Y1,
        FK_GUIA_Y2,
        tipo_d) VALUES
    (  1,   3,  1,  4, TRUE , NULL, ''  , 'Robot1.png', 'Gráfico robot.'               ,   2,   3,   1,   2,   0),

    (  1,   4,  1,  1, TRUE ,  100, ''  , ''          , 'Botón click de las despensas.',   2,   3,   1,   2,   0);

###############################################################################
-- mostrar_puntos dice si ESTA zona dibuja la etiqueta del total; dónde y
-- con qué letra lo hace es del grupo (Arbitraje_TotalGrupoAcciones).
INSERT INTO Arbitraje_ZonaAcciones (
        ID_ZONA_ACCIONES,
        FK_GRUPO_ACCIONES,
        FK_LADO,
        FK_ARBITRO,
        zona,
        valor_defecto,
        reflejar_x,
        FK_OFFSET_X,
        FK_OFFSET_Y,
        mostrar_puntos,
        color_v) VALUES
    (  1,   3,  1,    1, 'Nido 1'             ,    0, FALSE,   1,   1, TRUE ,  255),
    (  1,   3,  2,    2, 'Nido 1 (espejo)'    ,    0, TRUE ,   8,   1, TRUE ,  255),

    (  1,   4,  1,    1, 'Despensa 1'         ,    0, FALSE,   3,   2, TRUE ,  255),
    (  2,   4,  1,    1, 'Despensa 2'         ,    0, TRUE ,   4,   2, TRUE ,  255),
    (  1,   4,  2,    2, 'Despensa 1 (espejo)',    0, TRUE ,   6,   2, TRUE ,  255),
    (  2,   4,  2,    2, 'Despensa 2 (espejo)',    0, FALSE,   5,   2, TRUE ,  255);

###############################################################################
-- Etiquetas (Arbitraje_Etiqueta): texto o imagen que se dibuja en cada
-- colocacion del grupo. Con externa = FALSE, 'valor' es el contenido; con
-- externa = TRUE es el identificador del dato en
-- VistaPartido_EtiquetasPartido, que da un valor por lado.
INSERT INTO Arbitraje_Etiqueta (
        ID_ETIQUETA,
        FK_GRUPO_ACCIONES,
        FK_ESTILO_FUENTE,
        FK_GUIA_X1,
        FK_GUIA_X2,
        FK_GUIA_Y1,
        FK_GUIA_Y2,
        externa,
        tipo,
        valor,
        etiqueta_d,
        color_v,
        justificacion) VALUES
    (  1,   4,  1,   1,   2,   1,   2, FALSE,  1, 'Partido',   0,  255, 'c');    # Despensa2

COMMIT;
