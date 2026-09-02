START TRANSACTION;

-- Script para insertar los datos constantes para una competición genérica.


    
###############################################################################


###############################################################################

###############################################################################





INSERT INTO Arbitraje_ListaArbitros (
        ID_ARBITRO, 
        nombre,
        descripcion) VALUES
    (1, 'IZP', 'Izquierda Propio'),
    (2, 'IZR', 'Izquierda Resto'),
    (3, 'DRP', 'Derecha Propio'),
    (4, 'DRR', 'Derecha Resto'),
    (5, 'GR',  'Granero');

###############################################################################
INSERT INTO Arbitraje_EstiloFuente (
        ID_ESTILO_FUENTE, 
        descripcion, 
        nombre_fuente, 
        estilo_fuente, 
        tamano_fuente, 
        color_fuente) VALUES
    (  0, ''         , 'Liberation Sans', ''    ,   0, '#000000'),
    # El 0 se reserva para acciones que no muestran números (gráficos)
    (  1, 'Cajas'     , 'Liberation Sans', '',      15, '#000000'),
    (  2, 'Penalizac' , 'Liberation Sans', 'bold',  20, '#FF0000'),
    (  3, 'Parciales' , 'Liberation Sans', 'bold',  40, '#000000'),
    (  4, 'TOTAL'     , 'Liberation Sans', 'bold', 110, '#000000'),
    (  5, 'Dorsal'    , 'Liberation Sans', 'bold',  40, '#303030'),
    (  6, 'Equipo'    , 'Liberation Sans', '',      40, '#303030'),
    (  7, 'Etiquetas' , 'Liberation Sans', '',      20, '#303030');


###############################################################################
###############################################################################
###############################################################################
-- Insertamos primero los registros correspondientes a los resultados del
-- equipo que están guardados en la tabla GeneralResultado.
INSERT INTO Arbitraje_GrupoAcciones (
        ID_GRUPO_ACCIONES, 
        nombre)
    SELECT ID_RESULTADO, nombre
      FROM General_Resultado;
-- Y después insertamos el resto de grupos de acciones.     
INSERT INTO Arbitraje_GrupoAcciones (
        ID_GRUPO_ACCIONES, 
        nombre,
        comun) VALUES
    (  4, 'Cajas despensa', TRUE),
    (  5, 'Termómetro'    , FALSE),
    (  6, 'Nido'          , FALSE),
    (  7, 'Despensa'      , FALSE),
    (  8, 'Comer'         , FALSE),
    (  9, 'Granero'       , TRUE),
    ( 10, 'Penalización'  , FALSE),
    ( 11, 'Totales'       , FALSE);

###############################################################################
###############################################################################
INSERT INTO Guia_GrupoX (
        ID_GUIA,
        posicion) VALUES
    (  1,   40),
    (  2, 1880),
    (  3,  210),
    (  4, 1710),
    (  5,  861),
    (  6,  831),
    (  7,  891),
    (  8, 1059),
    (  9, 1029),
    ( 10, 1089),
    ( 11,  520),
    ( 12,  490),
    ( 13,  550),
    ( 14,  742),
    ( 15,  712),
    ( 16,  772),
    ( 17,  960),
    ( 18,  930),
    ( 19,  990),
    ( 20, 1178),
    ( 21, 1148),
    ( 22, 1208),
    ( 23, 1400),
    ( 24, 1370),
    ( 25, 1430),
    ( 26,  960),
    ( 27,  930),
    ( 28,  990),
    ( 29,  710),
    ( 30,  680),
    ( 31,  740),
    ( 32, 1210),
    ( 33, 1180),
    ( 34, 1240),
    ( 35,  710),
    ( 36, 1210),
    ( 37,  500),
    ( 38, 1420),
    ( 39,  814),
    ( 40,  908),
    ( 41, 1012),
    ( 42, 1106),
    ( 43,  473),
    ( 44,  567),
    ( 45,  695),
    ( 46,  789),
    ( 47,  913),
    ( 48, 1007),
    ( 49, 1131),
    ( 50, 1225),
    ( 51, 1353),
    ( 52, 1447),
    ( 53,  663),
    ( 54,  757),
    ( 55,  913),
    ( 56, 1007),
    ( 57, 1163),
    ( 58, 1257),
    ( 59,  630),
    ( 60, 1290),
    ( 61,  960),
    ( 62,  210),
    ( 63, 1710);

