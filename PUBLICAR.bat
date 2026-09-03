@echo off
chcp 65001 >nul
setlocal

REM  PUBLICAR.bat  -  cifra los datos y publica.
REM
REM  Cuando usarlo:
REM    - cargaste links de video
REM    - editaste el plantel
REM    - corregiste una pantalla
REM
REM  Si agregaste un partido .dvw, usa HACER_TODO.bat en su lugar.
REM
REM  El paso de cifrar no se puede saltear: la app lee los datos
REM  cifrados, asi que un archivo en texto plano no lo ve nadie.

echo.
echo   ==============================================================
echo      PUBLICAR
echo   ==============================================================
echo.

if not exist "cifrar_datos.py" (
  echo      No encontre cifrar_datos.py
  echo      No parece la carpeta de un club.
  echo.
  pause
  exit /b 1
)

echo      Se van a hacer tres cosas:
echo.
echo        1. revisar que no haya nada roto
echo        2. cifrar los datos
echo        3. publicar
echo.
echo      Si agregaste un partido .dvw, cerra esto y usa HACER_TODO.
echo.

set /p RESP="     Sigo? (S/N): "
if /i not "%RESP%"=="S" (
  echo.
  echo      No toque nada.
  echo.
  pause
  exit /b 0
)

echo.
echo   --------------------------------------------------------------
echo      Revisando...
echo.

if exist "REVISAR_ANTES_DE_PUBLICAR.py" (
  python REVISAR_ANTES_DE_PUBLICAR.py --si
  if errorlevel 1 (
    echo.
    echo      FRENO: la revision encontro problemas.
    echo      Arreglalos y volve a intentar.
    echo.
    pause
    exit /b 1
  )
)

echo.
echo   --------------------------------------------------------------
echo      Cifrando...
echo.

python cifrar_datos.py
if errorlevel 1 (
  echo.
  echo      ERROR al cifrar. Freno para no publicar algo roto.
  echo.
  pause
  exit /b 1
)

echo.
echo   --------------------------------------------------------------
echo      Publicando...
echo.

git --version >nul 2>&1
if errorlevel 1 (
  echo      No encuentro Git. Instalalo desde git-scm.com
  echo.
  pause
  exit /b 1
)

git add -A
git commit -m "Actualizacion %DATE%"
git pull --no-rebase --no-edit -X ours
git push
if errorlevel 1 (
  echo.
  echo      ERROR al publicar. Fijate si tenes internet.
  echo.
  pause
  exit /b 1
)

echo.
echo   --------------------------------------------------------------
echo      Listo.
echo.
pause
