# -*- coding: utf-8 -*-
"""
ARREGLAR_PLANTEL_CLUB.py
========================

Hace que TODAS las pantallas encuentren el plantel del club.

── EL PROBLEMA ───────────────────────────────────────────────────────────────
El plantel de cada club vive en un archivo con su nombre:

    plantel_nafels.js   ->  window.PLANTEL_NAFELS
    plantel_gelp.js     ->  window.PLANTEL_GELP

Pero varias pantallas lo buscan con un nombre generico —PLANTEL_CLUB— que no
existe en ningun club. En el verificador aparecia asi:

    baggerone.html pide "plantel_club.js" y no existe
    panel_vivo.html pide "plantel_club.js" y no existe

No rompia nada porque estan protegidas con onerror, pero significa que esas
pantallas se quedaban SIN la lista de jugadores: mostraban solo a los que
salen de los partidos, o directamente nada.

── QUE HACE ──────────────────────────────────────────────────────────────────
Busca el archivo de plantel real del club y hace que todas las pantallas lo
carguen y lo busquen con el nombre correcto.

De cada pantalla tocada queda una copia .antes-plantel
"""

import io
import os
import re
import shutil
import sys
import glob

AQUI = os.path.dirname(os.path.abspath(__file__))


def encontrar_plantel():
    """Devuelve (archivo, variable) del plantel real del club."""
    for cand in sorted(glob.glob(os.path.join(AQUI, 'plantel_*.js'))):
        n = os.path.basename(cand)
        if 'desde_dvw' in n or n == 'plantel_club.js':
            continue
        t = io.open(cand, encoding='utf-8', errors='replace').read()
        m = re.search(r'window\.(\w+)\s*=', t)
        if m:
            return n, m.group(1)
    return None, None


def main():
    print()
    print('  ' + '=' * 62)
    print('     QUE TODAS LAS PANTALLAS ENCUENTREN EL PLANTEL')
    print('  ' + '=' * 62)
    print()

    archivo, variable = encontrar_plantel()
    if not archivo:
        print('     No encontre el archivo de plantel del club.')
        print('     Deberia llamarse plantel_<club>.js')
        print()
        return 1

    print('     El plantel de este club:')
    print('       archivo:  %s' % archivo)
    print('       variable: window.%s' % variable)
    print()

    # que pantallas no lo encuentran
    pendientes = []
    for ruta in sorted(glob.glob(os.path.join(AQUI, '*.html'))):
        f = os.path.basename(ruta)
        s = io.open(ruta, encoding='utf-8', errors='replace').read()

        # Una pantalla puede MENCIONAR la variable correcta y aun asi cargar
        # el archivo equivocado. Es lo que pasaba en historial_voley: esperaba
        # PLANTEL_GELP pero cargaba plantel_club.js, que no existe.
        # Por eso se miran las dos cosas por separado.
        carga_mal = 'plantel_club.js' in s
        busca_mal = 'PLANTEL_CLUB' in s and variable not in s
        if carga_mal or busca_mal:
            pendientes.append(f)

    if not pendientes:
        print('  ' + '-' * 62)
        print('     Todas las pantallas ya lo encuentran.')
        print()
        return 0

    print('     Pantallas que NO lo encuentran (%d):' % len(pendientes))
    for f in pendientes:
        print('       · ' + f)
    print()

    if '--si' in sys.argv:
        r = 's'
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

        # 1) cargar el archivo correcto
        s = s.replace('<script src="plantel_club.js"',
                      '<script src="' + archivo + '"')

        # 2) buscar la variable correcta. Se agrega, no se reemplaza: si una
        #    pantalla busca varios nombres, que siga buscando todos.
        s = re.sub(r"'PLANTEL_CLUB'", "'" + variable + "','PLANTEL_CLUB'", s)
        s = re.sub(r'"PLANTEL_CLUB"', '"' + variable + '","PLANTEL_CLUB"', s)
        s = re.sub(r'window\.PLANTEL_CLUB\b',
                   '(window.' + variable + ' || window.PLANTEL_CLUB)', s)

        if s == orig:
            print('       %-24s sin cambios (otra forma)' % f)
            continue

        respaldo = ruta + '.antes-plantel'
        if not os.path.exists(respaldo):
            try:
                shutil.copy2(ruta, respaldo)
            except Exception:
                pass
        io.open(ruta, 'w', encoding='utf-8').write(s)
        print('       %-24s listo' % f)

    print()
    print('  ' + '-' * 62)
    print('     Ahora corre REVISAR_ANTES_DE_PUBLICAR.py y publica.')
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