INSERT INTO Guia_GrupoY (
        ID_GUIA,
        posicion) VALUES
    (  1,  720),
    (  2,  400),
    (  3,  280),
    (  4,  429), -- valor original, 494),
    (  5,  648), -- valor original, 713),
    (  6,  780),
    (  7,  160),
    (  8,  281),
    (  9,  430), -- valor original, 495),
    ( 10,  649), -- valor original, 714),
    ( 11,  310),
    ( 12,  115),
    ( 13,  500),
    ( 14,  450);

INSERT INTO Guia_ControlX (
        FK_GRUPO_ACCIONES,
        ID_GUIA,
        posicion) VALUES

    (  1,   1,    0),
    (  1,   2,  300),

    (  2,   1,    0),
    (  2,   2,   60),
        
    (  4,   1,  -15),
    (  4,   2,   15),
    (  4,   3,    0),
    (  4,   4,   65),

    (  5,   1, -110),
    (  5,   2,  110),
    (  5,   3, -200),
    (  5,   4, -120),

    (  6,   1,    0),
    (  6,   2,   60),
    (  6,   3,   64),
    (  6,   4,   94),
    (  6,   5,    1),
    (  6,   6,   81),

    (  7,   1,  -50),
    (  7,   2,    0),

    (  8,   1,    0),
    (  8,   2,   80),

    (  9,   1, -143),
    (  9,   2, -103),
    (  9,   3,  -66),
    (  9,   4,  -26),
    (  9,   5,   26),
    (  9,   6,   66),
    (  9,   7,  103),
    (  9,   8,  143),
    (  9,   9,  -40),
    (  9,  10,   40),

    ( 10,   1,    0),
    ( 10,   2,   60),
    
    ( 11,   1,    0),
    ( 11,   2,   60);

INSERT INTO Guia_ControlY (
        FK_GRUPO_ACCIONES,
        ID_GUIA,
        posicion) VALUES
    (  1,   1,    0),
    (  1,   2,  200),

    (  2,   1,    0),
    (  2,   2,   47),

    (  4,   1,    1),
    (  4,   2,   31),
    (  4,   3,    0),
    (  4,   4,   60),
    (  4,   5,  120),
    (  4,   6,  -64),
    (  4,   7,   -4),

    (  5,   1,    0),
    (  5,   2,   50),
    (  5,   3,   60),
    (  5,   4,  -64),

    (  6,   1,   64),
    (  6,   2,  124),
    (  6,   3,   94),
    (  6,   4,    0),
    (  6,   5,   60),

    (  7,   1,    2),
    (  7,   2,   52),
    (  7,   3,    0),

    (  8,   1,    0),
    (  8,   2,   80),

    (  9,   1,   84),
    (  9,   2,  114),
    (  9,   3,   69),
    (  9,   4,   99),
    (  9,   5,  144),
    (  9,   6,  129),
    (  9,   7,    0),
    (  9,   8,   60),

    ( 10,   1,    0),
    ( 10,   2,   47),
    
    ( 11,   1,    0),
    ( 11,   2,   47);
###############################################################################
INSERT INTO Arbitraje_TotalGrupoAcciones (
        FK_GRUPO_ACCIONES,
        FK_ESTILO_FUENTE,
        FK_GUIA_X1,
        FK_GUIA_X2,
        FK_GUIA_Y1,
        FK_GUIA_Y2,
        zona_d) VALUES
    ( 1, 4,     1,  2,  1,  2,    0),
    ( 2, 7,     1,  2,  1,  2,    0),
    ( 4, 3,     1,  4,  4,  5,    0),
    ( 5, 3,     3,  4,  1,  3,    0),
    ( 6, 3,     5,  6,  4,  5,    0),
    ( 9, 3,     9, 10,  7,  8,    0),
    (11, 7,     1,  2,  1,  2,    0);
