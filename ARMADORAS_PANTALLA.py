# -*- coding: utf-8 -*-
"""
ARMADORAS_PANTALLA.py
=====================

Que la pantalla de armado lea las TRES armadoras.

── DONDE ESTABA EL PROBLEMA ──────────────────────────────────────────────────
No era el motor: el motor ya genera las tres.

    LIGA_DATA.teams.gelp.setters  ->  Bicecci 286, Cosulich 58, Silberstein 40

El problema estaba en la pantalla. hm_armador.html hace:

    var setters = {};
    if (td.setter && td.setter.num) {          <- SINGULAR: una sola
        setters[td.setter.num] = td.setter;
    }

Lee "setter" en singular —el titular— cuando los datos estan en "setters",
plural. Por eso aparecia una sola aunque las tres estuvieran generadas.

── QUE HACE ──────────────────────────────────────────────────────────────────
Cambia la pantalla para que recorra la lista completa. Si por alguna razon
no existiera la lista, sigue funcionando con el titular como antes.
"""

import io
import os
import re
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
ARCH = os.path.join(AQUI, 'hm_armador.html')

VIEJO = "var setters={}; if(td.setter && td.setter.num){ setters[String(td.setter.num)]={name:td.setter.name,num:td.setter.num,s:td.setter.s}; }"

NUEVO = ("""var setters={};
      /* Las armadoras estan en td.setters (plural). Antes se leia td.setter
         —el titular, en singular— y por eso aparecia una sola aunque el
         motor generara las tres. */
      if(td.setters && td.setters.length){
        td.setters.forEach(function(sx){
          if(sx && sx.num!=null) setters[String(sx.num)]={name:sx.name,num:sx.num,s:sx.s};
        });
      } else if(td.setter && td.setter.num){
        setters[String(td.setter.num)]={name:td.setter.name,num:td.setter.num,s:td.setter.s};
      }""")


def main():
    print()
    print('  ' + '=' * 62)
    print('     QUE LA PANTALLA LEA LAS TRES ARMADORAS')
    print('  ' + '=' * 62)
    print()

    if not os.path.exists(ARCH):
        print('     No encontre hm_armador.html en esta carpeta.')
        print()
        return 1

    s = io.open(ARCH, encoding='utf-8', errors='replace').read()

    if 'td.setters && td.setters.length' in s:
        print('  ' + '-' * 62)
        print('     Ya estaba puesto.')
        print()
        return 0

    if VIEJO not in s:
        m = re.search(r"var setters=\{\};\s*if\(td\.setter && td\.setter\.num\)\{[^}]*\}", s)
        if not m:
            print('     La pantalla tiene otra forma: no la toco.')
            print()
            return 1
        viejo = m.group(0)
    else:
        viejo = VIEJO

    print('     La pantalla lee td.setter (singular, una sola).')
    print('     Los datos estan en td.setters (plural, las tres).')
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

    s = s.replace(viejo, NUEVO, 1)

    resp = ARCH + '.antes-armadoras'
    if not os.path.exists(resp):
        try:
            shutil.copy2(ARCH, resp)
        except Exception:
            pass
    io.open(ARCH, 'w', encoding='utf-8').write(s)

    print()
    print('       hm_armador.html          listo')
    print()
    print('  ' + '-' * 62)
    print('     Listo. Corre PUBLICAR.bat')
    print('     (no hace falta HACER_TODO: los datos ya estan bien)')
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
