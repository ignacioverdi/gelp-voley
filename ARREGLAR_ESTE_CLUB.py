# -*- coding: utf-8 -*-
"""
ARREGLAR_ESTE_CLUB.py
=====================

Aplica a un club los arreglos del 1 de septiembre, SIN tocar sus datos
propios: la direccion de su base, su clave y su nombre quedan como estan.

Corre en la carpeta del club (GELP, CASLA, BOCA...) y arregla su firebase.js.

── QUE ARREGLA ───────────────────────────────────────────────────────────────

  1. EL JUGADOR CORRE EL MISMO CAMINO QUE EL ENTRENADOR
     Habia una funcion que solo se ejecutaba para jugadores. Ahi estaban
     casi todos los problemas, y era invisible probando con cuenta de staff.

  2. NO SE PIERDEN LOS TOKENS AL RENOVAR
     Al renovar la sesion se guardaba sin los tokens: la llamada siguiente
     no encontraba ninguno, pedia renovar otra vez, y asi miles de veces.

  3. SI GOOGLE RECHAZA EL TOKEN, SE PIDE INGRESAR
     Antes se reintentaba con el mismo token invalido, sin fin.

  4. UNA SOLA RENOVACION A LA VEZ
     Firebase quema el token cada vez que se usa. Si dos pedidos renovaban
     juntos, el segundo salia con uno ya quemado.

  5. NO REPETIR EL ROL NI EL CONTROL DE SESION
     Se pedian cientos de veces por carga. Ahora, una vez por minuto.

  6. NO CERRAR LA SESION SI NO SE SABE CUANDO SE CREO
     Las sesiones viejas no traen fecha y se cerraban solas a los 2 segundos.

  7. FRENO GENERAL
     Tope de pedidos por carga. Si algo se dispara en bucle, se corta antes
     de colgar el telefono.

── COMO SE USA ───────────────────────────────────────────────────────────────
    Copiar a la carpeta del club y hacer doble clic.
    Queda una copia firebase.js.antes por las dudas.
"""

import io
import os
import re
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
ARCH = os.path.join(AQUI, 'firebase.js')


