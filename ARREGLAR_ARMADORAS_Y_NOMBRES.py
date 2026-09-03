# -*- coding: utf-8 -*-
"""
ARREGLAR_ARMADORAS_Y_NOMBRES.py
===============================

Dos correcciones pedidas:

  1. QUE APAREZCAN TODAS LAS ARMADORAS
  2. NOMBRES DE EQUIPO CORTOS Y LEGIBLES


── 1. LAS ARMADORAS ──────────────────────────────────────────────────────────

El motor tomaba solo DOS armadoras por partido:

    setters = detectar_armadores(content, pfx, 2, ...)

En GELP armaron tres:

    #5  BICECCI       180 armados
    #13 COSULICH       58
    #10 SILBERSTEIN    40

Con el tope en 2, la tercera quedaba afuera y no aparecia en el heat map
de armado. Ahora toma hasta cuatro: entran las suplentes que armaron poco,
y las que no armaron nada siguen sin aparecer porque no tienen datos.


── 2. LOS NOMBRES DE EQUIPO ──────────────────────────────────────────────────

Los rivales se mostraban con el nombre completo del club:

    CLUB SOCIAL, DEPORTIVO Y CULTURAL ARGENTINO DE CASTELAR
    CLUB ATLETICO SAN LORENZO DE ALMAGRO
    CLUB FERRO CARRIL OESTE

No entran en pantalla y se leen mal. Ahora se muestra el nombre corto, el
que usa todo el mundo:

    CASTELAR  ·  SAN LORENZO  ·  FERRO

Se agrega una tabla de nombres cortos que el motor usa al generar los datos.
"""

import io
import os
import re
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
MOTOR = os.path.join(AQUI, 'update_db.py')

CORTOS = '''
# ── NOMBRES CORTOS DE LOS CLUBES ──────────────────────────────────────────
# Los .dvw traen el nombre completo —"Club Social, Deportivo y Cultural
# Argentino de Castelar"— que no entra en pantalla y se lee mal.
# Aca esta como lo llama todo el mundo.
NOMBRE_CORTO = {
    'club social, deportivo y cultural argentino de castelar': 'Castelar',
    'club atletico san lorenzo de almagro':                    'San Lorenzo',
    'club atlético san lorenzo de almagro':                    'San Lorenzo',
    'club ferro carril oeste':                                 'Ferro',
    'club atletico boca juniors':                              'Boca',
    'club atlético boca juniors':                              'Boca',
    'club atletico river plate':                               'River',
    'club atlético river plate':                               'River',
    'club gimnasia y esgrima la plata':                        'GELP',
    'club banco provincia':                                    'Banco Provincia',
    'universidad nacional de la matanza':                      'UNLaM',
    'universidad nacional de tres de febrero':                 'Untref',
    'instituto educativo san gregorio "el iluminador"':        'San Gregorio',
    'instituto educativo san gregorio el iluminador':          'San Gregorio',
    'club atletico velez sarsfield':                           'Velez',
    'club atlético vélez sarsfield':                           'Velez',
    'club estudiantes de la plata':                            'Estudiantes',
}


def nombre_corto(nombre):
    """Devuelve el nombre corto del club, o el original si no esta en la tabla."""
    if not nombre:
        return nombre
    n = NOMBRE_CORTO.get(nombre.strip().lower())
    if n:
        return n
    # Si no esta en la tabla, al menos sacamos el "Club " del principio
    limpio = re.sub(r'^(club|instituto|universidad nacional)\\s+', '', nombre.strip(), flags=re.I)
    return limpio if limpio else nombre

'''


def main():
    print()
    print('  ' + '=' * 62)
    print('     ARMADORAS Y NOMBRES DE EQUIPO')
    print('  ' + '=' * 62)
    print()

    if not os.path.exists(MOTOR):
        print('     No encontre update_db.py en esta carpeta.')
        print()
        return 1

    s = io.open(MOTOR, encoding='utf-8', errors='replace').read()

    hechas = []
    faltan = []

    # ── 1. armadoras ────────────────────────────────────────────────────
    if 'detectar_armadores(content, pfx, 2,' in s:
        faltan.append('subir el tope de armadoras de 2 a 4')
    elif 'detectar_armadores(content, pfx, 4,' in s:
        hechas.append('las armadoras ya estaban en 4')

    # ── 2. nombres cortos ───────────────────────────────────────────────
    if 'NOMBRE_CORTO' in s:
        hechas.append('los nombres cortos ya estaban')
    else:
        faltan.append('agregar la tabla de nombres cortos')

    if hechas:
        print('     Ya estaba:')
        for x in hechas:
            print('       · ' + x)
        print()

    if not faltan:
        print('  ' + '-' * 62)
        print('     No hay nada que hacer.')
        print()
        return 0

    print('     Se va a hacer:')
    for x in faltan:
        print('       · ' + x)
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

    # armadoras: de 2 a 4
    if 'detectar_armadores(content, pfx, 2,' in s:
        # Solo se cambia el numero, sin tocar la indentacion: agregar
        # comentarios ahi rompia el archivo.
        s = s.replace('detectar_armadores(content, pfx, 2,',
                      'detectar_armadores(content, pfx, 4,')
        print('       armadoras: hasta 4 por partido    listo')

    # nombres cortos
    if 'NOMBRE_CORTO' not in s:
        m = re.search(r'^(import |from )', s, re.M)
        if m:
            # despues del ultimo import
            ult = 0
            for mm in re.finditer(r'^(import |from )[^\n]*\n', s, re.M):
                ult = mm.end()
            s = s[:ult] + CORTOS + s[ult:]
            print('       tabla de nombres cortos           listo')

    resp = MOTOR + '.antes-nombres'
    if not os.path.exists(resp):
        try:
            shutil.copy2(MOTOR, resp)
        except Exception:
            pass
    io.open(MOTOR, 'w', encoding='utf-8').write(s)

    print()
    print('  ' + '-' * 62)
    print('     Listo. Ahora corre HACER_TODO.bat')
    print('     (hay que reprocesar: cambio como se leen los partidos)')
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