/*
INSERT INTO Arbitraje_CategoriaAcciones (
        ID_CATEGORIA, 
        FK_TIPO_ACCION, 
        publicar,
        valor_maximo, 
        img_pos, 
        directorio, 
        accion) VALUES
    ( 1, 1, TRUE,  NULL, 's', 'cajas'       , 'Cajas en despensa'   ),
    ( 2, 4, TRUE,    10, 'e', 'termometro'  , 'Cursor termómetro'   ),
    ( 3, 4, TRUE,     2, 'e', 'final'       , 'Mamá ardilla en nido'),
    ( 4, 1, TRUE,     6, 's', 'cajas'       , 'Cajas en nido'       ),
    ( 5, 3, TRUE,     1, 'e', 'despensa'    , 'Ardilla en despensa' ),
    ( 6, 3, TRUE,     1, 'e', 'comer'       , 'Ardillas comiendo'   ),
    ( 7, 3, TRUE,     1, 'e', 'refrigerador', 'Refrigeradores vacío'),
    ( 8, 3, TRUE,     1, 'e', 'caja_vacia'  , 'Caja vacia en refrig'),
    ( 9, 2, TRUE,  NULL, 'e', ''            , 'Penalizaciones'      );
*/
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
    (  1,  4, 1,  1,  TRUE, NULL, 's', 'cajas'        , 'Cajas en despensa'    ,  1,  2,  1,  2,  0),
    (  1,  5, 0,  4,  TRUE,   10, 'e', 'termometro'   , 'Cursor termómetro'    ,  1,  2,  1,  2,  0),
    (  1,  6, 0,  4,  TRUE,    2, 'e', 'final'        , 'Mamá ardilla en nido' ,  1,  2,  1,  2,  0),
    (  2,  6, 1,  1,  TRUE,    6, 's', 'cajas'        , 'Cajas en nido'        ,  3,  4,  1,  3,  0),

    (  1,  7, 0,  3,  TRUE,    1, 'e', 'despensa'     , 'Ardillas en despensa' ,  1,  2,  1,  2,  0),
    (  2,  8, 0,  3,  TRUE,    1, 'e', 'comer'        , 'Ardillas comiendo'    ,  1,  2,  1,  2,  0),

    (  1,  9, 0,  3,  TRUE,    1, 'e', 'refrigerador' , 'Refrigerador 1 vacío' ,  1,  2,  1,  2,  0),
    (  2,  9, 0,  3,  TRUE,    1, 'e', 'refrigerador' , 'Refrigerador 2 vacío' ,  3,  4,  3,  4,  0),
    (  3,  9, 0,  3,  TRUE,    1, 'e', 'refrigerador' , 'Refrigerador 3 vacío' ,  5,  6,  3,  4,  0),
    (  4,  9, 0,  3,  TRUE,    1, 'e', 'refrigerador' , 'Refrigerador 4 vacío' ,  7,  8,  1,  2,  0),
    (  5,  9, 0,  3,  TRUE,    1, 'e', 'caja_vacia'   , 'Caja vacía en refr 1' ,  1,  2,  2,  5,  0),
    (  6,  9, 0,  3,  TRUE,    1, 'e', 'caja_vacia'   , 'Caja vacía en refr 2' ,  3,  4,  4,  6,  0),
    (  7,  9, 0,  3,  TRUE,    1, 'e', 'caja_vacia'   , 'Caja vacía en refr 3' ,  5,  6,  4,  6,  0),
    (  8,  9, 0,  3,  TRUE,    1, 'e', 'caja_vacia'   , 'Caja vacía en refr 4' ,  7,  8,  2,  5,  0),

    (  1, 10, 2,  2,  TRUE, NULL, 'e', ''             , 'Penalizaciones'       ,  1,  2,  1,  2,  0);

