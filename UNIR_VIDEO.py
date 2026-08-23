# -*- coding: utf-8 -*-
"""
===============================================================================
  UNIR_VIDEO.py — VARIOS ARCHIVOS, UN SOLO VIDEO
-------------------------------------------------------------------------------
  Doble clic. Arrastra los archivos del partido y los une en uno.

  ── QUE PROBLEMA RESUELVE ───────────────────────────────────────────────────
  Muchas camaras cortan la grabacion cada 20 o 30 minutos, o cada 4 GB. Un
  partido queda en cuatro o cinco archivos.

  Para subirlo a YouTube y que los cortes de video funcionen hace falta UN
  solo archivo: si se suben por separado, cada accion apunta al minuto
  equivocado.

  ── COMO LO HACE ────────────────────────────────────────────────────────────
  Si los archivos son de la misma camara —lo normal cuando es una grabacion
  cortada— se pegan SIN volver a comprimir. Un partido de dos horas tarda
  segundos y no pierde ni un poco de calidad.

  Si vienen de camaras distintas hay que unificarlos, y eso si lleva tiempo.
  El programa avisa antes de empezar.

  ── QUE NECESITA ───────────────────────────────────────────────────────────
  ffmpeg. Si no esta, el programa explica como instalarlo: es una sola vez y
  despues funciona para siempre.
===============================================================================
"""
import io
import os
import re
import sys
import glob
import json
import shutil
import subprocess

AQUI = os.path.dirname(os.path.abspath(__file__))

EXTENSIONES = ('.mp4', '.mov', '.mkv', '.avi', '.m4v', '.mts', '.m2ts', '.wmv')


def hay_ffmpeg():
    for cmd in ('ffmpeg', os.path.join(AQUI, 'ffmpeg.exe')):
        try:
            subprocess.run([cmd, '-version'], capture_output=True, timeout=10)
            return cmd
        except Exception:
            continue
    return None


def explicar_ffmpeg():
    print()
    print('  ' + '=' * 66)
    print('     FALTA UN PROGRAMA (una sola vez)')
    print('  ' + '=' * 66)
    print()
    print('     Para unir videos hace falta ffmpeg, que es gratuito y lo usan')
    print('     casi todos los programas de video del mundo.')
    print()
    print('     COMO INSTALARLO:')
    print()
    print('       1. Entra a  https://www.gyan.dev/ffmpeg/builds/')
    print('       2. Baja  "ffmpeg-release-essentials.zip"')
    print('       3. Abri el zip y busca la carpeta  bin')
    print('       4. Copia  ffmpeg.exe  al lado de este programa')
    print()
    print('     Y listo: no hay que instalar nada mas ni volver a hacerlo.')
    print()


def datos_de(cmd, ruta):
    """El formato de un video, para saber si se puede pegar sin recomprimir."""
    try:
        r = subprocess.run(
            [cmd.replace('ffmpeg', 'ffprobe'), '-v', 'error',
             '-show_entries', 'stream=codec_name,width,height,r_frame_rate',
             '-show_entries', 'format=duration',
             '-of', 'json', ruta],
            capture_output=True, text=True, timeout=60)
        d = json.loads(r.stdout or '{}')
        v = None
        for s in (d.get('streams') or []):
            if s.get('width'):
                v = s
                break
        dur = float((d.get('format') or {}).get('duration') or 0)
        if not v:
            return None, dur
        return (v.get('codec_name'), v.get('width'), v.get('height'),
                v.get('r_frame_rate')), dur
    except Exception:
        return None, 0


def mmss(seg):
    seg = int(seg or 0)
    h, r = divmod(seg, 3600)
    m, s = divmod(r, 60)
    return ('%d:%02d:%02d' % (h, m, s)) if h else ('%d:%02d' % (m, s))


def pedir_archivos():
    print('  Arrastra los archivos del partido, uno por uno, y Enter en cada uno.')
    print('  Cuando termines, Enter solo.')
    print()
    print('  IMPORTANTE: arrastralos EN ORDEN, del primero al ultimo.')
    print()
    lista = []
    while True:
        try:
            r = input('  %d) ' % (len(lista) + 1)).strip().strip('"').strip("'")
        except Exception:
            break
        if not r:
            break
        if not os.path.isfile(r):
            print('     no encuentro ese archivo')
            continue
        if not r.lower().endswith(EXTENSIONES):
            print('     eso no parece un video')
            continue
        lista.append(r)
    return lista