def aplicar(s):
    """Devuelve (texto_nuevo, lista_de_lo_hecho, lista_de_lo_que_ya_estaba)."""
    hechos, ya = [], []

    # ── 1. el jugador, mismo camino que el entrenador ────────────────────
    if 'function _fbCategoriaJugador(){ return; }' in s:
        ya.append('el jugador ya corre el mismo camino')
    else:
        m = re.search(r'\s*if\(!_fbCatPedida\)\{[^\n]*\n', s)
        if m:
            s = s.replace(m.group(0), '\n', 1)
        else:
            s = s.replace('_fbSincronizarRol(); _fbCategoriaJugador();',
                          '_fbSincronizarRol();', 1)
        i = s.find('function _fbCategoriaJugador')
        if i >= 0:
            j = s.find('\n}', i) + 2
            s = (s[:i] +
                 '/* Desactivada: era LO UNICO que un jugador hacia y un entrenador no,\n'
                 '   y ahi estaban casi todos los problemas. Ahora los dos corren el\n'
                 '   mismo codigo. */\nfunction _fbCategoriaJugador(){ return; }\n\n' +
                 s[j:])
            hechos.append('el jugador corre el mismo camino que el entrenador')

    # ── 2. guardar los tokens al renovar ─────────────────────────────────
    if 'idToken: d.id_token' in s:
        ya.append('ya guarda los tokens al renovar')
    else:
        m = re.search(r"_fbGuardarSes\(\{emitido:\(FB_SES && FB_SES\.emitido\)", s)
        if m:
            s = s.replace(m.group(0),
                          "_fbGuardarSes({idToken: d.id_token,\n"
                          "                     refreshToken: d.refresh_token || FB_SES.refreshToken,\n"
                          "                     emitido:(FB_SES && FB_SES.emitido)", 1)
            hechos.append('guarda los tokens al renovar')

    # ── 3. si Google rechaza, pedir ingresar ─────────────────────────────
    V3 = "if(!d || !d.id_token) throw new Error('sesion vencida');"
    if V3 in s:
        s = s.replace(V3,
                      "if(!d || !d.id_token){\n"
                      "        /* un token que Google rechaza no se arregla reintentando */\n"
                      "        try{ _fbGuardarSes(null); }catch(e){}\n"
                      "        throw new Error('sesion vencida');\n"
                      "      }", 1)
        hechos.append('si Google rechaza el token, se pide ingresar')
    else:
        ya.append('ya maneja el rechazo del token')

    # ── 4. una sola renovacion a la vez ──────────────────────────────────
    if '_fbEnCurso' in s:
        ya.append('ya renueva de a una')
    else:
        m = re.search(r"function _fbRefrescar\(\)\{\s*\n\s*if\(!FB_SES \|\| !FB_SES\.refreshToken\)"
                      r" return Promise\.reject\(new Error\('sin sesion'\)\);", s)
        if m:
            s = s.replace(m.group(0),
                          "var _fbEnCurso = null;\n"
                          "function _fbRefrescar(){\n"
                          "  if(!FB_SES || !FB_SES.refreshToken) return Promise.reject(new Error('sin sesion'));\n"
                          "  if(_fbEnCurso) return _fbEnCurso;", 1)
            m2 = re.search(r"      return FB_SES\.idToken;\n    \}\);\n\}", s)
            if m2:
                s = s.replace(m2.group(0),
                              "      return FB_SES.idToken;\n"
                              "    })\n"
                              "    .then(function(t){ _fbEnCurso = null; return t; },\n"
                              "          function(e){ _fbEnCurso = null; throw e; });\n\n"
                              "  _fbEnCurso = p;\n  return p;\n}", 1)
                s = s.replace("  return fetch('https://securetoken.googleapis.com/v1/token?key=' + FB_KEY, {",
                              "  var p = fetch('https://securetoken.googleapis.com/v1/token?key=' + FB_KEY, {", 1)
                hechos.append('una sola renovacion de token a la vez')

    # ── 5. no repetir el rol ni el control de sesion ─────────────────────
    if '_fbRolHecho' in s:
        ya.append('ya evita repetir el rol')
    else:
        m = re.search(r'function _fbCargarRol\(\)\{', s)
        if m:
            s = s.replace('function _fbCargarRol(){',
                          "var _fbRolEnCurso = null, _fbRolHecho = 0;\n"
                          "function _fbCargarRol(){\n"
                          "  /* el rol no cambia mientras se usa la app: alcanza una vez por minuto */\n"
                          "  if(_fbRolEnCurso) return _fbRolEnCurso;\n"
                          "  if(_fbRolHecho && (Date.now() - _fbRolHecho) < 60000) return Promise.resolve();\n"
                          "  _fbRolEnCurso = _fbCargarRolReal();\n"
                          "  var _s = function(){ _fbRolEnCurso = null; _fbRolHecho = Date.now(); };\n"
                          "  _fbRolEnCurso.then(_s, _s);\n"
                          "  return _fbRolEnCurso;\n}\n\n"
                          "function _fbCargarRolReal(){", 1)
            hechos.append('el rol no se repite')

    if '_fbCtrlHecho' in s:
        ya.append('ya evita repetir el control de sesion')
    else:
        m = re.search(r"function _fbControlSesion\(\)\{\s*\n?\s*if\(!FB_SES \|\| !FB_SES\.uid\) return Promise\.resolve\(\);", s)
        if m:
            s = s.replace(m.group(0), m.group(0).replace(
                'function _fbControlSesion(){',
                'var _fbCtrlHecho = 0;\nfunction _fbControlSesion(){') +
                "\n  if(_fbCtrlHecho && (Date.now() - _fbCtrlHecho) < 60000) return Promise.resolve();\n"
                "  _fbCtrlHecho = Date.now();", 1)
            hechos.append('el control de sesion no se repite')

    # ── 6. no cerrar sesion sin fecha ────────────────────────────────────
    if 'FB_SES.emitido || 0' in s:
        s = s.replace('var emitido = FB_SES.emitido || 0;',
                      '/* sin fecha, se trata como recien creada: en la duda se deja entrar */\n'
                      '        var emitido = FB_SES.emitido || Date.now();', 1)
        hechos.append('no cierra la sesion cuando no sabe la fecha')
    else:
        ya.append('ya no cierra sesiones sin fecha')

    # ── 7. freno general ─────────────────────────────────────────────────
    if '_fbCorta' in s:
        ya.append('ya tiene freno general')
    else:
        i = s.find('function _fbSufijo')
        if i > 0:
            s = (s[:i] +
                 "/* Freno general: si algo se dispara en bucle, se corta antes de que el\n"
                 "   telefono se quede sin recursos. El uso normal no llega ni cerca. */\n"
                 "var _fbCuenta = 0, _fbCortado = false;\n"
                 "function _fbCorta(){\n"
                 "  if(_fbCortado) return true;\n"
                 "  if(++_fbCuenta > 1200){ _fbCortado = true;\n"
                 "    try{ console.warn('Volley-Stats: demasiados pedidos, se corto.'); }catch(e){}\n"
                 "    return true; }\n"
                 "  return false;\n}\n\n" + s[i:])
            for f, ret in [('function fbGet(', 'undefined'),
                           ('function fbSet(', 'Promise.resolve()'),
                           ('function fbPush(', 'Promise.resolve()')]:
                j = s.find(f)
                if j < 0:
                    continue
                k = s.find('{', s.find(')', j)) + 1
                s = s[:k] + ('\n  if(_fbCorta()) return ' + ret + ';') + s[k:]
            hechos.append('freno general contra bucles')

    return s, hechos, ya


def main():
    print()
    print('  ' + '=' * 62)
    print('     ARREGLOS DEL 1 DE SEPTIEMBRE')
    print('  ' + '=' * 62)
    print()

    if not os.path.exists(ARCH):
        print('     No encontre firebase.js en esta carpeta.')
        print('     Copia este programa a la carpeta del club.')
        print()
        return 1

    s = io.open(ARCH, encoding='utf-8', errors='replace').read()

    club = re.search(r"FB_CLUB\s*=\s*'([^']*)'", s)
    print('     Club: %s' % (club.group(1) if club else '?'))
    print()

    nuevo, hechos, ya = aplicar(s)

    if ya:
        print('     Ya estaba:')
        for x in ya:
            print('       · ' + x)
        print()

    if not hechos:
        print('  ' + '-' * 62)
        print('     No habia nada que arreglar.')
        print()
        return 0

    print('     Se va a arreglar:')
    for x in hechos:
        print('       · ' + x)
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

    if not os.path.exists(ARCH + '.antes'):
        shutil.copy2(ARCH, ARCH + '.antes')
    io.open(ARCH, 'w', encoding='utf-8').write(nuevo)

    # la copia de la temporada archivada, si existe
    for d in os.listdir(os.path.join(AQUI, 'temporadas')) if os.path.isdir(os.path.join(AQUI, 'temporadas')) else []:
        q = os.path.join(AQUI, 'temporadas', d, 'firebase.js')
        if os.path.exists(q):
            shutil.copy2(ARCH, q)
            print('     tambien en temporadas/%s' % d)

    print()
    print('  ' + '-' * 62)
    print('     Listo. Queda una copia en firebase.js.antes')
    print('     Ahora publica y proba con una cuenta de JUGADOR.')
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
