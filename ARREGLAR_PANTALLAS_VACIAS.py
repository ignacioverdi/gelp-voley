# -*- coding: utf-8 -*-
"""
ARREGLAR_PANTALLAS_VACIAS.py
============================

Arregla las pantallas que pueden quedar vacias porque leen sus datos antes
de que lleguen.

── EL PROBLEMA ───────────────────────────────────────────────────────────────
Muchas pantallas hacen esto al abrir:

    var DATA = window.EQUIPO_DATA || null;

Esa linea corre UNA sola vez. Si en ese instante el archivo cifrado todavia
no termino de descifrarse, DATA queda vacio — y aunque los datos lleguen un
segundo despues, la pantalla ya no los mira. Queda en blanco.

Al entrenador casi no le pasa. Al JUGADOR si: pide ademas su rol, asi que
todo lo demas llega un poco mas tarde y pierde la carrera.

Y empeora a medida que se cargan mas entrenamientos: archivos mas grandes,
mas tiempo para descifrar, mas chances de perder.

── QUE HACE ──────────────────────────────────────────────────────────────────
Agrega un vigia liviano: si los datos aparecen despues, actualiza la variable
y vuelve a dibujar la pantalla. Se apaga solo a los 8 segundos.

No es un observador de los que trabaron los telefonos: no vigila la pantalla,
solo mira una variable cada 200 ms y se detiene apenas la encuentra.

── COMO SE USA ───────────────────────────────────────────────────────────────
    Copiar a la carpeta del club y hacer doble clic.
    De cada pantalla tocada queda una copia .antes-vacia
"""

import io
import os
import re
import shutil
import sys
import glob

AQUI = os.path.dirname(os.path.abspath(__file__))

PATRON = re.compile(r'var\s+(\w+)\s*=\s*window\.(\w+_DATA)\s*\|\|[^;]*;')

VIGIA = '''

/* ── LOS DATOS PUEDEN LLEGAR DESPUES ────────────────────────────────────
   La linea de arriba corre UNA vez al cargar. Si el archivo cifrado
   todavia no termino de descifrarse, la pantalla quedaba vacia para
   siempre, aunque los datos llegaran un instante despues.

   Este vigia mira la variable cada 200 ms. Apenas aparece, la actualiza,
   redibuja la pantalla y se apaga. A los 8 segundos se rinde solo. */
(function esperarDatos(){
  var _i = 0, _t = setInterval(function(){
    if(++_i > 40){ clearInterval(_t); return; }
    if(window.%(VAR)s && window.%(VAR)s !== %(LOCAL)s){
      %(LOCAL)s = window.%(VAR)s;
      clearInterval(_t);
      try{ if(typeof render==='function') render();
           else if(typeof pintar==='function') pintar();
           else if(typeof dibujar==='function') dibujar();
           else if(typeof cargar==='function') cargar();
           else if(typeof init==='function') init(); }catch(e){}
    }
  }, 200);
})();'''


def revisar(aplicar):
    tocadas = []
    for ruta in sorted(glob.glob(os.path.join(AQUI, '*.html'))):
        f = os.path.basename(ruta)
        try:
            s = io.open(ruta, encoding='utf-8', errors='replace').read()
        except Exception:
            continue
        if 'esperarDatos' in s:
            continue
        m = PATRON.search(s)
        if not m:
            continue
        # devicePixelRatio y parecidos no son datos del club
        if not m.group(2).endswith('_DATA'):
            continue
        tocadas.append((f, m.group(2)))
        if aplicar:
            if not os.path.exists(ruta + '.antes-vacia'):
                try:
                    shutil.copy2(ruta, ruta + '.antes-vacia')
                except Exception:
                    pass
            nuevo = s.replace(m.group(0),
                              m.group(0) + VIGIA % {'VAR': m.group(2), 'LOCAL': m.group(1)}, 1)
            io.open(ruta, 'w', encoding='utf-8').write(nuevo)
    return tocadas


def main():
    print()
    print('  ' + '=' * 62)
    print('     PANTALLAS QUE PUEDEN QUEDAR VACIAS')
    print('  ' + '=' * 62)
    print()

    if not glob.glob(os.path.join(AQUI, '*.html')):
        print('     No encontre pantallas en esta carpeta.')
        print('     Copia este programa a la carpeta del club.')
        print()
        return 1

    pend = revisar(aplicar=False)

    if not pend:
        print('  ' + '-' * 62)
        print('     Ninguna pantalla tiene ese problema.')
        print()
        return 0

    print('     Se van a arreglar %d pantalla(s):' % len(pend))
    print()
    for f, v in pend:
        print('       · %-26s (%s)' % (f, v))
    print()
    print('     De cada una queda una copia .antes-vacia')
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
    hechas = revisar(aplicar=True)
    for f, v in hechas:
        print('       arreglada: ' + f)

    print()
    print('  ' + '-' * 62)
    print('     Listo. Corre ahora REVISAR_ANTES_DE_PUBLICAR.py')
    print('     y si dice TODO EN ORDEN, publica.')
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
