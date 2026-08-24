# -*- coding: utf-8 -*-
"""
Arregla los encabezados que se encima uno arriba del otro.

EL PROBLEMA
La barra de arriba de cada pantalla es un "flex": pone los elementos en
fila y los reparte. Pero sin permiso para bajar de renglon, cuando no
entran no se acomodan: se montan uno sobre otro. Por eso arriba a la
derecha el titulo queda pisado por los botones de idioma y la etiqueta de
la temporada.

Se ve en pantallas anchas tambien, porque el titulo puede ser largo
("ANALISIS DE PARTIDOS - NAFELS VOLEY - NLA SUIZA 2025/26") y no tiene
un ancho maximo: empuja al resto fuera de lugar.

LA SOLUCION
Tres reglas de CSS, al final de la hoja de estilos de cada pantalla:

  1. la barra puede bajar de renglon    -> flex-wrap: wrap
  2. hay aire entre los elementos       -> gap
  3. el titulo puede achicarse          -> min-width: 0

Con eso, cuando no entra, baja. No se encima nunca mas.

No cambia colores, ni tamanos, ni el orden de nada. Solo agrega esas
reglas al final, que es lo ultimo que lee el navegador y por eso mandan.

Primero muestra que va a hacer y pide permiso. De cada pantalla que toca
deja una copia .antes-encimado
"""

import io
import os
import re
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))

MARCA = '/* === ENCABEZADO: QUE NO SE ENCIME === */'

ARREGLO = """
/* === ENCABEZADO: QUE NO SE ENCIME === */
/* Los botones de idioma van en un ".header-right" con position:fixed, que
   flota por encima de todo y NO ocupa lugar. El titulo se dibuja debajo y
   se lee la mezcla de los dos.
   Solucion: se le reserva el espacio al titulo con un margen del ancho de
   esos botones, y se sube la barra por encima del contenido. */
.header {
  position: relative;
  z-index: 1;
  padding-right: 190px;   /* el lugar que ocupan los botones flotantes */
  flex-wrap: wrap;
  gap: 10px 14px;
}
.header-right {
  z-index: 99998;
  pointer-events: auto;
}
/* El titulo puede achicarse en vez de empujar al resto */
.header > div,
.topbar > div,
.top-bar > div {
  min-width: 0;
}
.header .title,
.topbar .title,
.top-bar .title {
  min-width: 0;
  overflow-wrap: break-word;
}
/* Las otras barras, por las dudas */
.topbar,
.top-bar,
.page-header,
.hdr {
  flex-wrap: wrap;
  gap: 10px 14px;
}
.lang-wrap,
.lang-switch,
.idiomas {
  flex: none;
  white-space: nowrap;
}
/* En el celular los botones dejan de flotar: se ponen en su renglon */
@media (max-width: 820px) {
  .header {
    padding-right: 14px;
    padding-top: 46px;    /* aire para los botones de arriba */
    align-items: flex-start;
  }
}
"""


def pantallas(carpeta):
    for a in sorted(os.listdir(carpeta)):
        if a.endswith('.html') and not a.endswith('.antes-encimado'):
            yield os.path.join(carpeta, a)


def arreglar(ruta, aplicar):
    """Mete el arreglo al final del <style>. Devuelve True si hacia falta."""
    try:
        t = io.open(ruta, encoding='utf-8', errors='replace').read()
    except Exception:
        return False

    if MARCA in t:
        return False                      # ya lo tiene

    # el ultimo </style> del documento: ahi va, para que mande
    i = t.rfind('</style>')
    if i < 0:
        return False

    # solo si la pantalla tiene una barra de esas
    if not re.search(r'class\s*=\s*["\'][^"\']*\b(header|topbar|top-bar|page-header|hdr)\b', t):
        return False

    if aplicar:
        nuevo = t[:i] + ARREGLO + t[i:]
        respaldo = ruta + '.antes-encimado'
        if not os.path.exists(respaldo):
            shutil.copy2(ruta, respaldo)
        io.open(ruta, 'w', encoding='utf-8').write(nuevo)

    return True


def recorrer():
    """La carpeta del club y sus temporadas archivadas."""
    carpetas = [('principal', AQUI)]
    base = os.path.join(AQUI, 'temporadas')
    if os.path.isdir(base):
        for n in sorted(os.listdir(base)):
            c = os.path.join(base, n)
            if os.path.isdir(c) and not n.startswith('_'):
                carpetas.append((n, c))
    return carpetas


def main():
    print()
    print('  ' + '=' * 62)
    print('     QUE LOS ENCABEZADOS NO SE ENCIMEN')
    print('  ' + '=' * 62)
    print()
    print('  La barra de arriba no puede bajar de renglon, asi que cuando')
    print('  el titulo es largo los botones se le montan encima.')
    print()

    carpetas = recorrer()
    plan = []
    total = 0

    for nombre, carpeta in carpetas:
        faltan = [p for p in pantallas(carpeta) if arreglar(p, aplicar=False)]
        plan.append((nombre, carpeta))
        total += len(faltan)
        if faltan:
            print('  %-14s %d pantalla(s) para arreglar' % (nombre, len(faltan)))
        else:
            print('  %-14s ya estaban bien' % nombre)

    print()
    if not total:
        print('  ' + '-' * 62)
        print('     No hay nada que hacer.')
        print()
        return 0

    print('  ' + '-' * 62)
    print('     Solo se agregan reglas de CSS al final de cada pantalla.')
    print('     No cambia colores, ni tamanos, ni el orden de nada.')
    print('     De cada una queda una copia .antes-encimado')
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
    for nombre, carpeta in plan:
        n = sum(1 for p in pantallas(carpeta) if arreglar(p, aplicar=True))
        if n:
            print('     %-14s %d pantalla(s) arreglada(s)' % (nombre, n))

    print()
    print('  ' + '-' * 62)
    print('     Listo. Publica y abri en INCOGNITO para verlo.')
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
