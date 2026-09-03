# -*- coding: utf-8 -*-
"""
ARMADORAS_TRES.py
=================

Que aparezcan las TRES armadoras del equipo.

── EL PROBLEMA ───────────────────────────────────────────────────────────────
En el heat map de armado aparecia una sola:

    #5 Bicecci Valentina (286 arm.)

Pero en los .dvw armaron tres:

    #5  BICECCI       180
    #13 COSULICH       58
    #10 SILBERSTEIN    40

El motor cortaba la lista en dos:

    ranked = sorted(setters_rallies.items(), key=...)[:2]

── POR QUE TRES Y NO MAS ─────────────────────────────────────────────────────
Ningun equipo tiene mas de tres armadoras. Poner un tope mas alto haria que
apareciera cualquier jugadora de campo que haya armado unas pocas pelotas
en una emergencia, y ensuciaria la lista.

Tres es el numero justo: entran las armadoras de verdad y ninguna mas.
"""

import io
import os
import re
import shutil
import sys
import glob

AQUI = os.path.dirname(os.path.abspath(__file__))


def main():
    print()
    print('  ' + '=' * 62)
    print('     LAS TRES ARMADORAS')
    print('  ' + '=' * 62)
    print()

    motores = [f for f in glob.glob(os.path.join(AQUI, 'update_db*.py'))]
    if not motores:
        print('     No encontre los motores update_db*.py')
        print()
        return 1

    tocar = []
    for m in motores:
        s = io.open(m, encoding='utf-8', errors='replace').read()
        if 'setters_rallies.items(), key=lambda x:-len(x[1]))[:2]' in s:
            tocar.append(os.path.basename(m))

    if not tocar:
        print('  ' + '-' * 62)
        print('     Ya estaba en tres (o el corte tiene otra forma).')
        print()
        return 0

    print('     Motores a corregir:')
    for f in tocar:
        print('       · ' + f)
    print()
    print('     El corte pasa de 2 armadoras a 3.')
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
    for f in tocar:
        ruta = os.path.join(AQUI, f)
        s = io.open(ruta, encoding='utf-8', errors='replace').read()
        n = s.count('setters_rallies.items(), key=lambda x:-len(x[1]))[:2]')
        s = s.replace('setters_rallies.items(), key=lambda x:-len(x[1]))[:2]',
                      'setters_rallies.items(), key=lambda x:-len(x[1]))[:3]')
        # y el tope de detectar_armadores, por las dudas
        s = s.replace('detectar_armadores(content, pfx, 4,',
                      'detectar_armadores(content, pfx, 3,')
        s = s.replace('detectar_armadores(content, pfx, 2,',
                      'detectar_armadores(content, pfx, 3,')

        resp = ruta + '.antes-armadoras'
        if not os.path.exists(resp):
            try:
                shutil.copy2(ruta, resp)
            except Exception:
                pass
        io.open(ruta, 'w', encoding='utf-8').write(s)
        print('       %-30s listo (%d corte/s)' % (f, n))

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