def main():
    print()
    print('  ' + '=' * 66)
    print('     UNIR LOS VIDEOS DE UN PARTIDO')
    print('  ' + '=' * 66)
    print()

    cmd = hay_ffmpeg()
    if not cmd:
        explicar_ffmpeg()
        input('  Enter para cerrar...')
        return 1

    archivos = pedir_archivos()
    if len(archivos) < 2:
        print()
        print('  Hacen falta al menos dos archivos para unir.')
        input('\n  Enter para cerrar...')
        return 0

    # ── mirar que son ───────────────────────────────────────────────────────
    print()
    print('  ' + '-' * 66)
    print('  LOS ARCHIVOS')
    print('  ' + '-' * 66)
    formatos, total = [], 0
    for f in archivos:
        fmt, dur = datos_de(cmd, f)
        formatos.append(fmt)
        total += dur
        tam = os.path.getsize(f) / 1048576
        print('     %-38s %8s  %6.0f MB' % (os.path.basename(f)[:38], mmss(dur), tam))
        if fmt:
            print('        %s · %sx%s' % (fmt[0], fmt[1], fmt[2]))

    print()
    print('     En total: %s' % mmss(total))

    # ── se pueden pegar sin recomprimir? ────────────────────────────────────
    iguales = all(f == formatos[0] for f in formatos if f) and formatos[0]
    print()
    if iguales:
        print('     Son del mismo formato: los pego sin volver a comprimir.')
        print('     Tarda segundos y no pierde nada de calidad.')
    else:
        print('     [ATENCION] Los archivos NO tienen el mismo formato.')
        print('     Hay que unificarlos, y eso tarda: un partido de dos horas')
        print('     puede llevar 20 minutos o mas, segun la computadora.')

    # ── donde guardarlo ─────────────────────────────────────────────────────
    base = os.path.splitext(archivos[0])[0]
    base = re.sub(r'[_\- ]*\(?\d+\)?$', '', base)      # sacar el "(1)" del final
    salida = base + '_completo.mp4'
    print()
    print('     Se va a guardar como:')
    print('        %s' % os.path.basename(salida))

    print()
    try:
        r = input('  Uno los videos? (s/n): ').strip().lower()
    except Exception:
        r = 'n'
    if r != 's':
        print('  No toque nada.')
        input('\n  Enter para cerrar...')
        return 0

    # ── unir ────────────────────────────────────────────────────────────────
    print()
    print('  Uniendo... (no cierres esta ventana)')
    print()

    lista_txt = os.path.join(os.path.dirname(salida) or '.', '_lista_union.txt')
    try:
        with io.open(lista_txt, 'w', encoding='utf-8') as f:
            for a in archivos:
                f.write("file '%s'\n" % os.path.abspath(a).replace('\\', '/').replace("'", "'\\''"))

        if iguales:
            # pegar tal cual: sin recomprimir
            orden = [cmd, '-f', 'concat', '-safe', '0', '-i', lista_txt,
                     '-c', 'copy', salida, '-y']
        else:
            # unificar: se recomprime a un formato comun
            orden = [cmd, '-f', 'concat', '-safe', '0', '-i', lista_txt,
                     '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
                     '-c:a', 'aac', salida, '-y']

        p = subprocess.run(orden, capture_output=True, text=True)
        if p.returncode != 0:
            print('  No pude unirlos.')
            det = (p.stderr or '')[-400:]
            if det:
                print()
                print('  El detalle:')
                for l in det.split('\n')[-6:]:
                    if l.strip():
                        print('     %s' % l.strip()[:70])
            print()
            print('  Si dice algo de "codec" o "format", los archivos son de')
            print('  camaras distintas: proba de nuevo, va a tardar mas pero')
            print('  deberia funcionar.')
            input('\n  Enter para cerrar...')
            return 1
    finally:
        try:
            os.remove(lista_txt)
        except Exception:
            pass

    _fmt, dur = datos_de(cmd, salida)
    tam = os.path.getsize(salida) / 1048576

    print()
    print('  ' + '=' * 66)
    print('     LISTO')
    print('  ' + '=' * 66)
    print('     %s' % os.path.basename(salida))
    print('     %s  ·  %.0f MB' % (mmss(dur), tam))
    print()
    if abs(dur - total) > 5:
        print('     [ATENCION] El video unido dura %s y los originales sumaban %s.'
              % (mmss(dur), mmss(total)))
        print('     Revisalo antes de subirlo.')
        print()
    print('     Ahora subilo a YouTube como "No listado" y pega el link en')
    print('     Cargar Videos.')
    print()
    print('     Los archivos originales quedaron intactos.')
    print()
    input('  Enter para cerrar...')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        print()
        print('  ALGO FALLO: %s' % e)
        traceback.print_exc()
        try:
            input('  Enter para cerrar...')
        except Exception:
            pass
        sys.exit(1)
