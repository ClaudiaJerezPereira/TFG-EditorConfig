START TRANSACTION;

-- Script para insertar los datos constantes para una competición genérica.

###############################################################################
INSERT INTO Arbitraje_ListaArbitros (
        ID_ARBITRO, 
        nombre,
        descripcion) VALUES
    (1, 'IZ', 'Frontal izquierda'),
    (2, 'DR', 'Frontal derecha'),
    (3, 'FN', 'Zona fondo'),
    (4, 'TB', 'Tablas resultados');

###############################################################################
INSERT INTO Arbitraje_EstiloFuente (
        ID_ESTILO_FUENTE, 
        descripcion, 
        nombre_fuente, 
        estilo_fuente, 
        tamano_fuente, 
        color_fuente) VALUES
    (  0, ''          , '',          '',       0, '#000000'),
    (  1, 'Tribunas'  , 'Helvetica', '',      20, '#000000'),
    (  2, 'Parciales' , 'Helvetica', 'bold',  50, '#000000'),
    (  3, 'Dorsal'    , 'Helvetica', 'bold',  40, '#303030'),
    (  4, 'Equipo'    , 'Helvetica', '',      40, '#303030'),
    (  5, 'Resumen'   , 'Helvetica', 'bold',  25, '#000000'),
    (  6, 'Penaliz.'  , 'Helvetica', 'bold',  25, '#FF0000'),
    (  7, 'Previos'   , 'Helvetica', 'bold',  25, '#000000'),
    (  8, 'Total Sin' , 'Helvetica', 'bold',  35, '#000000'),
    (  9, 'TOTAL' ,     'Helvetica', 'bold', 110, '#000000');

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
        nombre) VALUES
    ( 4, 'Tribunas'    ),
    ( 5, 'Cartel'      ),
    ( 6, 'Llegada'     ),
    ( 7, 'SIMAs'       ),
    ( 8, 'Bonus'       ),
    ( 9, 'Penalización'),
    (10, 'Totales'     );

###############################################################################
###############################################################################
INSERT INTO Guia_GrupoX (
        ID_GUIA,
	    posicion) VALUES
    (  1,    20),
    (  2,  1900),
    (  3,    99),
    (  4,  1821),
    (  5,     0),
    (  6,   503),
    (  7,  1417),
    (  8,   808),
    (  9,  1112),
    ( 10,   614),
    ( 11,  1306),
    ( 12,   627),
    ( 13,  1293),
    ( 14,   823),
    ( 15,  1097),
    ( 16,   280),
    ( 17,  1640),
    ( 18,   210),
    ( 19,  1710);

###############################################################################
INSERT INTO Guia_GrupoY (
        ID_GUIA,
	    posicion) VALUES
    (  1,   720),
    (  2,   567),
    (  3,     0),
    (  4,   461),
    (  5,   659),
    (  6,   822),
    (  7,   184),
    (  8,    50),
    (  9,   250),
    ( 10,   100),
    ( 11,   150);

###############################################################################
INSERT INTO Guia_ControlX (
	    FK_GRUPO_ACCIONES,
	    ID_GUIA,
	    posicion) VALUES
	(  1,  1,     0),    
	(  1,  2,   320),   
	 
	(  2,  1,     0),    
	(  2,  2,   102),  
	
	(  3,  1,     0),    
	    
	(  4,   1,    0),
	(  4,   2,  135),
	(  4,   3, -138),
	(  4,   4,   -3),
	
	(  5,   1,    9),
	(  5,   2,   51),
	(  5,   3, -106),
	(  5,   4,  -10),
	
	(  6,   1,    0),
	(  6,   2,   54),
	(  6,   3, -127),
	(  6,   4,    3),
	
	(  7,   1,    0),
	(  7,   2,  124),
	(  7,   3, -130),
	(  7,   4,  -46),
	(  7,   5,   50),
	(  7,   6,  134),
	(  7,   7,  230),
	(  7,   8,  314),
	(  7,   9,   -6),
	
	(  8,   1,    0),
	(  8,   2,   60),
	
	(  9,   1,    0),
	(  9,   2,   60),
	
	( 10,   1,    0),
	( 10,   2,   60);
	


