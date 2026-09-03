# -*- coding: utf-8 -*-
"""
REPARAR_HM_ARMADOR.py
=====================

Repara hm_armador.html: el cambio anterior dejo una llave de mas y la
pantalla quedo sin datos.

── QUE PASO ──────────────────────────────────────────────────────────────────
Al reemplazar el bloque que lee las armadoras, el patron capturo una llave
que pertenecia al codigo de alrededor. Quedo asi:

        setters[...] = ...;
      };  }          <- esta de mas
    return { rivals: ...

Eso rompe el JavaScript: la pantalla no llega a armar sus datos y el
selector de armadoras sale vacio.

── QUE HACE ──────────────────────────────────────────────────────────────────
Saca la llave sobrante. El resto del cambio —leer las tres armadoras— queda
como estaba, que era correcto.
"""

import io
import os
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
ARCH = os.path.join(AQUI, 'hm_armador.html')

MALO = """        setters[String(td.setter.num)]={name:td.setter.name,num:td.setter.num,s:td.setter.s};
      }; }"""

BUENO = """        setters[String(td.setter.num)]={name:td.setter.name,num:td.setter.num,s:td.setter.s};
      }"""


def main():
    print()
    print('  ' + '=' * 62)
    print('     REPARAR LA PANTALLA DE ARMADO')
    print('  ' + '=' * 62)
    print()

    if not os.path.exists(ARCH):
        print('     No encontre hm_armador.html en esta carpeta.')
        print()
        return 1

    s = io.open(ARCH, encoding='utf-8', errors='replace').read()

    if MALO not in s:
        if 'td.setters && td.setters.length' in s:
            print('  ' + '-' * 62)
            print('     El archivo ya esta bien.')
            print()
            return 0
        print('     No encontre el error esperado.')
        print('     Si tenes el respaldo hm_armador.html.antes-armadoras,')
        print('     renombralo a hm_armador.html y avisame.')
        print()
        return 1

    print('     Encontre la llave de mas. Se saca y queda:')
    print()
    print('           } else if(td.setter && td.setter.num){')
    print('             setters[...] = ...;')
    print('           }')
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

    s = s.replace(MALO, BUENO, 1)

    resp = ARCH + '.antes-reparar'
    if not os.path.exists(resp):
        try:
            shutil.copy2(ARCH, resp)
        except Exception:
            pass
    io.open(ARCH, 'w', encoding='utf-8').write(s)

    print()
    print('       hm_armador.html          reparado')
    print()
    print('  ' + '-' * 62)
    print('     Corre PUBLICAR.bat')
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
