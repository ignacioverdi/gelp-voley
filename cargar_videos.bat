@echo off
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
REM ============================================
REM   CARGAR VIDEOS - Convierte el Excel a videos.js
REM ============================================
title Cargar Videos - Game Plan

echo.
echo  ========================================
echo    CARGANDO VIDEOS AL GAME PLAN
echo  ========================================
echo.

REM Detecta automaticamente el Excel de videos en la carpeta
set EXCEL=
if exist videos_gelp.xlsx set EXCEL=videos_gelp.xlsx
if exist videos_gelp.xlsx set EXCEL=videos_gelp.xlsx

if "%EXCEL%"=="" (
    echo  [ERROR] No encontre ningun archivo videos_gelp.xlsx ni videos_gelp.xlsx
    echo  Asegurate de que el .bat este en la misma carpeta que el Excel.
    echo.
    pause
    exit /b
)

echo  Excel encontrado: %EXCEL%
echo  Procesando...
echo.

python build_videos.py %EXCEL%

echo.
if exist videos.js (
    echo  ========================================
    echo    LISTO! Se genero videos.js
    echo  ========================================
    echo.
    echo  Ahora subi el archivo videos.js a GitHub
    echo  junto al game_plan.html
) else (
    echo  [ERROR] No se genero videos.js - revisa los mensajes de arriba
)
echo.
pause
