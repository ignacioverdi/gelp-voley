# -*- coding: utf-8 -*-
"""
ARREGLAR_CARGAR_VIDEOS.py
=========================

Hace que la pantalla "Cargar videos" espere a que lleguen los datos.

── EL PROBLEMA ───────────────────────────────────────────────────────────────
La pantalla arma la lista de partidos asi:

    var VD = (window.VIDEO_DATA && window.VIDEO_DATA.matches) || {};

Esa linea corre UNA vez, al abrir. Si en ese momento el archivo cifrado
todavia no termino de descifrarse, VD queda vacio y la pantalla se dibuja
SIN NINGUN PARTIDO — aunque los datos lleguen un segundo despues.

Empeora a medida que se cargan partidos: mas datos, mas tarda el descifrado,
mas chances de perder la carrera. Con 19 partidos ya pasa siempre.

── LA SOLUCION ───────────────────────────────────────────────────────────────
Se espera a que los datos esten, y recien ahi se dibuja. Si a los 10 segundos
no llegaron, se dibuja igual con lo que haya.

── COMO SE USA ───────────────────────────────────────────────────────────────
    Copiar a la carpeta del club (o de la PLANTILLA) y hacer doble clic.
    Queda una copia importar_video.html.antes-espera
"""

import io
import os
import re
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
ARCH = os.path.join(AQUI, 'importar_video.html')


def main():
    print()
    print('  ' + '=' * 62)
    print('     QUE "CARGAR VIDEOS" ESPERE LOS DATOS')
    print('  ' + '=' * 62)
    print()

    if not os.path.exists(ARCH):
        print('     No encontre importar_video.html en esta carpeta.')
        print()
        return 1

    s = io.open(ARCH, encoding='utf-8', errors='replace').read()

    if 'esperarVideoData' in s:
        print('  ' + '-' * 62)
        print('     Ya estaba puesto.')
        print()
        return 0

    if 'var VD' not in s and 'VIDEO_DATA' not in s:
        print('     La pantalla tiene otra forma: no la toco.')
        print()
        return 1

    print('     Se va a hacer que espere a que lleguen los datos antes de')
    print('     dibujar la lista de partidos.')
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

    # En vez de envolver el bloque —que rompia las llaves— se hace algo
    # mas simple y seguro: si al abrir no hay datos, se recarga la pagina
    # una sola vez, cuando ya llegaron. Nada mas cambia.
    ESPERA = """
<script>
/* ── ESPERAR A QUE LLEGUEN LOS DATOS ──────────────────────────────────────
   Los archivos cifrados pueden tardar en abrirse. Si esta pantalla se
   dibuja antes, la lista de partidos queda vacia para siempre: por eso
   con 19 partidos no aparecia ninguno.

   Aca no se toca como dibuja: si al abrir no habia datos, se espera a que
   lleguen y se recarga UNA sola vez. La segunda vez ya estan en el
   navegador y la lista sale completa.

   La marca en sessionStorage evita que se recargue en bucle. */
(function esperarVideoData(){
  function hayDatos(){
    try{
      var d = (typeof MODO !== 'undefined' && MODO === 'ent')
                ? window.VIDEO_DATA_ENT : window.VIDEO_DATA;
      return !!(d && d.matches && Object.keys(d.matches).length);
    }catch(e){ return false; }
  }
  if(hayDatos()) return;                       /* ya estaban: nada que hacer */
  if(sessionStorage.getItem('vid_recarga')) return;   /* ya se recargo una vez */

  var intentos = 0;
  var t = setInterval(function(){
    intentos++;
    if(intentos > 50){ clearInterval(t); return; }    /* 10 segundos y basta */
    if(hayDatos()){
      clearInterval(t);
      try{ sessionStorage.setItem('vid_recarga','1'); }catch(e){}
      location.reload();
    }
  }, 200);

  try{ window.addEventListener('datos-listos', function(){
    if(hayDatos() && !sessionStorage.getItem('vid_recarga')){
      try{ sessionStorage.setItem('vid_recarga','1'); }catch(e){}
      location.reload();
    }
  }); }catch(e){}
})();
</script>
"""

    if '</body>' in s:
        s = s.replace('</body>', ESPERA + '</body>', 1)
    else:
        s = s + ESPERA

    respaldo = ARCH + '.antes-espera'
    if not os.path.exists(respaldo):
        try:
            shutil.copy2(ARCH, respaldo)
        except Exception:
            pass
    io.open(ARCH, 'w', encoding='utf-8').write(s)

    print()
    print('  ' + '-' * 62)
    print('     Listo. Ahora corre PUBLICAR.bat')
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
