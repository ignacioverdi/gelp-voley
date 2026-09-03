# -*- coding: utf-8 -*-
"""
ARREGLAR_VIDEOS_VACIO.py
========================

Hace que "Cargar videos" muestre la lista de partidos.

── EL PROBLEMA ───────────────────────────────────────────────────────────────
Los datos llegan bien —se puede comprobar en la consola: VIDEO_DATA existe—
pero llegan TARDE. La pantalla arma la lista de partidos apenas abre, y para
ese momento los 4 MB de datos todavia se estan descifrando.

Resultado: la lista sale vacia aunque los partidos esten.

Con 5 partidos casi no se notaba. Con 19 pasa siempre.

── LA SOLUCION ───────────────────────────────────────────────────────────────
Los archivos grandes se abren en segundo plano para no colgar los celulares
de los jugadores. Eso esta bien ahi.

Pero "Cargar videos" es una herramienta de escritorio, tuya: un segundo de
espera no molesta a nadie. Asi que esa pantalla —y solo esa— pide que los
datos se abran de una, antes de dibujar.

Las pantallas de los jugadores quedan igual.
"""

import io
import os
import re
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))


def main():
    print()
    print('  ' + '=' * 62)
    print('     QUE "CARGAR VIDEOS" MUESTRE LOS PARTIDOS')
    print('  ' + '=' * 62)
    print()

    ds = os.path.join(AQUI, 'datos_seguros.js')
    iv = os.path.join(AQUI, 'importar_video.html')

    if not os.path.exists(ds) or not os.path.exists(iv):
        print('     Faltan archivos: no parece la carpeta de un club.')
        print()
        return 1

    s = io.open(ds, encoding='utf-8', errors='replace').read()
    h = io.open(iv, encoding='utf-8', errors='replace').read()

    if '__DESCIFRAR_SINCRONO' in s and '__DESCIFRAR_SINCRONO' in h:
        print('  ' + '-' * 62)
        print('     Ya estaba puesto.')
        print()
        return 0

    print('     Se van a cambiar dos cosas:')
    print()
    print('       1. datos_seguros.js  entiende el pedido de abrir "de una"')
    print('       2. importar_video    lo pide, antes de dibujar')
    print()
    print('     Las pantallas de los jugadores no se tocan.')
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

    # ── 1. datos_seguros.js: respetar la marca ──────────────────────────
    if '__DESCIFRAR_SINCRONO' not in s:
        V = "      if(b64 && b64.length > CHICO) { pendientes.push(nombre); continue; }"
        if V not in s:
            m = re.search(r"if\(b64 && b64\.length > CHICO\) \{ pendientes\.push\(nombre\); continue; \}", s)
            if not m:
                print('       datos_seguros.js  tiene otra forma: no lo toco')
                return 1
            V = m.group(0)

        N = ("""/* Una pantalla puede pedir que los archivos grandes se abran DE UNA
         en vez de en segundo plano. Lo usa "Cargar videos", que es una
         herramienta de escritorio: ahi un segundo de espera no molesta,
         y a cambio la lista sale completa a la primera.

         Las pantallas de los jugadores no ponen esa marca, asi que siguen
         abriendo en segundo plano y no se les cuelga el telefono. */
      if(b64 && b64.length > CHICO && !window.__DESCIFRAR_SINCRONO) { pendientes.push(nombre); continue; }""")
        s = s.replace(V, N, 1)

        resp = ds + '.antes-sincrono'
        if not os.path.exists(resp):
            try:
                shutil.copy2(ds, resp)
            except Exception:
                pass
        io.open(ds, 'w', encoding='utf-8').write(s)
        print('       datos_seguros.js       listo')
    else:
        print('       datos_seguros.js       ya estaba')

    # ── 2. importar_video.html: poner la marca ──────────────────────────
    if '__DESCIFRAR_SINCRONO' not in h:
        m = re.search(r'<script src="datos_seguros\.js[^"]*"[^>]*></script>', h)
        if not m:
            print('       importar_video.html    no encontre donde poner la marca')
            return 1

        marca = ('<script>\n'
                 '/* Esta pantalla necesita la lista de partidos completa apenas abre.\n'
                 '   Con los datos abriendose en segundo plano, se dibujaba vacia. */\n'
                 'window.__DESCIFRAR_SINCRONO = true;\n'
                 '</script>\n')
        h = h.replace(m.group(0), marca + m.group(0), 1)

        resp = iv + '.antes-sincrono'
        if not os.path.exists(resp):
            try:
                shutil.copy2(iv, resp)
            except Exception:
                pass
        io.open(iv, 'w', encoding='utf-8').write(h)
        print('       importar_video.html    listo')
    else:
        print('       importar_video.html    ya estaba')

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
