# -*- coding: utf-8 -*-
"""
ARREGLAR_DORSALES_DUPLICADOS.py
===============================

Junta las jugadoras que aparecen dos veces en las listas de analisis.

── EL PROBLEMA ───────────────────────────────────────────────────────────────
En los heat maps y otras pantallas, la misma jugadora aparece dos veces:

    #6 · Oyola Martina (48)
    #6 · Oyola (48)            <- la misma
    #7 · Gomez Zoe (46)
    #7 · Gomez (46)            <- la misma

La causa: el dorsal llega en dos formatos distintos, "6" y "06", segun como
lo escribio el scout en cada .dvw. El codigo agrupa asi:

    if(!PLAYERS[a.num]) PLAYERS[a.num] = {...}

Y para el, "6" y "06" son dos jugadoras diferentes.

── LA SOLUCION ───────────────────────────────────────────────────────────────
Se normaliza el dorsal a numero antes de agrupar: "06" y "6" pasan a ser 6.
Asi las acciones de las dos formas se suman en una sola jugadora.

Tambien se conserva el nombre mas completo de los dos: entre "Oyola" y
"Oyola Martina", queda el segundo.
"""

import io
import os
import re
import shutil
import sys
import glob

AQUI = os.path.dirname(os.path.abspath(__file__))

VIEJO = "if(!PLAYERS[a.num])PLAYERS[a.num]={num:a.num,name:a.name,acts:[]}; PLAYERS[a.num].acts.push(a);"

NUEVO = ("""/* El dorsal puede venir como "6" o como "06" segun el .dvw. Sin
           normalizarlo, la misma jugadora aparecia dos veces en la lista.
           Se agrupa por numero, y se queda el nombre mas completo. */
        var _n = parseInt(a.num, 10);
        if(isNaN(_n)) _n = a.num;
        if(!PLAYERS[_n]) PLAYERS[_n]={num:_n, name:a.name, acts:[]};
        else if((a.name||'').length > (PLAYERS[_n].name||'').length) PLAYERS[_n].name = a.name;
        PLAYERS[_n].acts.push(a);""")


def main():
    print()
    print('  ' + '=' * 62)
    print('     JUNTAR LAS JUGADORAS DUPLICADAS')
    print('  ' + '=' * 62)
    print()

    pendientes = []
    for ruta in sorted(glob.glob(os.path.join(AQUI, '*.html'))):
        s = io.open(ruta, encoding='utf-8', errors='replace').read()
        if 'PLAYERS[a.num]' in s:
            pendientes.append(os.path.basename(ruta))

    if not pendientes:
        print('  ' + '-' * 62)
        print('     Ninguna pantalla tiene ese problema.')
        print()
        return 0

    print('     Pantallas a arreglar (%d):' % len(pendientes))
    print()
    for f in pendientes:
        print('       · ' + f)
    print()
    print('     Ejemplo de lo que se corrige:')
    print()
    print('       antes:  #6 Oyola Martina (48)  y  #6 Oyola (48)')
    print('       ahora:  #6 Oyola Martina (96)')
    print()

    if '--si' in sys.argv:
        print('     Aplico? (S/N): S   (automatico)')
    else:
        try:
            r = input('     Aplico? (S/N): ').strip().lower()
        except Exception:
            r = 'n'
        if r not in ('s', 'si', 'y'):
            print()
            print('     No toque nada.')
            print()
            return 0

    print()
    for f in pendientes:
        ruta = os.path.join(AQUI, f)
        s = io.open(ruta, encoding='utf-8', errors='replace').read()
        orig = s

        s = s.replace(VIEJO, NUEVO)
        # variantes con espacios distintos
        if s == orig:
            m = re.search(r"if\(!PLAYERS\[a\.num\]\)\s*PLAYERS\[a\.num\]=\{num:a\.num,\s*name:a\.name,\s*acts:\[\]\};\s*PLAYERS\[a\.num\]\.acts\.push\(a\);", s)
            if m:
                s = s.replace(m.group(0), NUEVO, 1)

        if s == orig:
            print('       %-24s sin cambios (otra forma)' % f)
            continue

        resp = ruta + '.antes-dorsales'
        if not os.path.exists(resp):
            try:
                shutil.copy2(ruta, resp)
            except Exception:
                pass
        io.open(ruta, 'w', encoding='utf-8').write(s)
        print('       %-24s listo' % f)

    print()
    print('  ' + '-' * 62)
    print('     Listo. Corre PUBLICAR.bat')
    print()
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    finally:
        if '--si' not in sys.argv:
            try:
                input('  Enter para cerrar...')
            except Exception:
                pass