###############################################################################
-- Insertamos primero los registros correspondientes a los resultados de los
-- equipos guardados en la tabla GeneralResultado, uno por cada uno de los lados
-- guardados en la tabla GeneralLado.
-- Y a continuacion, definimos el resto de zonas.
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

    -- Copia tabla GeneralResultado
    (  1,  1, 1, NULL, 'TOTAL PUNTOS',                        NULL, FALSE,  1,   1,   TRUE,  240),
    (  1,  1, 2, NULL, 'TOTAL PUNTOS',                        NULL, TRUE,   2,   1,   TRUE,  240),
    (  1,  2, 1, NULL, 'ROBOT IZQUIERDO',                        0, FALSE,  3,   2,   TRUE,  200),
    (  1,  2, 2, NULL, 'ROBOT DERECHO',                          0, TRUE,   4,   2,   TRUE,  200),

--    (  1,  2, 1, NULL, 1, 'Total Robot',                       NULL, FALSE,  0,   0,     0,     0,   100,    47,     0, 240),
--    (  1,  2, 2, NULL, 1, 'Total Robot',                       NULL, TRUE,   0,   0,     0,     0,   100,    47,     0, 240),
--  (  1,  3, 1, NULL, 1, 'Total no común',                      NULL, FALSE,  0,   0,     0,     0,     0,     0,     0,   0),
--  (  1,  3, 2, NULL, 1, 'Total no común',                      NULL, TRUE,   0,   0,     0,     0,     0,     0,     0,   0),
    -- Cajas en despensas
    (  1,  4, 0,    2, 'Despensa 1 común',                       0, FALSE,  5,   3,   FALSE, 200),
    (  1,  4, 1,    1, 'Despensa 1 izquierda',                   0, TRUE,   6,   3,   TRUE,  200),
    (  1,  4, 2,    2, 'Despensa 1 derecha',                     0, FALSE,  7,   3,   TRUE,  200),

    (  2,  4, 0,    4, 'Despensa 2 común',                       0, FALSE,  8,   3,   FALSE, 200),
    (  2,  4, 1,    4, 'Despensa 2 izquierda',                   0, TRUE,   9,   3,   TRUE,  200),
    (  2,  4, 2,    3, 'Despensa 2 derecha',                     0, FALSE, 10,   3,   TRUE,  200),

    (  3,  4, 0,    2, 'Despensa 3 común',                       0, FALSE, 11,   4,   FALSE, 200),
    (  3,  4, 1,    1, 'Despensa 3 izquierda',                   0, TRUE,  12,   4,   TRUE,  200),
    (  3,  4, 2,    2, 'Despensa 3 derecha',                     0, FALSE, 13,   4,   TRUE,  200),

    (  4,  4, 0,    2, 'Despensa 4 común',                       0, FALSE, 14,   4,   FALSE, 200),
    (  4,  4, 1,    1, 'Despensa 4 izquierda',                   0, TRUE,  15,   4,   TRUE,  200),
    (  4,  4, 2,    2, 'Despensa 4 derecha',                     0, FALSE, 16,   4,   TRUE,  200),

    (  5,  4, 0,    2, 'Despensa 5 común',                       0, FALSE, 17,   4,   FALSE, 200),
    (  5,  4, 1,    1, 'Despensa 5 izquierda',                   0, TRUE,  18,   4,   TRUE,  200),
    (  5,  4, 2,    2, 'Despensa 5 derecha',                     0, FALSE, 19,   4,   TRUE,  200),

    (  6,  4, 0,    4, 'Despensa 6 común',                       0, FALSE, 20,   4,   FALSE, 200),
    (  6,  4, 1,    4, 'Despensa 6 izquierda',                   0, TRUE,  21,   4,   TRUE,  200),
    (  6,  4, 2,    3, 'Despensa 6 derecha',                     0, FALSE, 22,   4,   TRUE,  200),

    (  7,  4, 0,    4, 'Despensa 7 común',                       0, FALSE, 23,   4,   FALSE, 200),
    (  7,  4, 1,    4, 'Despensa 7 izquierda',                   0, TRUE,  24,   4,   TRUE,  200),
    (  7,  4, 2,    3, 'Despensa 7 derecha',                     0, FALSE, 25,   4,   TRUE,  200),

    (  8,  4, 0,    2, 'Despensa 8 común',                       0, FALSE, 26,   5,   FALSE, 200),
    (  8,  4, 1,    1, 'Despensa 8 izquierda',                   0, TRUE,  27,   5,   TRUE,  200),
    (  8,  4, 2,    2, 'Despensa 8 derecha',                     0, FALSE, 28,   5,   TRUE,  200),

    (  9,  4, 0,    2, 'Despensa 9 común',                       0, FALSE, 29,   5,   FALSE, 200),
    (  9,  4, 1,    1, 'Despensa 9 izquierda',                   0, TRUE,  30,   5,   TRUE,  200),
    (  9,  4, 2,    2, 'Despensa 9 derecha',                     0, FALSE, 31,   5,   TRUE,  200),

    ( 10,  4, 0,    4, 'Despensa 10 común',                      0, FALSE, 32,   5,   FALSE, 200),
    ( 10,  4, 1,    4, 'Despensa 10 izquierda',                  0, TRUE,  33,   5,   TRUE,  200),
    ( 10,  4, 2,    3, 'Despensa 10 derecha',                    0, FALSE, 34,   5,   TRUE,  200),
    -- Termómetro
    (  1,  5, 1,    1, 'Termómetro izquierdo',                   0, FALSE, 35,   6,   TRUE,  150),
    (  1,  5, 2,    3, 'Termómetro derecho' ,                    0, TRUE,  36,   6,   TRUE,  150),

    -- Finalización
    (  1,  6, 1,    1, 'Nido equipo izquierdo',                  0, FALSE, 37,   7,   TRUE,  180),
    (  1,  6, 2,    3, 'Nido equipo derecho',                    0, TRUE,  38,   7,   TRUE,  180),
    -- Ardilla en despensa
    (  1,  7, 1,    1, 'Ardilla en despensa 1',                  0, FALSE, 39,   8,   FALSE, 240),
    (  1,  7, 2,    1, 'Ardilla en despensa 1',                  0, TRUE,  40,   8,   FALSE, 240),

    (  2,  7, 1,    3, 'Ardilla en despensa 2',                  0, FALSE, 41,   8,   FALSE, 240),
    (  2,  7, 2,    3, 'Ardilla en despensa 2',                  0, TRUE,  42,   8,   FALSE, 240),

    (  3,  7, 1,    1, 'Ardilla en despensa 3',                  0, FALSE, 43,   9,   FALSE, 240),
    (  3,  7, 2,    1, 'Ardilla en despensa 3',                  0, TRUE,  44,   9,   FALSE, 240),

    (  4,  7, 1,    1, 'Ardilla en despensa 4',                  0, FALSE, 45,   9,   FALSE, 240),
    (  4,  7, 2,    1, 'Ardilla en despensa 4',                  0, TRUE,  46,   9,   FALSE, 240),

    (  5,  7, 1,    1, 'Ardilla en despensa 5',                  0, FALSE, 47,   9,   FALSE, 240),
    (  5,  7, 2,    1, 'Ardilla en despensa 5',                  0, TRUE,  48,   9,   FALSE, 240),

    (  6,  7, 1,    3, 'Ardilla en despensa 6',                  0, FALSE, 49,   9,   FALSE, 240),
    (  6,  7, 2,    3, 'Ardilla en despensa 6',                  0, TRUE,  50,   9,   FALSE, 240),

    (  7,  7, 1,    3, 'Ardilla en despensa 7',                  0, FALSE, 51,   9,   FALSE, 240),
    (  7,  7, 2,    3, 'Ardilla en despensa 7',                  0, TRUE,  52,   9,   FALSE, 240),

    (  8,  7, 1,    1, 'Ardilla en despensa 8',                  0, FALSE, 53,  10,   FALSE, 240),
    (  8,  7, 2,    1, 'Ardilla en despensa 8',                  0, TRUE,  54,  10,   FALSE, 240),

    (  9,  7, 1,    1, 'Ardilla en despensa 9',                  0, FALSE, 55,  10,   FALSE, 240),
    (  9,  7, 2,    1, 'Ardilla en despensa 9',                  0, TRUE,  56,  10,   FALSE, 240),

    ( 10,  7, 1,    3, 'Ardilla en despensa 10',                 0, FALSE, 57,  10,   FALSE, 240),
    ( 10,  7, 2,    3, 'Ardilla en despensa 10',                 0, TRUE,  58,  10,   FALSE, 240),
    -- Ardillas comiendo
    (  1,  8, 1,    1, 'Ardillas comiendo',                      0, FALSE, 59,  11,   FALSE, 255),
    (  1,  8, 2,    3, 'Ardillas comiendo',                      0, TRUE,  60,  11,   FALSE, 255),

