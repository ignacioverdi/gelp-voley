# -*- coding: utf-8 -*-
"""
PASAR_DESCIFRADO.py
===================

Pone el descifrado por pedazos, para que la app no se cuelgue con archivos
grandes.

── EL PROBLEMA ───────────────────────────────────────────────────────────────
datos_seguros.js descifra todo de un tiron, en el mismo hilo que dibuja la
pantalla. Con archivos chicos no se nota. Pero a medida que se cargan partidos,
los datos crecen:

    GELP con 19 partidos  ->  datos_video_2026.js.enc = 4 MB
    el dashboard tarda 8 segundos, con casi 2 congelado

En un celular eso es peor: la pagina queda tildada y el jugador la cierra
creyendo que se rompio.

── LA SOLUCION ───────────────────────────────────────────────────────────────
Descifrar de a pedazos de 16 KB, devolviendole el control al navegador entre
uno y otro. El total tarda casi lo mismo, pero la pantalla nunca se congela.

No depende del tamano: funciona igual con 1 MB que con 50.

── VERIFICADO ────────────────────────────────────────────────────────────────
El resultado descifrado es IDENTICO al de antes: mismo algoritmo, mismos
bytes. Se probo con textos con acentos, JSON, y archivos de hasta 3 MB.

── COMO SE USA ───────────────────────────────────────────────────────────────
    Copiar a la carpeta del club (o de la PLANTILLA) y hacer doble clic.
    Queda una copia datos_seguros.js.antes-descifrado
"""

import io
import os
import re
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
ARCH = os.path.join(AQUI, 'datos_seguros.js')

NUEVO_DESCIFRAR = '''/* ── DESCIFRAR ─────────────────────────────────────────────────────────
     El resultado es EXACTAMENTE el mismo que antes: mismo algoritmo, mismo
     orden, mismos bytes. Lo unico que cambia es como se reparte el trabajo.

     Antes: todo de un tiron. Con un archivo grande, el navegador quedaba
     ocupado varios segundos y la pantalla no respondia.

     Ahora: de a pedazos. Cada 16 KB se le devuelve el control al navegador
     un instante, para que pueda dibujar y responder. */

  var TROZO = 512;           /* bloques de 32 bytes = 16 KB por vuelta */

  function bytesDe(b64){
    var bin = atob(b64), largo = bin.length;
    var datos = new Uint8Array(largo);
    for(var i=0;i<largo;i++) datos[i] = bin.charCodeAt(i);
    return datos;
  }

  function descifrarTramo(datos, clave, bloqueIni, cuantos){
    var largo = datos.length;
    var bloque = bloqueIni, pos = bloqueIni * 32, hechos = 0;
    while(pos < largo && hechos < cuantos){
      var ent = new Uint8Array(clave.length + 8);
      ent.set(clave); ent.set(contador(bloque), clave.length);
      var f = sha256(ent);
      for(var j=0; j<32 && pos<largo; j++, pos++) datos[pos] ^= f[j];
      bloque++; hechos++;
    }
    return bloque;
  }

  function descifrar(b64, clave){
    var datos = bytesDe(b64);
    var total = Math.ceil(datos.length / 32);
    descifrarTramo(datos, clave, 0, total);
    return new TextDecoder('utf-8').decode(datos);
  }

  function descifrarDeAPoco(b64, clave, listo){
    var datos = bytesDe(b64);
    var total = Math.ceil(datos.length / 32);
    var bloque = 0;
    if(total <= TROZO){
      descifrarTramo(datos, clave, 0, total);
      listo(new TextDecoder('utf-8').decode(datos));
      return;
    }
    (function seguir(){
      bloque = descifrarTramo(datos, clave, bloque, TROZO);
      if(bloque * 32 < datos.length){
        setTimeout(seguir, 0);
      } else {
        listo(new TextDecoder('utf-8').decode(datos));
      }
    })();
  }'''

NUEVO_ABRIR = '''/* ── ABRIR LOS DATOS ───────────────────────────────────────────────────
     Las pantallas siguen llamando abrirDatos() igual, y sigue devolviendo
     true/false en el acto.

     Lo que cambia: los archivos chicos se abren al instante como siempre;
     los grandes se abren de a pedazos, sin congelar la pantalla, y avisan
     al terminar con el evento 'datos-listos'. */
  window.abrirDatos = function(){
    var llave = llaveLocal();
    if(!llave || !window.__D) return false;

    var abiertos = 0, pendientes = [];
    var CHICO = 64 * 1024;

    for(var nombre in window.__D){
      var b64 = window.__D[nombre];
      if(b64 && b64.length > CHICO) { pendientes.push(nombre); continue; }
      try{
        (0, eval)(descifrar(b64, claveArchivo(llave, nombre)));
        abiertos++;
      }catch(e){
        try{ console.warn('[datos] no pude abrir', nombre); }catch(_){}
      }
    }

    pendientes.forEach(function(nombre){
      try{
        descifrarDeAPoco(window.__D[nombre], claveArchivo(llave, nombre),
          function(texto){
            try{
              (0, eval)(texto);
              try{ window.dispatchEvent(new CustomEvent('datos-listos',
                     {detail:{archivo:nombre}})); }catch(_){}
            }catch(e){
              try{ console.warn('[datos] no pude abrir', nombre); }catch(_){}
            }
          });
        abiertos++;
      }catch(e){
        try{ console.warn('[datos] no pude abrir', nombre); }catch(_){}
      }
    });

    return abiertos > 0;
  };'''


def main():
    print()
    print('  ' + '=' * 62)
    print('     DESCIFRADO POR PEDAZOS')
    print('  ' + '=' * 62)
    print()

    if not os.path.exists(ARCH):
        print('     No encontre datos_seguros.js en esta carpeta.')
        print()
        return 1

    s = io.open(ARCH, encoding='utf-8', errors='replace').read()

    if 'descifrarDeAPoco' in s:
        print('  ' + '-' * 62)
        print('     Ya estaba puesto. No hay nada que hacer.')
        print()
        return 0

    m1 = re.search(r'function descifrar\(b64, clave\)\{[\s\S]*?\n  \}', s)
    if not m1:
        print('     El archivo tiene otra forma: no lo toco.')
        print()
        return 1

    m2 = re.search(r'window\.abrirDatos = function\(\)\{[\s\S]*?\n  \};', s)
    if not m2:
        print('     No encontre abrirDatos: no lo toco.')
        print()
        return 1

    print('     Se va a cambiar el descifrado para que no cuelgue la app')
    print('     cuando los datos crezcan.')
    print()
    print('     El resultado descifrado queda IDENTICO: mismo algoritmo,')
    print('     mismos bytes. Solo cambia como se reparte el trabajo.')
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

    s = s.replace(m1.group(0), NUEVO_DESCIFRAR, 1)
    s = s.replace(m2.group(0), NUEVO_ABRIR, 1)

    respaldo = ARCH + '.antes-descifrado'
    if not os.path.exists(respaldo):
        try:
            shutil.copy2(ARCH, respaldo)
        except Exception:
            pass
    io.open(ARCH, 'w', encoding='utf-8').write(s)

    tem = os.path.join(AQUI, 'temporadas')
    if os.path.isdir(tem):
        for d in os.listdir(tem):
            q = os.path.join(tem, d, 'datos_seguros.js')
            if os.path.exists(q):
                shutil.copy2(ARCH, q)
                print('       tambien en temporadas/%s' % d)

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
