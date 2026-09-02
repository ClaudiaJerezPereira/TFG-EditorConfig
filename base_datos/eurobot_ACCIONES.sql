START TRANSACTION;
--
-- Script con la estructura de la base de datos para el diseño de los controles
-- de la aplicación de recuento de puntos.
-- 
-- Guías de estilo. Obtenido de:
-- https://www.sqlstyle.guide/
-- https://videlcloud.wordpress.com/2017/03/05/buenas-practicas-para-el-diseno-
--   de-base-de-datos/

###############################################################################
###############################################################################
# Declaración de funciones.
###############################################################################
###############################################################################

###############################################################################
###############################################################################
# Fin definición de funciones.
###############################################################################
###############################################################################


###############################################################################
###############################################################################
###############################################################################
--
-- Si queremos crear solo las tablas de configuración de la aplicación de
-- arbitraje, sin tablas de equipos, partidos, etc, es necesario al menos esta
-- tabla, ya que los controles de la aplicación sí dependen del lado. Por eso,
-- añadimos esta tabla en el caso de que no haya sido añadida ya (porque estemos
-- creando la base de datos completa).
--
CREATE TABLE IF NOT EXISTS Partido_Lado (
    ID_LADO INT UNSIGNED PRIMARY KEY NOT NULL,
    nombre VARCHAR(9) NOT NULL,
    color_h FLOAT NOT NULL DEFAULT 0,
    color_s FLOAT NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf16 COLLATE=utf16_spanish_ci;

###############################################################################
--
-- Similar para la tabla de resultados.
--
CREATE TABLE IF NOT EXISTS General_Resultado (
    ID_RESULTADO INT UNSIGNED PRIMARY KEY NOT NULL,
    nombre VARCHAR(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf16 COLLATE=utf16_spanish_ci;


###############################################################################
###############################################################################
# Tablas de acciones y parciales
###############################################################################
###############################################################################
--
-- Esta tabla premite crear grupos de acciones / parciales, y por lo tanto
-- poder asignar parciales a usuarios (árbitros) concretos.
--
CREATE TABLE Arbitraje_ListaArbitros (
    ID_ARBITRO INT(1) UNSIGNED NOT NULL,
    nombre VARCHAR(5) NOT NULL,
    descripcion VARCHAR(20) NOT NULL,
    PRIMARY KEY (ID_ARBITRO)
) ENGINE=InnoDB DEFAULT CHARSET=utf16 COLLATE=utf16_spanish_ci;


###############################################################################
--
-- Esta tabla define los diferentes tipos de controles que implementa la
-- aplicación de arbitraje. En la insercción de datos se incluye una 
-- descripción de cada uno de los tipos.
-- Campos:
--     - tipo_accion: ver INSERT INTO debajo.
--
CREATE TABLE Arbitraje_TipoAccion (
       ID_TIPO_ACCION 	INT UNSIGNED NOT NULL,
       tipo_accion 		VARCHAR(5) NOT NULL,
       PRIMARY KEY (ID_TIPO_ACCION)
) ENGINE=InnoDB DEFAULT CHARSET=utf16 COLLATE=utf16_spanish_ci 
     COMMENT='Tipo de campo: hacer click o por teclado';
--
-- Datos fijos para la tabla.
--
INSERT INTO Arbitraje_TipoAccion (
       ID_TIPO_ACCION, 
       tipo_accion) VALUES
    (0, 'nulo'),
    -- Se emplea este campo para insertar acciones que no deben generar
    -- control en la aplicación, sino que su valor se obtiene en función
    -- de otras acciones. Su uso es para la tabla de estadísticas.
    (1, 'click'),
    -- El valor se introduce mediante clicks del ratón sobre
    -- la zona activa definida por la acción, por ejemplo, un click
    -- aumenta en 1 su valor, y CTRL+Click reduce en uno su valor.
    (2, 'texto'),
    -- El valor se introduce en un campo de texto, por
    -- ejemplo, se selecciona con el ratón, y con el teclado se
    -- introduce el valor. Este tipo es para acciones cuyo valor sea
    -- típicamente números altos.
    (3, 'bool'),
    -- Para acciones que sean de marcar sí o no.
    (4, 'graf');
    -- Como un botón click, pero no se muestra un número con el valor de la
    -- acción, sino que se muestra un dibujo en función del valor de la
    -- acción. El valor de la acción se corresponde con el sufijo del
    -- nombre del dibujo. Por ejemplo, dibujo01.png cuando vale 1. El 
    -- índice se construye con 2 cifras, es decir, ¡podemos llegar hasta 100!

###############################################################################
--
-- Definición de los estilos de las fuentes para la aplicación de arbitraje.
-- Los formatos se corresponden con los definidos para tkinter en python.
--
CREATE TABLE Arbitraje_EstiloFuente (
       ID_ESTILO_FUENTE INT UNSIGNED NOT NULL,
       descripcion VARCHAR(50) NOT NULL,
       nombre_fuente VARCHAR(50) NOT NULL,
       estilo_fuente VARCHAR(10) NOT NULL COMMENT 'Negrita, cursiva, ...',
       tamano_fuente INT UNSIGNED NOT NULL COMMENT 'Tamaño de la fuente.',
       color_fuente VARCHAR(10) NOT NULL COMMENT 'Color de la fuente',
       -- color_fondo VARCHAR(10) NOT NULL COMMENT 'Color del fondo',
       PRIMARY KEY (ID_ESTILO_FUENTE)
) ENGINE=InnoDB DEFAULT CHARSET=utf16 COLLATE=utf16_spanish_ci
    COMMENT='Definición del estilo con el que se dibuja la zona activa';

###############################################################################
###############################################################################
--
-- Esta tabla permite agrupar diferentes acciones que se pueden realizar en
-- distintas partes del campo.
-- campos:
--     - comun: Si su valor es True, indica que el valor de un lado afecta
--       al valor de todos los lados. Por ejemplo, con las cajas de bellotas
--       de 2026, las cajas del lado sin pintar da puntos a ambos equipos. Y
--       si un equipo tiene mayoría de su color, le da el bonús a ese equipo,
--       y no al otro. Este campo lo utiliza la aplicación de arbitraje para
--       saber si al modificar una acción, debe actualizar sólo el parcial de
--       dicho equipo, o debe actualizar el de los dos equipos.
--
CREATE TABLE Arbitraje_GrupoAcciones (
    ID_GRUPO_ACCIONES INT UNSIGNED NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    comun BOOLEAN DEFAULT FALSE,
       PRIMARY KEY (ID_GRUPO_ACCIONES)
) ENGINE=InnoDB DEFAULT CHARSET=utf16 COLLATE=utf16_spanish_ci;

###############################################################################
###############################################################################
# Tablas de guías para ubicación de coordenadas de controles en la GUI
###############################################################################
###############################################################################
--
-- Definición de guías para la colocación de los grupos de controles. El campo
-- posición define valores absolutos en píxeles dentro de la imagen del fondo
-- de la aplicación.
--
CREATE TABLE Guia_GrupoX (
    ID_GUIA INT UNSIGNED NOT NULL,
    posicion INT NOT NULL,
    PRIMARY KEY (ID_GUIA)
) ENGINE=InnoDB DEFAULT CHARSET=utf16 COLLATE=utf16_spanish_ci;

CREATE TABLE Guia_GrupoY (
    ID_GUIA INT UNSIGNED NOT NULL,
    posicion INT NOT NULL,
    PRIMARY KEY (ID_GUIA)
) ENGINE=InnoDB DEFAULT CHARSET=utf16 COLLATE=utf16_spanish_ci;

###############################################################################
--
-- Definición de guías para la colocación de los controles. En este caso, el
-- campo posición define valores en píxeles relativos al grupo al que pertenece
-- la guía en cuestión.
--
CREATE TABLE Guia_ControlX (
    ID_GUIA INT UNSIGNED NOT NULL,
    FK_GRUPO_ACCIONES INT UNSIGNED NOT NULL,
    posicion INT NOT NULL,
    PRIMARY KEY (ID_GUIA, FK_GRUPO_ACCIONES)
) ENGINE=InnoDB DEFAULT CHARSET=utf16 COLLATE=utf16_spanish_ci;
ALTER TABLE Guia_ControlX
    ADD KEY guia_grupo_x (FK_GRUPO_ACCIONES),
    ADD CONSTRAINT guia_grupo_x FOREIGN KEY (FK_GRUPO_ACCIONES)
        REFERENCES Arbitraje_GrupoAcciones (ID_GRUPO_ACCIONES);

CREATE TABLE Guia_ControlY (
    ID_GUIA INT UNSIGNED NOT NULL,
    FK_GRUPO_ACCIONES INT UNSIGNED NOT NULL,
    posicion INT NOT NULL,
    PRIMARY KEY (ID_GUIA, FK_GRUPO_ACCIONES)
) ENGINE=InnoDB DEFAULT CHARSET=utf16 COLLATE=utf16_spanish_ci;
ALTER TABLE Guia_ControlY
    ADD KEY guia_grupo_y (FK_GRUPO_ACCIONES),
    ADD CONSTRAINT guia_grupo_y FOREIGN KEY (FK_GRUPO_ACCIONES)
        REFERENCES Arbitraje_GrupoAcciones (ID_GRUPO_ACCIONES);

###############################################################################
###############################################################################
--
-- Tabla para determinar la posición y características de la etiqueta para
-- marcar el total de cada zona de acciones. Se trata de una relación 1 a 1
-- con la tabla GrupoAcciones. No obstante, si el registro correspondiente a
-- un grupo no existe, significa que ese grupo no visualiza ningún total.
-- Aparte de esto, en la tabla ZonaAcciones se puede indicar que, para una
-- zona concreta de un grupo que sí tiene definida la etiqueta de total, que
-- para dicha zona el total no se muestre. Es decir, que para que en una zona
-- concreta se visualice su total, el grupo correspondiente debe incluir su
-- registro en esta tabla para indicar la posición, tamaño, etc de la etiqueta
-- del total, y tener marcado a TRUE el campo mostrar_puntos en la tabla
-- ZonaAcciones. Todo esto es procesado en la vista VistaAuxParciales, que
-- genera el campo mostrar_puntos a partir de si existe usuario para este grupo
--(si no existe, no se muestra puntos para ninguna zona de este grupos) y si se 
-- ha marcado la opción mostrar_puntos para una zona concreta en la
-- tabla ZonaAcciones.
--
-- Campos:
--     - zona_d: desplazamiento para los campos de texto. Esto es un truco
--       para que los textos queden centrados en el control, ya que en tkinter
--       la linéa de base de los caracteres está ligeramente elevada, y queda
--       descentrado. El campo d permite bajar un poco la línea de base. No
--       hay una fórmula para calcular este valor. De momento, probar a ojo
--       hasta que quede centrado.
--
CREATE TABLE Arbitraje_TotalGrupoAcciones (
	FK_GRUPO_ACCIONES INT UNSIGNED NOT NULL,
    FK_ESTILO_FUENTE INT UNSIGNED NOT NULL,
    FK_GUIA_X1 INT UNSIGNED NOT NULL,
    FK_GUIA_X2 INT UNSIGNED NOT NULL,
    FK_GUIA_Y1 INT UNSIGNED NOT NULL,
    FK_GUIA_Y2 INT UNSIGNED NOT NULL,
    zona_d INT NOT NULL DEFAULT 0,
    PRIMARY KEY (FK_GRUPO_ACCIONES)
) ENGINE=InnoDB DEFAULT CHARSET=utf16 COLLATE=utf16_spanish_ci;
ALTER TABLE Arbitraje_TotalGrupoAcciones
    ADD KEY total_grupo_acciones (FK_GRUPO_ACCIONES),
    ADD CONSTRAINT total_grupo_acciones FOREIGN KEY (FK_GRUPO_ACCIONES)
        REFERENCES Arbitraje_GrupoAcciones (ID_GRUPO_ACCIONES),
    
    ADD KEY estilo_parcial (FK_ESTILO_FUENTE),
    ADD CONSTRAINT estilo_parcial FOREIGN KEY (FK_ESTILO_FUENTE)
        REFERENCES Arbitraje_EstiloFuente (ID_ESTILO_FUENTE),
        
    ADD KEY guia_x1_parcial (FK_GRUPO_ACCIONES, FK_GUIA_X1),
    ADD CONSTRAINT guia_x1_parcial FOREIGN KEY (FK_GRUPO_ACCIONES, FK_GUIA_X1)
        REFERENCES Guia_ControlX (FK_GRUPO_ACCIONES, ID_GUIA),
    ADD KEY guia_x2_parcial (FK_GRUPO_ACCIONES, FK_GUIA_X2),
    ADD CONSTRAINT guia_x2_parcial FOREIGN KEY (FK_GRUPO_ACCIONES, FK_GUIA_X2)
        REFERENCES Guia_ControlX (FK_GRUPO_ACCIONES, ID_GUIA),
    ADD KEY guia_y1_parcial (FK_GRUPO_ACCIONES, FK_GUIA_Y1),
    ADD CONSTRAINT guia_y1_parcial FOREIGN KEY (FK_GRUPO_ACCIONES, FK_GUIA_Y1)
        REFERENCES Guia_ControlY (FK_GRUPO_ACCIONES, ID_GUIA),
    ADD KEY guia_y2_parcial (FK_GRUPO_ACCIONES, FK_GUIA_Y2),
    ADD CONSTRAINT guia_y2_parcial FOREIGN KEY (FK_GRUPO_ACCIONES, FK_GUIA_Y2)
        REFERENCES Guia_ControlY (FK_GRUPO_ACCIONES, ID_GUIA);
        
###############################################################################
###############################################################################
--
-- Tabla TipoAcciones
--
-- Esta tabla define las diferentes acciones que se pueden realizar. Cada
-- registro en esta tabla genera un control (botón, texto) en la aplicación
-- de arbitraje en cada zona en la que se haya añadido el grupo al que pertenece
-- el control.
--
-- Campos:
--     - FK_TIPO_ACCION: Ver tabla Arbitraje_TipoAccion
--     - publicar: indica si el valor debe aparecer en la tabla de estadísticas.
--       Ver vista Estadisticas (quizás no esté implementada para una edición
--       concreta, ya que no es una vista esencial para el funcionamiento de
--       todo el sistema, sino que es informativa para los participantes).
--     - valor_maximo: si es igual a NULL, no hay un límite superior.
--     - img_pos: indica la posición del icono con respecto al número, para
--       controles de tipo click. Sus valores son "w" (izquierda), "e" (derecha)
--       "n" (arriba), "s" (abajo).
--     - directorio: nombre completo de la imagen que se usará como icono. La
--       extensión del icono debe ser png. El directorio completo se define en
--       el archivo de configuración de la aplicación (xml).
--     - accion: descripción de la acción.
--     - FK_GUIA_X1, X2, Y1, Y2: referencias a las guías sobre las que se
--       define el botón de la acción. Sus valores son posiciones relativas con
--       respecto a la posición absoluta del grupo definido en la tabla
--       ZonaAcciones.
--     - tipo_d: Ver zona_d en tabla TotalGrupoAcciones.
-- 
--
CREATE TABLE Arbitraje_TipoAcciones (
    ID_TIPO_ACCIONES INT UNSIGNED NOT NULL,
    FK_GRUPO_ACCIONES INT UNSIGNED NOT NULL,
    FK_ESTILO_FUENTE INT UNSIGNED NOT NULL,
    FK_TIPO_ACCION INT UNSIGNED NOT NULL,
    publicar BOOLEAN NOT NULL,
    valor_maximo INT NULL,
    img_pos VARCHAR(1) DEFAULT NULL,
    directorio VARCHAR (256) NOT NULL,
    accion VARCHAR(256) NOT NULL,
    FK_GUIA_X1 INT UNSIGNED NOT NULL,
    FK_GUIA_X2 INT UNSIGNED NOT NULL,
    FK_GUIA_Y1 INT UNSIGNED NOT NULL,
    FK_GUIA_Y2 INT UNSIGNED NOT NULL,
    tipo_d INT NOT NULL DEFAULT 0,
    PRIMARY KEY (ID_TIPO_ACCIONES, FK_GRUPO_ACCIONES)
) ENGINE=InnoDB DEFAULT CHARSET=utf16 COLLATE=utf16_spanish_ci;
ALTER TABLE Arbitraje_TipoAcciones
    ADD KEY tipo_accion (FK_TIPO_ACCION),
    ADD CONSTRAINT tipo_accion FOREIGN KEY (FK_TIPO_ACCION)
        REFERENCES Arbitraje_TipoAccion (ID_TIPO_ACCION),
    ADD KEY grupo_acciones (FK_GRUPO_ACCIONES),
    ADD CONSTRAINT grupo_acciones FOREIGN KEY (FK_GRUPO_ACCIONES)
        REFERENCES Arbitraje_GrupoAcciones (ID_GRUPO_ACCIONES),
    ADD KEY estilo_accion (FK_ESTILO_FUENTE),
    ADD CONSTRAINT estilo_accion FOREIGN KEY (FK_ESTILO_FUENTE)
        REFERENCES Arbitraje_EstiloFuente (ID_ESTILO_FUENTE),

    ADD KEY guia_x1 (FK_GRUPO_ACCIONES, FK_GUIA_X1),
    ADD CONSTRAINT guia_x1 FOREIGN KEY (FK_GRUPO_ACCIONES, FK_GUIA_X1)
        REFERENCES Guia_ControlX (FK_GRUPO_ACCIONES, ID_GUIA),
    ADD KEY guia_x2 (FK_GRUPO_ACCIONES, FK_GUIA_X2),
    ADD CONSTRAINT guia_x2 FOREIGN KEY (FK_GRUPO_ACCIONES, FK_GUIA_X2)
        REFERENCES Guia_ControlX (FK_GRUPO_ACCIONES, ID_GUIA),
    ADD KEY guia_y1 (FK_GRUPO_ACCIONES, FK_GUIA_Y1),
    ADD CONSTRAINT guia_y1 FOREIGN KEY (FK_GRUPO_ACCIONES, FK_GUIA_Y1)
        REFERENCES Guia_ControlY (FK_GRUPO_ACCIONES, ID_GUIA),
    ADD KEY guia_y2 (FK_GRUPO_ACCIONES, FK_GUIA_Y2),
    ADD CONSTRAINT guia_y2 FOREIGN KEY (FK_GRUPO_ACCIONES, FK_GUIA_Y2)
        REFERENCES Guia_ControlY (FK_GRUPO_ACCIONES, ID_GUIA);

###############################################################################
###############################################################################
--
-- Tabla ZonaAcciones
--
-- Esta tabla identifica todas las zonas del campo donde se pueden realizar
-- las acciones de la tabla GrupoAcciones. Los registos de esta tabla se
-- traducen en registros en la tabla Parciales para cada uno de los partidos.
-- IMPORTANTE: Cada registro de la tabla Arbitraje_TipoAcciones debe tener un
-- registro asociado de esta tabla (acciones con parciales). Sin embargo, puede
-- haber registros de esta tabla que no tengan registros asociados en la anterior
-- (parciales sin acciones asociadas), por ejemplo el campo de TOTAL debe
-- incluir un registro en esta tabla para que se visualice en la aplicación, pero
-- no tiene ninguna acción asociada ( ya que su valor se obtiene a partir del
-- resto de parciales).
-- Campos:
--     - FK_LADO: Es en este punto donde se asignan grupos de acciones a uno
--       de los lados (equipo participante) del partido. Este campo permite
--       a las funciones de cálculo asignar los puntos al equipo correspondiente
--       y además permite a la aplicación de arbitraje determinar el color del
--       fondo de los controles (junto con el campo color_v, ver más abajo).
--     - zona: descripción de la zona
--     - valor_defecto: si al iniciar el partido, debe tener un valor distinto
--       de cero, asignarlo aquí.
--     - reflejar_x: si es True, al representar todos los controles de acciones
--       asociados a esta zona se reflejan. Esto puede ser útil, ya que en
--       general el campo de Eurobot es simétrico, por lo que para definir
--       los cotroles de un lado, basta con reflejar los del otro lado.
--     - FK_OFFSET_X, Y: Posición dentro de la imagen del campo, donde se
--       representarán todas los controles correspondientes a las acciones
--       asociadas a esta zona, y el control del total de puntos para este
--       parcial. Este campo define la posición absoluta, en píxeles, de todo
--       el conjunto de controles, y luego cada control se situa a partir de
--       las posiciones relativas definidas en la tabla TipoAcciones.
--     - mostrar_puntos: Si es False, la aplicación de arbitraje no debe
--       mostrar la etiqueta con el total de puntos para esta zona.
--     - color_v: Intensidad del color con el que se representarán el fondo
--       de los controles asociados a este parcial. El color se forma a
--       partir de este valor V, y de los valores H y S definidos en la
--       tabla General_Lado. Es decir, todos los controles de un mismo
--       lado tienen el mismo color, pero podemos cambiar la intensidad
--       para los distintos parciales del mismo lado.
--
CREATE TABLE Arbitraje_ZonaAcciones (
    ID_ZONA_ACCIONES INT UNSIGNED NOT NULL,
    FK_GRUPO_ACCIONES INT UNSIGNED NOT NULL,
    FK_LADO INT UNSIGNED NOT NULL,
    FK_ARBITRO INT UNSIGNED,
    
    zona VARCHAR(256) NOT NULL,
    valor_defecto INT UNSIGNED DEFAULT 0,
    reflejar_x BOOL NOT NULL DEFAULT FALSE,
    FK_OFFSET_X INT UNSIGNED NOT NULL,
    FK_OFFSET_Y INT UNSIGNED NOT NULL,
    mostrar_puntos BOOL,
    color_v INT NOT NULL DEFAULT 255,
    
    PRIMARY KEY (ID_ZONA_ACCIONES, FK_GRUPO_ACCIONES, FK_LADO)
) ENGINE=InnoDB DEFAULT CHARSET=utf16 COLLATE=utf16_spanish_ci;
ALTER TABLE Arbitraje_ZonaAcciones
    ADD KEY grupo_zona_acciones (FK_GRUPO_ACCIONES),
    ADD CONSTRAINT grupo_zona_acciones FOREIGN KEY (FK_GRUPO_ACCIONES)
        REFERENCES Arbitraje_GrupoAcciones (ID_GRUPO_ACCIONES),
    ADD KEY lado_acciones (FK_LADO),
    ADD CONSTRAINT lado_acciones FOREIGN KEY (FK_LADO)
        REFERENCES Partido_Lado (ID_LADO),
    ADD KEY arbitro_zona (FK_ARBITRO),
    ADD CONSTRAINT arbitro_zona FOREIGN KEY (FK_ARBITRO)
        REFERENCES Arbitraje_ListaArbitros (ID_ARBITRO),

    ADD KEY guia_offset_x (FK_OFFSET_X),
    ADD CONSTRAINT guia_offset_x FOREIGN KEY (FK_OFFSET_X)
        REFERENCES Guia_GrupoX (ID_GUIA),
    ADD KEY guia_offset_y (FK_OFFSET_Y),
    ADD CONSTRAINT guia_offset_y FOREIGN KEY (FK_OFFSET_Y)
        REFERENCES Guia_GrupoY (ID_GUIA);


###############################################################################
###############################################################################
# VISTAS AUXILIARES PARA LAS TABLAS DE ACCIONES Y PARCIALES
###############################################################################
###############################################################################
/*
--
-- Vista auxiliar para obtener todos los iconos a mostrar en la aplicación de
-- arbitraje.
--
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER
        VIEW Arbitraje_IconosAcciones AS
    SELECT ROW_NUMBER() OVER (
               ORDER BY
                   FK_GRUPO_ACCIONES ASC,
                   ID_TIPO_ACCIONES ASC) AS ID_ICONO,
           Arbitraje_TipoAcciones.ID_TIPO_ACCIONES,
           Arbitraje_TipoAcciones.FK_GRUPO_ACCIONES,
           Arbitraje_TipoAcciones.FK_TIPO_ACCION,
           Arbitraje_TipoAcciones.directorio,
           Arbitraje_TipoAcciones.valor_maximo,
           Arbitraje_TipoAcciones.accion
      FROM Arbitraje_TipoAcciones;
*/
--
-- Vista auxiliar para obtener todos los iconos a mostrar en la aplicación de
-- arbitraje (ver aplicación de arbitraje).
--
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER
        VIEW Arbitraje_IconosAcciones AS
    SELECT Arbitraje_TipoAcciones.ID_TIPO_ACCIONES,
           Arbitraje_TipoAcciones.FK_GRUPO_ACCIONES,
           Arbitraje_TipoAcciones.FK_TIPO_ACCION,
           Arbitraje_TipoAcciones.directorio,
           Arbitraje_TipoAcciones.valor_maximo,
           Arbitraje_TipoAcciones.accion
      FROM Arbitraje_TipoAcciones;
###############################################################################
--
-- Vista auxiliar para obtener los valores de posición y ancho / alto de las
-- acciones a partir de las guías de controles. Esta vista permite que las guías
-- no tengan por qué estar definidas en orden, es decir, la de coordenada más
-- pequeña la primera.
--
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER
       VIEW Arbitraje_VistaAuxGuiasAcciones AS
    SELECT Arbitraje_TipoAcciones.ID_TIPO_ACCIONES,
           Arbitraje_TipoAcciones.FK_GRUPO_ACCIONES,
           Arbitraje_TipoAcciones.FK_ESTILO_FUENTE,
           Arbitraje_TipoAcciones.FK_TIPO_ACCION,
           Arbitraje_TipoAcciones.publicar,
           Arbitraje_TipoAcciones.valor_maximo,
           Arbitraje_TipoAcciones.img_pos,
           Arbitraje_TipoAcciones.directorio,
           Arbitraje_TipoAcciones.accion,
           -- La posición se corresponde con el menor valor de los dos.
           IF (X1.posicion < X2.posicion, X1.posicion, X2.posicion) AS tipo_x,
           IF (Y1.posicion < Y2.posicion, Y1.posicion, Y2.posicion) AS tipo_y,
           -- Y el tamaño será igual al valor absoluto de la diferencia. De esta
           -- forma, no importa el orden en el que se definan las guías.
           ABS(X1.posicion - X2.posicion) AS tipo_w,
           ABS(Y1.posicion - Y2.posicion) AS tipo_h,
           Arbitraje_TipoAcciones.tipo_d
      FROM Arbitraje_TipoAcciones
          INNER JOIN Guia_ControlX AS X1
                ON Arbitraje_TipoAcciones.FK_GUIA_X1 = X1.ID_GUIA
                AND Arbitraje_TipoAcciones.FK_GRUPO_ACCIONES = X1.FK_GRUPO_ACCIONES
          INNER JOIN Guia_ControlX AS X2
                ON Arbitraje_TipoAcciones.FK_GUIA_X2 = X2.ID_GUIA
                AND Arbitraje_TipoAcciones.FK_GRUPO_ACCIONES = X2.FK_GRUPO_ACCIONES
          INNER JOIN Guia_ControlY AS Y1
                ON Arbitraje_TipoAcciones.FK_GUIA_Y1 = Y1.ID_GUIA
                AND Arbitraje_TipoAcciones.FK_GRUPO_ACCIONES = Y1.FK_GRUPO_ACCIONES
          INNER JOIN Guia_ControlY AS Y2
                ON Arbitraje_TipoAcciones.FK_GUIA_Y2 = Y2.ID_GUIA
                AND Arbitraje_TipoAcciones.FK_GRUPO_ACCIONES = Y2.FK_GRUPO_ACCIONES;
###############################################################################
-- 
-- Vista AuxAcciones
--
-- Obtiene una vista con todas las acciones definidas para una competición.
-- Se emplea para añadir correctamente todas las acciones a la tabla Accion
-- para un nuevo partido creado (ver trigger anadir_parciales_partido).
--
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER 
       VIEW Arbitraje_VistaAuxAcciones AS 
    SELECT Arbitraje_ZonaAcciones.ID_ZONA_ACCIONES,
           Arbitraje_TipoAcciones.FK_GRUPO_ACCIONES,
           Arbitraje_TipoAcciones.ID_TIPO_ACCIONES,
		   Arbitraje_ZonaAcciones.FK_LADO,
           Arbitraje_ZonaAcciones.FK_ARBITRO,
           Arbitraje_GrupoAcciones.comun,
           Arbitraje_TipoAcciones.FK_TIPO_ACCION,
           -- Si reflejamos en horizontal, cambiamos también la posición del
           -- icono con respecto al número (sólo para acciones de tipo click)
           CASE 
               WHEN reflejar_x THEN
               CASE 
                   WHEN Arbitraje_TipoAcciones.img_pos = "w" THEN "e"
                   WHEN Arbitraje_TipoAcciones.img_pos = "e" THEN "w"
                   ELSE Arbitraje_TipoAcciones.img_pos
               END 
               ELSE Arbitraje_TipoAcciones.img_pos 
           END AS img_pos,
           Arbitraje_TipoAcciones.directorio,
           Arbitraje_TipoAcciones.accion as descripcion,
           Arbitraje_ZonaAcciones.zona,
           -- Estilo del control:
           Arbitraje_EstiloFuente.nombre_fuente,
           Arbitraje_EstiloFuente.tamano_fuente,
           Arbitraje_EstiloFuente.estilo_fuente,
           Arbitraje_EstiloFuente.color_fuente,
           Partido_Lado.color_h AS color_h_fondo,
           Partido_Lado.color_s AS color_s_fondo,
           Arbitraje_ZonaAcciones.color_v AS color_v_fondo,
		   -- Posición del control.
           CASE 
               WHEN reflejar_x THEN Guia_GrupoX.posicion - tipo_x - tipo_w 
               ELSE Guia_GrupoX.posicion + tipo_x 
           END AS pos_x,
           Guia_GrupoY.posicion + tipo_y AS pos_y,
           tipo_w AS ancho,
           tipo_h AS alto,
           tipo_d AS desplazamiento
           
     FROM Arbitraje_VistaAuxGuiasAcciones AS Arbitraje_TipoAcciones
          -- Aquí hacemos un CROSS JOIN, para replicar todos los controles
          -- asociados a un grupo en todas las zonas correspondientes a ese
          -- grupo.
          JOIN Arbitraje_ZonaAcciones
               ON Arbitraje_TipoAcciones.FK_GRUPO_ACCIONES = 
               Arbitraje_ZonaAcciones.FK_GRUPO_ACCIONES
          INNER JOIN Arbitraje_GrupoAcciones
               ON Arbitraje_TipoAcciones.FK_GRUPO_ACCIONES = Arbitraje_GrupoAcciones.ID_GRUPO_ACCIONES
          INNER JOIN Arbitraje_EstiloFuente
                ON Arbitraje_TipoAcciones.FK_ESTILO_FUENTE = 
                Arbitraje_EstiloFuente.ID_ESTILO_FUENTE
          INNER JOIN Partido_Lado
                ON Arbitraje_ZonaAcciones.FK_LADO = Partido_Lado.ID_LADO

          INNER JOIN Guia_GrupoX
                ON Arbitraje_ZonaAcciones.FK_OFFSET_X = Guia_GrupoX.ID_GUIA
          INNER JOIN Guia_GrupoY
                ON Arbitraje_ZonaAcciones.FK_OFFSET_Y = Guia_GrupoY.ID_GUIA;

###############################################################################
--
-- Idem que Arbitraje_VistaAuxGuiasAcciones
--
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER
       VIEW Arbitraje_VistaAuxGuiasParciales AS
    SELECT Arbitraje_ZonaAcciones.ID_ZONA_ACCIONES,
           Arbitraje_ZonaAcciones.FK_GRUPO_ACCIONES,
           Arbitraje_ZonaAcciones.FK_LADO,
           Arbitraje_TotalGrupoAcciones.FK_ESTILO_FUENTE,
           IF (X1.posicion < X2.posicion, X1.posicion, X2.posicion) AS zona_x,
           IF (Y1.posicion < Y2.posicion, Y1.posicion, Y2.posicion) AS zona_y,
           ABS(X1.posicion - X2.posicion) AS zona_w,
           ABS(Y1.posicion - Y2.posicion) AS zona_h,
           Arbitraje_TotalGrupoAcciones.zona_d
      FROM Arbitraje_ZonaAcciones
      -- NOTA: Hacemos LEFT JOIN, ya que para algunos grupos no existe registros de 
      -- total. Esto ocurre en los grupos en los que no necesitamos sacar el total
      -- de puntos de ese grupo.
          LEFT JOIN Arbitraje_TotalGrupoAcciones
                ON Arbitraje_ZonaAcciones.FK_GRUPO_ACCIONES = Arbitraje_TotalGrupoAcciones.FK_GRUPO_ACCIONES
      -- Y debido a lo anterior, todas las relaciones con la tabla de la derecha
      -- deben llevar el LEFT.          
          LEFT JOIN Guia_ControlX AS X1
                ON Arbitraje_TotalGrupoAcciones.FK_GUIA_X1 = X1.ID_GUIA
                AND Arbitraje_TotalGrupoAcciones.FK_GRUPO_ACCIONES = X1.FK_GRUPO_ACCIONES
          LEFT JOIN Guia_ControlX AS X2
                ON Arbitraje_TotalGrupoAcciones.FK_GUIA_X2 = X2.ID_GUIA
                AND Arbitraje_TotalGrupoAcciones.FK_GRUPO_ACCIONES = X2.FK_GRUPO_ACCIONES
          LEFT JOIN Guia_ControlY AS Y1
                ON Arbitraje_TotalGrupoAcciones.FK_GUIA_Y1 = Y1.ID_GUIA
                AND Arbitraje_TotalGrupoAcciones.FK_GRUPO_ACCIONES = Y1.FK_GRUPO_ACCIONES
          LEFT JOIN Guia_ControlY AS Y2
                ON Arbitraje_TotalGrupoAcciones.FK_GUIA_Y2 = Y2.ID_GUIA
                AND Arbitraje_TotalGrupoAcciones.FK_GRUPO_ACCIONES = Y2.FK_GRUPO_ACCIONES;          

###############################################################################
-- 
-- Vista AuxParciales
--
-- Iden que Arbitraje_VistaAuxAcciones para los parciales. Los registros generados
-- se insertan en la tabla Parcial para un nuevo partido creado (ver trigger
-- anadir_parciales_partido).
--
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER 
       VIEW Arbitraje_VistaAuxParciales AS 
    SELECT Arbitraje_ZonaAcciones.ID_ZONA_ACCIONES,
           Arbitraje_ZonaAcciones.FK_GRUPO_ACCIONES,
		   Arbitraje_ZonaAcciones.FK_LADO,
           Arbitraje_ZonaAcciones.FK_ARBITRO,
           Arbitraje_GrupoAcciones.comun,
           Arbitraje_ZonaAcciones.zona AS descripcion,
           -- Estilo de la etiqueta de total (si existe)
           Arbitraje_EstiloFuente.nombre_fuente,
           Arbitraje_EstiloFuente.tamano_fuente,
           Arbitraje_EstiloFuente.estilo_fuente,
           Arbitraje_EstiloFuente.color_fuente, 
           Partido_Lado.color_h AS color_h_fondo,
           Partido_Lado.color_s AS color_s_fondo,
           Arbitraje_ZonaAcciones.color_v AS color_v_fondo,
           -- NOTA: Puede darse el caso que se inserte una zona sin guias
           -- de posición, pero con mostrar_puntos igual a FALSE. Esto
           -- provocará en la aplicación de arbitraje un error, así que
           -- con este AND conseguimos que si el usuario no ha insertado
           -- guías, se obtenga no mostrar puntos aunque se haya puesto
           -- a TRUE.
           Arbitraje_ZonaAcciones.mostrar_puntos 
               AND zona_x IS NOT NULL 
               AND zona_y IS NOT NULL AS mostrar_puntos,
           -- Posición absoluta para todo el todo el grupo de controles.
           CASE 
               WHEN reflejar_x THEN Guia_GrupoX.posicion - zona_x - zona_w 
               ELSE Guia_GrupoX.posicion + zona_x 
           END AS pos_x,
           Guia_GrupoY.posicion + zona_y AS pos_y,
           zona_w AS ancho,
           zona_h AS alto,
           zona_d AS desplazamiento
           
     FROM Arbitraje_ZonaAcciones
          INNER JOIN Arbitraje_GrupoAcciones
               ON Arbitraje_ZonaAcciones.FK_GRUPO_ACCIONES = Arbitraje_GrupoAcciones.ID_GRUPO_ACCIONES

          INNER JOIN Partido_Lado
              ON Arbitraje_ZonaAcciones.FK_LADO = Partido_Lado.ID_LADO

          INNER JOIN Guia_GrupoX
                ON Arbitraje_ZonaAcciones.FK_OFFSET_X = Guia_GrupoX.ID_GUIA
          INNER JOIN Guia_GrupoY
                ON Arbitraje_ZonaAcciones.FK_OFFSET_Y = Guia_GrupoY.ID_GUIA
                
          INNER JOIN Arbitraje_VistaAuxGuiasParciales
                ON Arbitraje_ZonaAcciones.ID_ZONA_ACCIONES = Arbitraje_VistaAuxGuiasParciales.ID_ZONA_ACCIONES
                AND Arbitraje_ZonaAcciones.FK_GRUPO_ACCIONES = Arbitraje_VistaAuxGuiasParciales.FK_GRUPO_ACCIONES
                AND Arbitraje_ZonaAcciones.FK_LADO = Arbitraje_VistaAuxGuiasParciales.FK_LADO
          LEFT JOIN Arbitraje_EstiloFuente
              ON Arbitraje_VistaAuxGuiasParciales.FK_ESTILO_FUENTE = 
                 Arbitraje_EstiloFuente.ID_ESTILO_FUENTE;     

###############################################################################
###############################################################################
# TABLAS DE ETIQUETAS
###############################################################################
###############################################################################
-- Las etiquetas son textos o gráficos que se añaden en la aplicación de
-- arbitraje y que no tiene que ver con las puntuaciones. Por ejemplo, el
-- nombre del equipo, su logo, etc. También se puede utilizar para añadir
-- textos fijos, para poder utilizar la misma fuente que la que se utiliza
-- en las acciones y parciales. Para diferenciar entre etiquetas fijas y
-- dependientes del partido, en la tabla Arbitraje_Etiqueta definimos el
-- campo "externa"" (ver descripción de la tabla).

-- NOTA: Se puede pensar inicialmente que en lugar de definir aquí los textos
-- fijos, se pueden poner como parte de la imagen del fondo. Sin embargo, de
-- esta forma, conseguimos que las fuentes sean las mismas (si editamos la
-- imagen del fondo por ejemplo con GIMP, es posible que las fuentes de GIMP
-- no sean las mismas que las que utiliza tkinter). Además, así se puede
-- configurar la aplicación para diferentes idiomas ("Puntos Totales" ->
-- "Total Points").
###############################################################################
###############################################################################
--
-- Si vamos a crear la base de datos solo para la edición de los controles de
-- la aplicación de arbitraje, sin crear las tablas de equipos y partidos,
-- entonces no tendremos la vista con las etiquetas que dependen del partido
-- (dorsal, nombre y logo del equipo, etc). Para solucionar esto, hacemos el
-- siguiente truco. Creamos una tabla auxiliar donde podemos añadir las
-- etiquetas de los datos del partido (nombre equipo, etc).
-- (seguir leyendo debajo...)
--
CREATE TABLE Arbitraje_AuxEtiquetasPartido(
    ID_PARTIDO INT UNSIGNED NOT NULL DEFAULT 1,
    ID_ETIQUETA VARCHAR(10) NOT NULL,
    FK_LADO INT UNSIGNED,
    tipo INT UNSIGNED NOT NULL DEFAULT 1,
    valor VARCHAR(50) DEFAULT "",
    PRIMARY KEY (ID_PARTIDO, ID_ETIQUETA, FK_LADO)
) ENGINE=InnoDB DEFAULT CHARSET=utf16 COLLATE=utf16_spanish_ci;
ALTER TABLE Arbitraje_AuxEtiquetasPartido
    ADD KEY lado_etiqueta_aux (FK_LADO),
    ADD CONSTRAINT lado_etiqueta_aux FOREIGN KEY (FK_LADO)
        REFERENCES Partido_Lado (ID_LADO);

###############################################################################
--
-- (...continua de arriba)
-- y creamos la vista con los datos del partido. En la bd completa, esta vista
-- se crea en la propia base de datos, pero si no tenemos la base de datos,
-- no tendremos la vista. Por eso, sólo en el caso de que la vista no exista,
-- (porque no estamos creando la bd completa) creamos esta vista (falsa) para
-- poder contruir la bd.
--
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER 
       VIEW IF NOT EXISTS VistaPartido_EtiquetasPartido AS 
    SELECT *
     FROM Arbitraje_AuxEtiquetasPartido;
         
###############################################################################
--
-- Esta tabla permite crear etiquetas adicionales para mostrar en la aplicación
-- de arbitraje, tales como los nombres de los equipos, sus dorsales, etc.

-- Campos:
--    - FK_GRUPO_ACCIONES: El grupo se emplea para determinar la posición
--        absoluta de las etiquetas en el mapa. Las etiquetas pueden existir
--        solas (es decir, un grupo de etiquetas sin ningún control), o bien
--        pueden existir junto a otros controles de acciones (opción añadida
--        en 2026 cuando se creó a aplicación de diseño del mapa de puntos).
--      FK_GUIA_X1, X2, Y1, Y2: Idem que para la tabla TipoAcciones.
--    - externa. Indica el origen del valor de la etiqueta. Si es FALSE,
--        el valor se obtiene del campo valor de esta tabla, por lo que se trata
--        de una etiqueta fija (siempre toma el mismo valor). Si es TRUE, el
--        valor se obtiene de la vista VistaPartido_EtiquetasPartido, por lo
--        que su valor depende del partido (nombre del equipo, dorsal, etc.).
--     - tipo: identifica el tipo de etiqueta. Sus posibles valores son:
--       - 1: texto: En este caso, indica el texto a mostrar.
--       - 2: imagen: Indica el nombre de la imagen a abrir. El directorio
--            de la imagen se encuentra en los parámetros de configufración
--            de la aplicación (archivo xml).
--       - 3: imagen web: igual que 2, pero la imagen hay que descargarla
--            de la web. Igual que antes, la uri de la imagen se encuentra en
--            el archivo xml de configuración.
--     - valor: en función del parámetro "externa", almacena el valor de la
--       etiqueta, o bien el registro de la vista VistaPartido_EtiquetasPartido
--       del cual hay que obtener su valor. La vista anterior está definida
--       (versión de julio 2026) en el archivo PARTIDO_2_EQUIPOS.
--     - etiqueta_d: Ver tabla TotalGrupoAcciones
--     - color_v: Ver tabla ZonaAcciones.
--
CREATE TABLE Arbitraje_Etiqueta (
    ID_ETIQUETA INT UNSIGNED NOT NULL,
    FK_GRUPO_ACCIONES INT UNSIGNED NOT NULL,
    FK_ESTILO_FUENTE INT UNSIGNED NOT NULL,
    FK_GUIA_X1 INT UNSIGNED NOT NULL,
    FK_GUIA_X2 INT UNSIGNED NOT NULL,
    FK_GUIA_Y1 INT UNSIGNED NOT NULL,
    FK_GUIA_Y2 INT UNSIGNED NOT NULL,
    externa BOOLEAN,
    tipo INT UNSIGNED NOT NULL DEFAULT 1,
    valor VARCHAR(50),
    etiqueta_d INT NOT NULL DEFAULT 0,
    color_v INT UNSIGNED NOT NULL DEFAULT 255,
    justificacion VARCHAR(6) NOT NULL DEFAULT 'c',
    PRIMARY KEY (ID_ETIQUETA, FK_GRUPO_ACCIONES)
) ENGINE=InnoDB DEFAULT CHARSET=utf16 COLLATE=utf16_spanish_ci;
ALTER TABLE Arbitraje_Etiqueta
    ADD KEY grupo_etiqueta (FK_GRUPO_ACCIONES),
    ADD CONSTRAINT grupo_etiqueta FOREIGN KEY (FK_GRUPO_ACCIONES)
        REFERENCES Arbitraje_GrupoAcciones (ID_GRUPO_ACCIONES),
    ADD KEY estilo_etiqueta (FK_ESTILO_FUENTE),
    ADD CONSTRAINT estilo_etiqueta FOREIGN KEY (FK_ESTILO_FUENTE)
        REFERENCES Arbitraje_EstiloFuente (ID_ESTILO_FUENTE),

    ADD KEY guia_etiqueta_x1 (FK_GRUPO_ACCIONES, FK_GUIA_X1),
    ADD CONSTRAINT guia_etiqueta_x1 FOREIGN KEY (FK_GRUPO_ACCIONES, FK_GUIA_X1)
        REFERENCES Guia_ControlX (FK_GRUPO_ACCIONES, ID_GUIA),
    ADD KEY guia_etiqueta_x2 (FK_GRUPO_ACCIONES, FK_GUIA_X2),
    ADD CONSTRAINT guia_etiqueta_x2 FOREIGN KEY (FK_GRUPO_ACCIONES, FK_GUIA_X2)
        REFERENCES Guia_ControlX (FK_GRUPO_ACCIONES, ID_GUIA),
    ADD KEY guia_etiqueta_y1 (FK_GRUPO_ACCIONES, FK_GUIA_Y1),
    ADD CONSTRAINT guia_etiqueta_y1 FOREIGN KEY (FK_GRUPO_ACCIONES, FK_GUIA_Y1)
        REFERENCES Guia_ControlY (FK_GRUPO_ACCIONES, ID_GUIA),
    ADD KEY guia_etiqueta_y2 (FK_GRUPO_ACCIONES, FK_GUIA_Y2),
    ADD CONSTRAINT guia_etiqueta_y2 FOREIGN KEY (FK_GRUPO_ACCIONES, FK_GUIA_Y2)
        REFERENCES Guia_ControlY (FK_GRUPO_ACCIONES, ID_GUIA);

###############################################################################
--
-- Vista para unir las etiquetas fijas (externa=FALSE) con las etiquetas
-- que dependen del partido (externa=TRUE) en una única vista, para simplificar
-- la estructura de la vista Arbitraje_VistaAuxEtiquetas. El campo externa es
-- el que permite diferenciar entre etiquetas fijas y variables.
--
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER 
       VIEW Arbitraje_VistaUnionEtiquetas AS
-- Etiquetas fijas
    SELECT NULL AS ID_PARTIDO,
           NULL AS FK_LADO,
           Arbitraje_Etiqueta.*,
           Arbitraje_Etiqueta.valor AS valor_final
      FROM Arbitraje_Etiqueta
     WHERE NOT externa
UNION
-- Etiquetas variables
    SELECT VistaPartido_EtiquetasPartido.ID_PARTIDO,
           VistaPartido_EtiquetasPartido.FK_LADO,
           Arbitraje_Etiqueta.*,
           VistaPartido_EtiquetasPartido.valor AS valor_final
      FROM Arbitraje_Etiqueta
           INNER JOIN VistaPartido_EtiquetasPartido
           -- Esta instruccióne es la que relaciona el campo valor con el
           -- registro de la vista EtiquetasPartido.
               ON Arbitraje_Etiqueta.valor = VistaPartido_EtiquetasPartido.ID_ETIQUETA
     WHERE externa;

###############################################################################
--
-- Idem que Arbitraje_VistaAuxGuiasAcciones
--
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER
       VIEW Arbitraje_VistaAuxGuiasEtiquetas AS
   SELECT Arbitraje_Etiqueta.ID_PARTIDO,
          Arbitraje_Etiqueta.FK_LADO,
          Arbitraje_Etiqueta.ID_ETIQUETA,
          Arbitraje_Etiqueta.FK_GRUPO_ACCIONES,
          Arbitraje_Etiqueta.FK_ESTILO_FUENTE,
          IF (X1.posicion < X2.posicion, X1.posicion, X2.posicion) AS etiqueta_x,
          IF (Y1.posicion < Y2.posicion, Y1.posicion, Y2.posicion) AS etiqueta_y,
          ABS(X1.posicion - X2.posicion) AS etiqueta_w,
          ABS(Y1.posicion - Y2.posicion) AS etiqueta_h,

          Arbitraje_Etiqueta.tipo,
          Arbitraje_Etiqueta.valor_final AS valor,
          Arbitraje_Etiqueta.etiqueta_d,
          Arbitraje_Etiqueta.color_v,
          Arbitraje_Etiqueta.justificacion
     FROM Arbitraje_VistaUnionEtiquetas AS Arbitraje_Etiqueta
          INNER JOIN Guia_ControlX AS X1
                ON Arbitraje_Etiqueta.FK_GUIA_X1 = X1.ID_GUIA
                AND Arbitraje_Etiqueta.FK_GRUPO_ACCIONES = X1.FK_GRUPO_ACCIONES
          INNER JOIN Guia_ControlX AS X2
                ON Arbitraje_Etiqueta.FK_GUIA_X2 = X2.ID_GUIA
                AND Arbitraje_Etiqueta.FK_GRUPO_ACCIONES = X2.FK_GRUPO_ACCIONES
           INNER JOIN Guia_ControlY AS Y1
                ON Arbitraje_Etiqueta.FK_GUIA_Y1 = Y1.ID_GUIA
                AND Arbitraje_Etiqueta.FK_GRUPO_ACCIONES = Y1.FK_GRUPO_ACCIONES
          INNER JOIN Guia_ControlY AS Y2
                ON Arbitraje_Etiqueta.FK_GUIA_Y2 = Y2.ID_GUIA
                AND Arbitraje_Etiqueta.FK_GRUPO_ACCIONES = Y2.FK_GRUPO_ACCIONES;
                    

###############################################################################
--
-- Vista final para obtener la lista de etiquetas a mostrar.
--

CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER 
       VIEW Arbitraje_VistaAuxEtiquetas AS 

    SELECT ID_PARTIDO,
           -- Justificación del texto. Si hay que reflejar el campo en horizontal,
           -- cambiamos su justificación. Por ejemplo, si es justificar a la
           -- izquierda, en caso de reflexión, lo justificamos a la derecha.
           CASE 
               WHEN Arbitraje_ZonaAcciones.reflejar_x THEN
               CASE 
                   WHEN Etiquetas.justificacion = "w" THEN "e"
                   WHEN Etiquetas.justificacion = "e" THEN "w"
                   ELSE Etiquetas.justificacion
               END 
               ELSE Etiquetas.justificacion 
           END AS justificacion,   
           -- Estilo del control:
           Arbitraje_EstiloFuente.nombre_fuente,
           Arbitraje_EstiloFuente.tamano_fuente,
           Arbitraje_EstiloFuente.estilo_fuente,
           Arbitraje_EstiloFuente.color_fuente,
           Partido_Lado.color_h AS color_h_fondo,
           Partido_Lado.color_s AS color_s_fondo,
           Etiquetas.color_v AS color_v_fondo,
           -- Posición de la etiqueta.
           CASE 
               WHEN Arbitraje_ZonaAcciones.reflejar_x THEN 
                   Guia_GrupoX.posicion - Etiquetas.etiqueta_x - Etiquetas.etiqueta_w 
               ELSE Guia_GrupoX.posicion + Etiquetas.etiqueta_x 
           END AS pos_x,
           Guia_GrupoY.posicion + Etiquetas.etiqueta_y AS pos_y,
           Etiquetas.etiqueta_w AS ancho,
           Etiquetas.etiqueta_h AS alto,                   
           Etiquetas.etiqueta_d AS desplazamiento,
           
           Etiquetas.tipo AS tipo,
           Etiquetas.valor AS valor
     
      FROM Arbitraje_VistaAuxGuiasEtiquetas AS Etiquetas
           JOIN Arbitraje_ZonaAcciones
                ON Etiquetas.FK_GRUPO_ACCIONES = Arbitraje_ZonaAcciones.FK_GRUPO_ACCIONES
                AND (Etiquetas.FK_LADO = Arbitraje_ZonaAcciones.FK_LADO OR
                     Etiquetas.FK_LADO IS NULL)

           INNER JOIN Arbitraje_EstiloFuente
                ON Etiquetas.FK_ESTILO_FUENTE = 
                   Arbitraje_EstiloFuente.ID_ESTILO_FUENTE
           INNER JOIN Partido_Lado
                ON Arbitraje_ZonaAcciones.FK_LADO = Partido_Lado.ID_LADO
                
          INNER JOIN Guia_GrupoX
                ON Arbitraje_ZonaAcciones.FK_OFFSET_X = Guia_GrupoX.ID_GUIA
          INNER JOIN Guia_GrupoY
                ON Arbitraje_ZonaAcciones.FK_OFFSET_Y = Guia_GrupoY.ID_GUIA;           

###############################################################################
###############################################################################
COMMIT;