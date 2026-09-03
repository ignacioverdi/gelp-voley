# -*- coding: utf-8 -*-
"""
ARREGLAR_PANTALLAS_ANALISIS.py
==============================

Hace que las pantallas de analisis esperen a que lleguen los datos.

── EL PROBLEMA ───────────────────────────────────────────────────────────────
Las pantallas de analisis —plan de partido, heat maps, rotaciones, cortes—
leen sus datos apenas abren. Pero los archivos cifrados son grandes y se
abren en segundo plano para no colgar los celulares.

Resultado: la pantalla se dibuja ANTES de que lleguen y queda vacia.

    "Plan de partido"  ->  Rival (0)  ->  no aparece nada

Los datos estan: se puede comprobar en la consola, PP_DATA existe. Solo
llegan tarde.

Con pocos partidos casi no se notaba. Con 19 pasa siempre.

── LA SOLUCION ───────────────────────────────────────────────────────────────
Estas son pantallas de escritorio, del cuerpo tecnico: un segundo de espera
no molesta. Se les pone la misma marca que ya usa "Cargar videos", para que
los datos se abran de una, antes de dibujar.

Las pantallas de las jugadoras —dashboard, wellness, prep fisica, equipo—
NO se tocan: siguen abriendo en segundo plano para no trabar telefonos.
"""

import io
import os
import re
import shutil
import sys
import glob

AQUI = os.path.dirname(os.path.abspath(__file__))

# Pantallas de escritorio que necesitan sus datos completos al abrir.
# Se excluyen a proposito las que usan los jugadores desde el celular.
DE_ESCRITORIO = [
    'plan_partido.html', 'game_plan.html', 'armadores.html', 'rotaciones.html',
    'cortes.html', 'jugador.html',
    'hm_armador.html', 'hm_ataque.html', 'hm_defensa.html',
    'hm_recepcion.html', 'hm_saque.html',
    'analisis.html', 'historial_voley.html', 'informe.html',
    'panel_voley.html', 'panel_vivo.html', 'diagnostico.html',
    'plan_desarrollo.html', 'tendencias.html', 'ranking.html',
    'baggerone.html', 'recepcion.html', 'ataque_jugador.html',
    'saque_jugador.html', 'recepcion_jugador.html', 'importar_video.html',
]

MARCA = ('<script>\n'
         '/* Esta pantalla necesita sus datos completos apenas abre: si se dibuja\n'
         '   antes de que terminen de descifrarse, sale vacia.\n'
         '   Es una pantalla de escritorio, del cuerpo tecnico: un segundo de\n'
         '   espera no molesta. Las pantallas de las jugadoras no llevan esta\n'
         '   marca, asi que siguen abriendo en segundo plano. */\n'
         'window.__DESCIFRAR_SINCRONO = true;\n'
         '</script>\n')


def main():
    print()
    print('  ' + '=' * 62)
    print('     QUE LAS PANTALLAS DE ANALISIS ESPEREN SUS DATOS')
    print('  ' + '=' * 62)
    print()

    ds = os.path.join(AQUI, 'datos_seguros.js')
    if not os.path.exists(ds):
        print('     No encontre datos_seguros.js: no parece la carpeta de un club.')
        print()
        return 1

    s = io.open(ds, encoding='utf-8', errors='replace').read()
    if '__DESCIFRAR_SINCRONO' not in s:
        print('     Falta preparar datos_seguros.js.')
        print('     Corre primero ARREGLAR_VIDEOS_VACIO.py')
        print()
        return 1

    pendientes = []
    for f in DE_ESCRITORIO:
        ruta = os.path.join(AQUI, f)
        if not os.path.exists(ruta):
            continue
        h = io.open(ruta, encoding='utf-8', errors='replace').read()
        if '__DESCIFRAR_SINCRONO' in h:
            continue
        if not re.search(r'<script src="datos_seguros\.js', h):
            continue
        pendientes.append(f)

    if not pendientes:
        print('  ' + '-' * 62)
        print('     Todas las pantallas de analisis ya estan listas.')
        print()
        return 0

    print('     Pantallas a arreglar (%d):' % len(pendientes))
    print()
    for f in pendientes:
        print('       · ' + f)
    print()
    print('     Las pantallas de las jugadoras NO se tocan.')
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
        h = io.open(ruta, encoding='utf-8', errors='replace').read()
        m = re.search(r'<script src="datos_seguros\.js[^"]*"[^>]*></script>', h)
        if not m:
            print('       %-24s sin cambios' % f)
            continue

        h = h.replace(m.group(0), MARCA + m.group(0), 1)

        resp = ruta + '.antes-sincrono'
        if not os.path.exists(resp):
            try:
                shutil.copy2(ruta, resp)
            except Exception:
                pass
        io.open(ruta, 'w', encoding='utf-8').write(h)
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
