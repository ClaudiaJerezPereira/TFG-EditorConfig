@echo off
REM ============================================================
REM  Equivalente en Windows del script crear_ACCIONES.sh
REM  Crea la base de datos eurobot_ACCIONES a partir de los .sql
REM  IMPORTANTE: ejecutar este .bat desde la carpeta que
REM  contiene los ficheros .sql (SOURCE usa rutas relativas).
REM ============================================================

REM Cambia usuario/contrasena si no usas admin/admin
mariadb -uadmin -padmin --default-character-set=utf8mb4 < crear_ACCIONES.sql

echo.
echo Proceso terminado. Revisa arriba por si hay errores.
pause