###############################################################################
INSERT INTO Guia_ControlY (
	    FK_GRUPO_ACCIONES,
	    ID_GUIA,
	    posicion) VALUES
	(  1,  1,     0),    
	(  1,  2,   200),    
	
	(  2,  1,     0),    
	(  2,  2,    71),    

	(  3,  1,     0),    
	
	(  4,   1,    0),
	(  4,   2,   45),
	(  4,   3,   90),
	(  4,   4,  135),

    (  5,   1,    5),
    (  5,   2,   29),
    (  5,   3,   53),
    (  5,   4,   77),
    (  5,   5,   -7),
    (  5,   6,   89),
    
	(  6,   1,    0),
	(  6,   2,   54),
	(  6,   3,  135),
	
	(  7,   1,    0),
	(  7,   2,  135),
	(  7,   3,  141),
	(  7,   4,  185),
	(  7,   5,  195),
	(  7,   6,  239),
	
	(  8,   1,    0),
	(  8,   2,   47),
	(  8,   3,  -50),
	(  8,   4,   -3),
	
	(  9,   1,    0),
	(  9,   2,  -50),
	(  9,   3,   -3),
	
	( 10,   1,    0),
	( 10,   2,   47);
	
###############################################################################
/*
INSERT INTO Arbitraje_CategoriaAcciones (
        ID_CATEGORIA, 
        FK_TIPO_ACCION, 
        publicar,
        valor_maximo, 
        img_pos, 
        directorio, 
        accion) VALUES
    ( 1, 1, TRUE,  NULL, 'w', 'tribuna',   'Tribuna nivel 1'),
    ( 2, 1, TRUE,  NULL, 'w', 'tribuna',   'Tribuna nivel 2'),
    ( 3, 1, TRUE,  NULL, 'w', 'tribuna',   'Tribuna nivel 3'),
    ( 4, 3, TRUE,     1, '',  'cartel',    'Cartel promoción'),
    ( 5, 3, TRUE,     1, '',  'llegada',   'Punto de llegada'),
    ( 6, 4, FALSE,    8, '',  'escenario', 'Superestrella en escenario'),
    ( 7, 3, TRUE,     1, '',  'pista',     'Groupie en pista'),
    ( 8, 3, TRUE,     1, '',  'todos',     'Todas las SIMAs OK'),
    ( 9, 2, FALSE, NULL, '',  '',          'Estimación de puntos'),
    (10, 2, FALSE, NULL, '',  '',          'Penalización'),
    (11, 0, TRUE,     1, '',   'estrella', 'Superestrella OK');
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
    ( 1,  4, 1,  1, TRUE,  NULL, 'w', 'tribuna',   'Tribuna nivel 1',            1,  2,  3,  4,   0),
    ( 2,  4, 1,  1, TRUE,  NULL, 'w', 'tribuna',   'Tribuna nivel 2',            1,  2,  2,  3,   0),
    ( 3,  4, 1,  1, TRUE,  NULL, 'w', 'tribuna',   'Tribuna nivel 3',            1,  2,  1,  2,   0),

    ( 1,  5, 0,  3, TRUE,     1, '',  'cartel',    'Cartel propio',              1,  2,  1,  2,   0),
    ( 2,  5, 0,  3, TRUE,     1, '',  'cartel',    'Cartel contrario',           1,  2,  3,  4,   0),

    ( 1,  6, 0,  3, TRUE,     1, '',  'llegada',   'Punto de llegada',           1,  2,  1,  2,   0),

    ( 1,  7, 0,  4, FALSE,    8, '',  'escenario', 'Superestrella en escenario', 1,  2,  1,  2,   0),
    ( 2,  7, 0,  3, TRUE,     1, '',  'pista',     'Groupies en pista',          3,  4,  3,  4,   0),
    ( 3,  7, 0,  3, TRUE,     1, '',  'pista',     'Groupies en pista',          5,  6,  3,  4,   0),
    ( 4,  7, 0,  3, TRUE,     1, '',  'pista',     'Groupies en pista',          7,  8,  3,  4,   0),
    ( 5,  7, 0,  3, TRUE,     1, '',  'todos',     'Todas las SIMAs OK',         3,  4,  5,  6,   0),
    ( 6,  7, 0,  0, TRUE,     1, '',  'estrella',  'Superestrella OK',           1,  1,  1,  1,   0),

    ( 1,  8, 7,  2, FALSE, NULL, '',  '',          'Estimación de puntos',       1,  2,  1,  2,   8),
    ( 1,  9, 6,  2, FALSE, NULL, '',  '',          'Penalización',               1,  2,  2,  3,   8);

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
        FK_ESTILO_FUENTE, 
        zona, 
        valor_defecto, 
        reflejar_x, 
        FK_OFFSET_X,
        FK_OFFSET_Y,
        FK_GUIA_X1,
        FK_GUIA_X2,
        FK_GUIA_Y1,
        FK_GUIA_Y2,
        zona_d,
        color_v) VALUES
    -- Copia tabla GeneralResultado
    ( 1,  1, 1, NULL, 9, 'TOTAL PUNTOS',                        NULL, FALSE,  1,   1,  1,  2,  1,  2,   21, 220),
    ( 1,  1, 2, NULL, 9, 'TOTAL PUNTOS',                        NULL, TRUE,   2,   1,  1,  2,  1,  2,    21, 220),
    ( 1,  2, 1, NULL, 8, 'Total sin bonus',                     NULL, FALSE,  3,   2,  1,  2,  1,  2,    12, 220),
    ( 1,  2, 2, NULL, 8, 'Total sin bonus',                     NULL, TRUE,   4,   2,  1,  2,  1,  2,    12, 220),
    ( 1,  3, 1, NULL, 2, 'Total Robot',                         NULL, FALSE,  5,   3,  1,  1,  1,  1,     0, 220),
    ( 1,  3, 2, NULL, 2, 'Total Robot',                         NULL, TRUE,   5,   3,  1,  1,  1,  1,     0, 220),
    -- Zonas de construcción
    ( 1,  4, 2,    1, 2, 'Lateral izquierda',                      0, FALSE,  6,   4,  3,  4,  1,  4,    13, 180),
    ( 1,  4, 1,    2, 2, 'Lateral derecha',                        0, TRUE,   7,   4,  3,  4,  1,  4,    13, 180),
    ( 2,  4, 2,    1, 2, 'Esquina izquierda',                      0, FALSE,  6,   5,  3,  4,  1,  4,    13, 180),
    ( 2,  4, 1,    2, 2, 'Esquina derecha',                        0, TRUE,   7,   5,  3,  4,  1,  4,    13, 180),
    ( 3,  4, 1,    1, 2, 'Centro izquierda',                       0, FALSE,  8,   5,  3,  4,  1,  4,    13, 180),
    ( 3,  4, 2,    2, 2, 'Centro cerecha',                         0, TRUE,   9,   5,  3,  4,  1,  4,    13, 180),

    -- Carteles
    ( 1,  5, 1,    1, 2, 'Carteles equipo amarillo',               0, FALSE, 10,   6,  3,  4,  5,  6,    16, 180),
    ( 1,  5, 2,    2, 2, 'Carteles equipo azul',                   0, TRUE,  11,   6,  3,  4,  5,  6,    16, 180),
    -- Zona de llegada
    ( 1,  6, 1,    3, 2, 'Zona de llegada equipo amarillo',        0, FALSE, 12,   7,  3,  4,  1,  3,    13, 160),
    ( 1,  6, 2,    3, 2, 'Zona de llegada equipo azul',            0, TRUE,  13,   7,  3,  4,  1,  3,    13, 160),
    -- SIMAs
    ( 1,  7, 1,    3, 2, 'SIMAs equipo amarillo',                  0, FALSE, 14,   7,  3,  9,  1,  2,    13, 220),
    ( 1,  7, 2,    3, 2, 'SIMAs equipo azul',                      0, TRUE,  15,   7,  3,  9,  1,  2,    13, 220),
    -- Estimación
    ( 0,  8, 1,    4, 1, 'Estimación equipo amarillo',             0, FALSE, 16,   8,  1,  1,  1,  1,     0, 220),
    ( 0,  8, 2,    4, 1, 'Estimación equipo azul',                 0, TRUE,  17,   8,  1,  1,  1,  1,     0, 220),
    -- Penalización / juego limpio
    ( 0,  9, 1,    4, 6, 'Penalización equipo amarillo',           1, FALSE, 18,   9,  1,  1,  1,  1,     0, 220),
    ( 0,  9, 2,    4, 6, 'Penalización equipo azul',               1, TRUE,  19,   9,  1,  1,  1,  1,     0, 220),
    -- Totales
    ( 1, 10, 1, NULL, 7, 'Previo equipo amarillo',                 0, FALSE, 18,   8,  1,  2,  1,  2,     8, 220),
    ( 1, 10, 2, NULL, 7, 'Previo equipo azul',                     0, TRUE,  19,   8,  1,  2,  1,  2,     8, 220),
    ( 2, 10, 1, NULL, 7, 'Delta equipo amarillo',                  0, FALSE, 16,  10,  1,  2,  1,  2,     8, 220),
    ( 2, 10, 2, NULL, 7, 'Delta equipo azul',                      0, TRUE,  17,  10,  1,  2,  1,  2,     8, 220),
    ( 3, 10, 1, NULL, 7, 'Bonus equipo amarillo',                  0, FALSE, 18,  10,  1,  2,  1,  2,     8, 220),
    ( 3, 10, 2, NULL, 7, 'Bonus equipo azul',                      0, TRUE,  19,  10,  1,  2,  1,  2,     8, 220),
    ( 4, 10, 1, NULL, 7, 'Total simas equipo amarillo',            0, FALSE, 18,  11,  1,  2,  1,  2,     8, 220),
    ( 4, 10, 2, NULL, 7, 'Total simas equipo azul',                0, TRUE,  19,  11,  1,  2,  1,  2,     8, 220);


###############################################################################
-- Etiquetas adicionales para mostrar en la aplicación de arbitraje:
INSERT INTO Arbitraje_EtiquetaFija (
        ID_ETIQUETA,
        FK_LADO,
        tipo,
        valor) VALUES
    ( 1, 1, 1, "PREVIO"),
    ( 1, 2, 1, "PREVIO"),
    ( 2, 1, 1, "ESTIM."),
    ( 2, 2, 1, "ESTIM."),
    ( 3, 1, 1, "DELTA"),
    ( 3, 2, 1, "DELTA"),
    ( 4, 1, 1, "BONUS"),
    ( 4, 2, 1, "BONUS"),
    ( 5, 1, 1, "SIMAs"),
    ( 5, 2, 1, "SIMAs"),
    ( 6, 1, 1, "PENALIZ."),
    ( 6, 2, 1, "PENALIZ."),
    ( 7, 1, 1, "T. SIN BONUS"),
    ( 7, 2, 1, "T. SIN BONUS");

-- Posición de las etiquetas, tanto las provinientes de la tabla de etiquetas
-- fijas, como las que se obtienen de las tablas de datos de partido.
INSERT INTO Arbitraje_Etiqueta (
        ID_ETIQUETA, 
        FK_LADO, 
        origen,
        FK_ESTILO_FUENTE, 
        etiqueta_x, 
        etiqueta_y, 
        etiqueta_w, 
        etiqueta_h,
        etiqueta_d,
        color_v,
        justificacion) VALUES

    ( 1,  1,  1,  3,    36,   986,    90,    73,    8,  220, 'c'),         # FK_EQUIPO
    ( 2,  1,  1,  4,   132,   986,   654,    73,    0,  220, 'c'),         # equipo
    ( 3,  1,  1,  0,   819,   949,   128,   128,    0,  220, 'c'),         # logo
    ( 1,  2,  1,  3,  1794,   986,    90,    73,    8,  220, 'c'),         # FK_EQUIPO
    ( 2,  2,  1,  4,  1134,   986,   654,    73,    0,  220, 'c'),         # equipo
    ( 3,  2,  1,  0,   974,   949,   128,   128,    0,  220, 'c'),         # logo

    ( 1,  1,  2,  5,    50,    50,   160,    47,    8,  240, 'e'),         # PREVIO
    ( 1,  2,  2,  5,  1710,    50,   160,    47,    8,  240, 'w'),         # PREVIO

    ( 2,  1,  2,  5,   340,    50,   180,    47,    8,  240, 'w'),         # ESTIMACIÓN
    ( 2,  2,  2,  5,  1400,    50,   180,    47,    8,  240, 'e'),         # ESTIMACIÓN

    ( 3,  1,  2,  5,   340,   100,   180,    47,    8,  240, 'w'),         # DELTA
    ( 3,  2,  2,  5,  1400,   100,   180,    47,    8,  240, 'e'),         # DELTA

    ( 4,  1,  2,  5,    50,   100,   160,    47,    8,  240, 'e'),         # BONUS
    ( 4,  2,  2,  5,  1710,   100,   160,    47,    8,  240, 'w'),         # BONUS

    ( 5,  1,  2,  5,    50,   150,   160,    47,    8,  240, 'e'),         # SIMAs
    ( 5,  2,  2,  5,  1710,   150,   160,    47,    8,  240, 'w'),         # SIMAs

    ( 6,  1,  2,  6,    50,   200,   160,    47,    8,  240, 'e'),         # PENALIZ
    ( 6,  2,  2,  6,  1710,   200,   160,    47,    8,  240, 'w'),         # PENALIZ

    ( 7,  1,  2,  5,    20,   500,   260,    67,    8,  240, 'c'),        # TOTAL SIN B.
    ( 7,  2,  2,  5,  1640,   500,   260,    67,    8,  240, 'c');        # TOTAL SIN B.

###############################################################################
# Vistas adicionales.
###############################################################################
/*
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