--    -- SIMAs
--    (  1,  7, 1,    1, 2, 'SIMAs equipo izquierdo',                 0, FALSE,     0,     0,     0,     0,     0,     0,     0,   0),
--    (  1,  7, 2,    1, 2, 'SIMAs equipo derecho',                   0, FALSE,     0,     0,     0,     0,     0,     0,     0,   0),

    -- Granero (puntos para ambos equipos)
    (  1,  9, 0,    5, 'Granero',                                0, FALSE, 61,  12,   TRUE,  200),
    -- Penalización
    (  0, 10, 1,    1, 'Penalización equipo izquierdo',          0, FALSE, 62,  13,   FALSE, 200),
    (  0, 10, 2,    3, 'Penalización equipo derecho',            0, TRUE,  63,  13,   FALSE, 200),
    -- Totales
    (  1, 11, 1, NULL, 'SIMAS IZQUIERDO',                        0, FALSE, 62,  14,   TRUE,  200),
    (  1, 11, 2, NULL, 'SIMAS DERECHO',                          0, TRUE,  63,  14,   TRUE,  200);

###############################################################################

-- Aunque estos registros pueden ser añadidos en los INSERT anteriores, los pongo
-- aquí en este caso para que quede más claro la diferencia entre registros de
-- acciones y de etiquetas.
INSERT INTO Arbitraje_GrupoAcciones (
        ID_GRUPO_ACCIONES, 
        nombre,
        comun) VALUES
    ( 20, 'Etiquetas parciales', FALSE),
    ( 21, 'Datos equipo',        FALSE);

