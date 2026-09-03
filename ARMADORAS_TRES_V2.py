# -*- coding: utf-8 -*-
"""
ARMADORAS_TRES_V2.py
====================

Que la pantalla de armado muestre las TRES armadoras.

── POR QUE HIZO FALTA UNA SEGUNDA VERSION ────────────────────────────────────
El corte de armadoras aparece en TRES lugares distintos del motor, escritos
de forma parecida pero no igual:

    setters_rallies.items(), ...)[:2]     <- lo corrigio la version anterior
    rallies.items(), ...)[:2]             <- ESTE quedo afuera

El ultimo es el que arma la pagina armador_<club>.html, que es de donde la
pantalla lee sus datos. Por eso LIGA_DATA ya tenia las tres armadoras pero
en pantalla seguia apareciendo una sola.

── QUE HACE ──────────────────────────────────────────────────────────────────
Cambia los tres cortes a 3, en todos los motores.

Tres es el numero justo: ningun equipo tiene mas armadoras, y un tope mas
alto haria aparecer a cualquier jugadora de campo que armo unas pelotas en
una emergencia.
"""

import io
import os
import re
import shutil
import sys
import glob

AQUI = os.path.dirname(os.path.abspath(__file__))

PATRON = re.compile(r'(sorted\(\s*(?:setters_)?rallies\.items\(\),\s*key=lambda x:-len\(x\[1\]\)\s*\))\[:2\]')


def main():
    print()
    print('  ' + '=' * 62)
    print('     LAS TRES ARMADORAS (segunda pasada)')
    print('  ' + '=' * 62)
    print()

    motores = sorted(glob.glob(os.path.join(AQUI, 'update_db*.py')))
    if not motores:
        print('     No encontre los motores update_db*.py')
        print()
        return 1

    tocar = []
    for m in motores:
        s = io.open(m, encoding='utf-8', errors='replace').read()
        n = len(PATRON.findall(s))
        if n:
            tocar.append((os.path.basename(m), n))

    if not tocar:
        print('  ' + '-' * 62)
        print('     Ya estan todos los cortes en 3.')
        print()
        return 0

    print('     Cortes que quedaron en 2:')
    print()
    for f, n in tocar:
        print('       · %-32s %d corte/s' % (f, n))
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
    for f, n in tocar:
        ruta = os.path.join(AQUI, f)
        s = io.open(ruta, encoding='utf-8', errors='replace').read()
        s = PATRON.sub(r'\1[:3]', s)

        resp = ruta + '.antes-arm3'
        if not os.path.exists(resp):
            try:
                shutil.copy2(ruta, resp)
            except Exception:
                pass
        io.open(ruta, 'w', encoding='utf-8').write(s)
        print('       %-32s listo (%d)' % (f, n))

    print()
    print('  ' + '-' * 62)
    print('     Listo. Corre HACER_TODO.bat')
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
