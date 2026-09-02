START TRANSACTION;

-- Datos de esta edición, generados por el editor de mapas.
-- Se ejecuta después de eurobot_ACCIONES.sql (estructura) y de
-- eurobot_DATOS.sql (datos comunes a todas las ediciones).
--
-- Los LADOS (Partido_Lado) no se vuelcan aquí: los crea eurobot_DATOS.sql,
-- porque son los mismos todos los años. El editor los guarda en el XML solo
-- para conocer sus colores al dibujar.

###############################################################################
INSERT INTO Arbitraje_ListaArbitros (
        ID_ARBITRO,
        nombre,
        descripcion) VALUES
    (0, 'Pepe', 'Arbitro amarillo'),
    (1, 'Juan', 'Arbitro azul'),
    (2, 'Carol', 'Arbitro verde');

###############################################################################
INSERT INTO Arbitraje_EstiloFuente (
        ID_ESTILO_FUENTE,
        descripcion,
        nombre_fuente,
        estilo_fuente,
        tamano_fuente,
        color_fuente) VALUES
    (  0, 'Normal'      , 'Arial'           , 'bold'  ,   20, '#000000'),
    (  1, 'Negrita'     , 'Elephant'        , 'bolditalic',   25, '#870c78'),
    (  2, 'Azul'        , 'Terminal'        , 'underline',   23, '#00ffff');

###############################################################################
-- Los grupos 1..3 son los totales generales, y se copian de
-- General_Resultado para que existan sus identificadores.
INSERT INTO Arbitraje_GrupoAcciones (
        ID_GRUPO_ACCIONES,
        nombre)
    SELECT ID_RESULTADO, nombre
      FROM General_Resultado;

-- Y después, los grupos definidos con el editor.
INSERT INTO Arbitraje_GrupoAcciones (
        ID_GRUPO_ACCIONES,
        nombre,
        comun) VALUES
    (  4, 'Despensa', FALSE),
    (  5, 'Nido'    , TRUE );


###############################################################################
INSERT INTO Guia_GrupoX (
        ID_GUIA,
        posicion) VALUES
    (  1,   500),
    (  2,  1415);

###############################################################################
INSERT INTO Guia_GrupoY (
        ID_GUIA,
        posicion) VALUES
    (  1,   206),
    (  2,   607);

###############################################################################
INSERT INTO Guia_ControlX (
        FK_GRUPO_ACCIONES,
        ID_GUIA,
        posicion) VALUES
    (  4,   1,  -128),
    (  4,   2,     0),
    (  4,   3,   172),

    (  5,   1,  -142),
    (  5,   2,  -128),
    (  5,   3,     0),
    (  5,   4,   158);

###############################################################################
INSERT INTO Guia_ControlY (
        FK_GRUPO_ACCIONES,
        ID_GUIA,
        posicion) VALUES
    (  4,   1,   -79),
    (  4,   2,     0),
    (  4,   3,   150),

    (  5,   1,  -125),
    (  5,   2,   -79),
    (  5,   3,     0),
    (  5,   4,   152);

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
    (  4,  2,   1,   2,   1,   2, -13),    # Despensa
    (  5,  0,   2,   3,   2,   3,   0);    # Nido

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
    (  1,   4,  1,  1, TRUE ,  128, ''  , ''          , 'botón de click',   2,   3,   2,   3,  20),
    (  2,   4,  0,  3, TRUE , NULL, 'n' , 'Robot1.png', 'botón de bool' ,   1,   2,   2,   3,  11),

    (  1,   5,  1,  2, TRUE ,   34, ''  , ''          , 'botón texto'   ,   3,   4,   3,   4, -12);

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
    (  1,   4,  2,    2, 'Despensa 1',   12, FALSE,   1,   1, TRUE ,  212),
    (  2,   4,  1,    0, 'Despensa 2',   45, TRUE ,   2,   2, TRUE ,  124),

    (  1,   5,  2,    1, 'Nido 1'    ,    0, FALSE,   2,   1, FALSE,  255),
    (  2,   5,  0, NULL, 'Nido 2'    ,    0, FALSE,   1,   2, TRUE ,  255);

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
    (  1,   4,  0,   2,   3,   1,   2, FALSE,  2, 'Robot2.png',   0,  255, 'c'),    # EtiquetaImagen

    (  1,   5,  1,   3,   4,   1,   3, TRUE ,  1, 'DORSAL'    , -14,   75, 'c'),    # EtiquetaExterna
    (  2,   5,  0,   1,   3,   3,   4, FALSE,  1, 'equipos'   ,  20,  221, 'e');    # EtiquetaTexto

COMMIT;