INSERT INTO Guia_GrupoX (
        ID_GUIA,
        posicion) VALUES
    ( 64,   44),
    ( 65, 1876),
    ( 66,   36),
    ( 67, 1884);

INSERT INTO Guia_GrupoY (
        ID_GUIA,
        posicion) VALUES
    ( 15,  400),
    ( 16,  949);

INSERT INTO Guia_ControlX (
        FK_GRUPO_ACCIONES,
        ID_GUIA,
        posicion) VALUES
    ( 20,   1,    0),
    ( 20,   2,  166),
    ( 21,   1,    0),
    ( 21,   2,   96),
    ( 21,   3,  750),
    ( 21,   4,  783),
    ( 21,   5,  911);

INSERT INTO Guia_ControlY (
        FK_GRUPO_ACCIONES,
        ID_GUIA,
        posicion) VALUES
    ( 20,   1,    0),
    ( 20,   2,   47),
    ( 20,   3,   50),
    ( 20,   4,   97),
    ( 20,   5,  100),
    ( 20,   6,  147),
    ( 21,   1,    0),
    ( 21,   2,   37),
    ( 21,   3,  110),
    ( 21,   4,  128);
    
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

    -- Zonas exclusivas para etiquetas.
    (  1, 20, 1, NULL, 'Parcial amarillo', NULL, FALSE, 64,  15,  FALSE, 240),
    (  2, 20, 2, NULL, 'Parcial azul',     NULL, TRUE,  65,  15,  FALSE, 240),
    (  1, 21, 1, NULL, 'Equipo amarillo',  NULL, FALSE, 66,  16,  FALSE, 240),
    (  2, 21, 2, NULL, 'Equipo azul',      NULL, TRUE,  67,  16,  FALSE, 240);


