# -*- coding: utf-8 -*-
"""
NOMBRES_CORTOS.py
=================

Que los rivales se muestren con el nombre corto.

── EL PROBLEMA ───────────────────────────────────────────────────────────────
Los .dvw traen el nombre completo del club, y asi se muestra en la app:

    CLUB SOCIAL, DEPORTIVO Y CULTURAL ARGENTINO DE CASTELAR
    CLUB ATLETICO SAN LORENZO DE ALMAGRO
    UNIVERSIDAD NACIONAL DE TRES DE FEBRERO

No entran en pantalla, se cortan, y se leen mal.

── LA SOLUCION ───────────────────────────────────────────────────────────────
Una tabla con el nombre corto de cada club —el que usa todo el mundo— que el
motor aplica al guardar los datos:

    Castelar  ·  San Lorenzo  ·  Untref  ·  Ferro  ·  Boca

Los clubes que no esten en la tabla al menos pierden el "Club" del principio.
"""

import io
import os
import re
import shutil
import sys
import glob

AQUI = os.path.dirname(os.path.abspath(__file__))

TABLA = '''

# ── NOMBRES CORTOS DE LOS CLUBES ──────────────────────────────────────────
# Los .dvw traen el nombre completo del club. En pantalla no entra y se lee
# mal, asi que se guarda el nombre corto: el que usa todo el mundo.
NOMBRE_CORTO = {
    'club social, deportivo y cultural argentino de castelar': 'Castelar',
    'club atletico san lorenzo de almagro':                    'San Lorenzo',
    'club atletico boca juniors':                              'Boca',
    'club atletico river plate':                               'River',
    'club atletico velez sarsfield':                           'Velez',
    'club ferro carril oeste':                                 'Ferro',
    'club gimnasia y esgrima la plata':                        'GELP',
    'club estudiantes de la plata':                            'Estudiantes',
    'club banco provincia':                                    'Banco Provincia',
    'universidad nacional de la matanza':                      'UNLaM',
    'universidad nacional de tres de febrero':                 'Untref',
    'instituto educativo san gregorio "el iluminador"':        'San Gregorio',
    'instituto educativo san gregorio el iluminador':          'San Gregorio',
}


def _sin_tildes(t):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD', t)
                   if unicodedata.category(c) != 'Mn')


def nombre_corto(nombre):
    """El nombre corto del club, o el original si no esta en la tabla."""
    if not nombre:
        return nombre
    clave = _sin_tildes(nombre.strip().lower())
    for k, v in NOMBRE_CORTO.items():
        if _sin_tildes(k) == clave:
            return v
    # No esta en la tabla: al menos se saca el "Club " del principio
    limpio = re.sub(r'^(club|instituto educativo|universidad nacional de la|'
                    r'universidad nacional de|universidad nacional)\\s+',
                    '', nombre.strip(), flags=re.I)
    return limpio.strip() or nombre

'''


def main():
    print()
    print('  ' + '=' * 62)
    print('     NOMBRES CORTOS DE LOS EQUIPOS')
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
        if "'name':team" in s.replace(' ', '') and 'NOMBRE_CORTO' not in s:
            tocar.append(os.path.basename(m))

    if not tocar:
        print('  ' + '-' * 62)
        print('     Ya estaba puesto (o el motor guarda los nombres de otra forma).')
        print()
        return 0

    print('     Motores a corregir:')
    for f in tocar:
        print('       · ' + f)
    print()
    print('     Ejemplo:')
    print('       antes:  CLUB SOCIAL, DEPORTIVO Y CULTURAL ARGENTINO DE CASTELAR')
    print('       ahora:  Castelar')
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

        # la tabla, despues del ultimo import
        ult = 0
        for mm in re.finditer(r'^(import |from )[^\n]*\n', s, re.M):
            ult = mm.end()
        s = s[:ult] + TABLA + s[ult:]

        # aplicarla donde se guarda el nombre
        antes = s
        s = re.sub(r"\{'name'\s*:\s*team\s*,", "{'name':nombre_corto(team),", s)
        s = re.sub(r"'name'\s*:\s*team\s*\}", "'name':nombre_corto(team)}", s)

        if s == antes:
            print('       %-30s la tabla si, el uso no (revisar)' % f)
        else:
            print('       %-30s listo' % f)

        resp = ruta + '.antes-nombres'
        if not os.path.exists(resp):
            try:
                shutil.copy2(ruta, resp)
            except Exception:
                pass
        io.open(ruta, 'w', encoding='utf-8').write(s)

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