-- Posición de las etiquetas, tanto las provinientes de la tabla de etiquetas
-- fijas, como las que se obtienen de las tablas de datos de partido.
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

    ( 1, 20,  7,    1, 2, 1, 2, FALSE, 1, "ROBOT ",        0,  240, 'e'),         # ROBOT
    ( 2, 20,  7,    1, 2, 3, 4, FALSE, 1, "SIMAS ",        0,  240, 'e'),         # SIMAS
    ( 3, 20,  7,    1, 2, 5, 6, FALSE, 1, "Penalización ", 0,  240, 'e'),         # PENALIZ.

    ( 1, 21,  5,    1, 2, 2, 3, TRUE,  1, "DORSAL",        0,  170, 'c'),         # FK_EQUIPO
    ( 2, 21,  6,    2, 3, 2, 3, TRUE,  1, "NOMBRE",        0,  220, 'c'),         # equipo
    ( 3, 21,  0,    4, 5, 1, 4, TRUE,  2, "LOGO",          0,  220, 'c');         # logo

/*
###############################################################################
# Vistas adicionales.
###############################################################################

-- Vistas para obtener la página de próximo partido. Dicha página necesita:
-- Dorsal de los equipos que se enfrentan en el próximo partido.
-- Nombre
-- Logo.
-- Estimación estática indicada por los equipos. En la edición de 2024, la
--   estimación se encuentra en la Zona 0 del grupo 8, tipo 1.

-- Vista para filtrar, de todas las acciones definidas en la base de datos,
-- la correspondiente a la estimación de puntuación dada por los equipos.
CREATE ALGORITHM=UNDEFINED SQL SECURITY INVOKER 
       VIEW VistaEstimacion AS 
    SELECT *
      FROM Arbitraje_Accion
     WHERE FK_ZONA_ACCIONES = 0
       AND FK_TIPO_ACCIONES = 1
       AND FK_GRUPO_ACCIONES = 8;

-- Vista que complementa la vista Resultado2Equipos, añadiendo el valor de
-- la estimación de puntuación dada por los equipos.
-- NOTA: Esta vista se declara aquí, y no en el archivo de vistas, ya que
-- esta vista no es genérica, sino que depende de cada edición (al menos los
-- ID asignados a la acción de estimación de puntuación.)
CREATE ALGORITHM=UNDEFINED SQL SECURITY INVOKER 
       VIEW VistaEstimacionPuntos AS 
    SELECT Resultado2Equipos.*,
           VistaEstimacion1.valor AS estimacion1,
           VistaEstimacion2.valor AS estimacion2
      FROM Resultado2Equipos
           LEFT JOIN VistaEstimacion AS VistaEstimacion1
                   ON Resultado2Equipos.ID_PARTIDO = VistaEstimacion1.FK_PARTIDO
                  AND VistaEstimacion1.FK_LADO = 1
           LEFT JOIN VistaEstimacion AS VistaEstimacion2
                   ON Resultado2Equipos.ID_PARTIDO = VistaEstimacion2.FK_PARTIDO
                  AND VistaEstimacion2.FK_LADO = 2;
*/
COMMIT;
