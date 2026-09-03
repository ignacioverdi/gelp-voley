# -*- coding: utf-8 -*-
"""
ARREGLAR_SCOUT_VIVO.py
======================

Los cuatro arreglos del scout en vivo, segun el manual de DataVolley 4.

Se corre en la carpeta de un club o en la PLANTILLA.

── 1. Ctrl+A REABRE EL PUNTO ─────────────────────────────────────────────────
Habia DOS manejadores para Ctrl+A: uno llamaba a reabrirPunto() y otro a
undoLast(). Como el segundo se registra despues, ganaba: Ctrl+A terminaba
borrando la ultima accion en vez de reabrir el rally completo.

En el manual (1.1) Ctrl+A selecciona todo el rally.

── 2. DESHACER, EN SU PROPIA TECLA ───────────────────────────────────────────
Queda en F4 y se puede cambiar desde Configuracion.

── 3. EL TIME-CODE DE CADA ACCION ────────────────────────────────────────────
El manual (2.5.6) lo muestra al lado de cada codigo: es lo que deja ver de un
vistazo si el rally quedo bien alineado al video, sin ir tocando uno por uno.

Las acciones sin alinear muestran un guion.

── 4. LA SECCION "TECLAS DEL VIDEO" ──────────────────────────────────────────
En Configuracion, para cambiar:

    la tecla de alineacion        (era F2, fija)
    la tecla de deshacer          (nueva)
    pasar al codigo siguiente     (manual 2.5.6 punto 1)
    saltar al video al elegir     (idem)

Las dos casillas existian en el codigo pero no tenian control visible.

── COMO SE USA ───────────────────────────────────────────────────────────────
    Copiar a la carpeta y hacer doble clic. Despues, PUBLICAR.bat
"""

import io
import os
import re
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
ARCH = os.path.join(AQUI, 'panel_vivo.html')

CSS = """
/* El tiempo de video de cada accion, a la derecha y en gris: se lee
   cuando lo buscas y no molesta mientras scouteas. */
.crow .tcode{ margin-left:auto; padding-left:10px; font-size:11px;
  color:#64748b; font-family:'JetBrains Mono',monospace; letter-spacing:.5px; }
.crow .tcode.sin{ color:#334155; }
.crow.sel .tcode{ color:#94a3b8; }
</style>"""

SECCION = '''<div class="sec">
        <h4>Teclas del video</h4>
        <p>El manual (2.5.6) las llama <em>shortcut keys</em> de sincronización.
           Podés poner cualquier tecla: F2, F3, una letra, la que te quede cómoda.</p>

        <div class="fgrid">
          <div>
            <label class="f">Alinear el código al video</label>
            <div class="keycap" data-key="__sync" onclick="listen(this)">F2</div>
            <div class="sub">Apretala mientras corre el video: el código seleccionado
              queda alineado a ese momento.</div>
          </div>
          <div>
            <label class="f">Deshacer la última acción</label>
            <div class="keycap" data-key="__undo" onclick="listen(this)">F4</div>
            <div class="sub">Antes era Ctrl+A, pero esa combinación reabre el punto
              completo, como dice el manual.</div>
          </div>
        </div>

        <div style="margin-top:10px">
          <label style="display:flex;align-items:center;gap:8px;cursor:pointer">
            <input type="checkbox" id="cfg-video-avanza">
            <span>Después de alinear, pasar al código siguiente</span>
          </label>
          <div class="sub">Así vas alineando el rally entero sin tocar la lista.</div>
        </div>

        <div style="margin-top:8px">
          <label style="display:flex;align-items:center;gap:8px;cursor:pointer">
            <input type="checkbox" id="cfg-video-salta">
            <span>Al elegir un código, saltar ahí en el video</span>
          </label>
          <div class="sub">Para revisar si quedó bien alineado.</div>
        </div>
      </div>

      '''


def main():
    print()
    print('  ' + '=' * 62)
    print('     EL SCOUT EN VIVO')
    print('  ' + '=' * 62)
    print()

    if not os.path.exists(ARCH):
        print('     No encontre panel_vivo.html en esta carpeta.')
        print()
        return 1

    s = io.open(ARCH, encoding='utf-8', errors='replace').read()

    falta = []
    if "e.key.toLowerCase()==='a'){ e.preventDefault(); undoLast(); return; }" in s:
        falta.append('Ctrl+A: sacar el manejador que lo pisa')
    if 'CFG.keys.undo' not in s:
        falta.append('deshacer en su propia tecla (F4)')
    if 'class="tcode"' not in s:
        falta.append('el time-code de cada accion')
    if 'Teclas del video' not in s:
        falta.append('la seccion en Configuracion')

    if not falta:
        print('  ' + '-' * 62)
        print('     El scout ya esta al dia.')
        print()
        return 0

    print('     Falta:')
    for x in falta:
        print('       · ' + x)
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
    hechos = []

    # 1 · Ctrl+A
    V = "if((e.ctrlKey||e.metaKey) && e.key.toLowerCase()==='a'){ e.preventDefault(); undoLast(); return; }"
    if V in s:
        N = """/* ── Ctrl+A ES REABRIR EL PUNTO, NO DESHACER ──────────────────────
       Habia DOS manejadores para Ctrl+A. El de mas abajo ganaba, y por eso
       Ctrl+A borraba la ultima accion en vez de reabrir el rally completo.
       En el manual (1.1) Ctrl+A selecciona todo el rally. */
    if(CFG.keys.undo && e.key===CFG.keys.undo && !e.ctrlKey && !e.altKey){
      e.preventDefault(); undoLast(); return;
    }"""
        s = s.replace(V, N, 1)
        hechos.append('Ctrl+A reabre el punto')

    # 2 · la tecla de deshacer
    V2 = "if(!CFG.keys.sync) CFG.keys.sync = 'F2';"
    if V2 in s and 'CFG.keys.undo =' not in s:
        s = s.replace(V2, V2 + "\n  if(!CFG.keys.undo) CFG.keys.undo = 'F4';"
                      "                  /* deshacer (Ctrl+A quedo para reabrir el punto) */", 1)
        hechos.append('deshacer en F4, configurable')

    # 3 · el time-code
    m = re.search(r"return '<div class=\"crow '\+cls\+sel\+'\" onclick=\"seleccionar\('\+i\+'\)\"[^\n]*?\+codigoEnColumnas\(c\.c\)\+'</div>';", s)
    if m and 'class="tcode"' not in s:
        nuevo = ("""/* El time-code de cada accion (manual 2.5.6): deja ver de un
         vistazo si el rally quedo bien alineado al video. */
      var _tc = (c.t!=null && c.t>0)
        ? '<span class="tcode">'+hhmmss(c.t)+'</span>'
        : '<span class="tcode sin">\\u2014</span>';
      """ + m.group(0).replace("+'</div>';", "+_tc+'</div>';"))
        s = s.replace(m.group(0), nuevo, 1)
        i = s.find('</style>')
        if i > 0:
            s = s[:i] + CSS + s[i + len('</style>'):]
        hechos.append('time-code en cada accion')

    # 4 · la seccion de configuracion
    m2 = re.search(r'<div class="sec">\s*<h4>Atajos propios</h4>', s)
    if m2 and 'Teclas del video' not in s:
        s = s.replace(m2.group(0), SECCION + m2.group(0), 1)

        # cargar los valores al abrir
        V3 = "function openConfig(){\n  const ev = document.getElementById('cfg-eval');"
        if V3 in s:
            s = s.replace(V3, """function openConfig(){
  /* Las teclas del video y las casillas de alineacion (manual 2.5.6). */
  try{
    var _ks=document.querySelector('.keycap[data-key="__sync"]');
    if(_ks) _ks.textContent = CFG.keys.sync || 'F2';
    var _ku=document.querySelector('.keycap[data-key="__undo"]');
    if(_ku) _ku.textContent = CFG.keys.undo || 'F4';
    var _va=document.getElementById('cfg-video-avanza');
    if(_va) _va.checked = CFG.videoAvanza !== false;
    var _vs=document.getElementById('cfg-video-salta');
    if(_vs) _vs.checked = CFG.videoSalta !== false;
  }catch(e){}
  const ev = document.getElementById('cfg-eval');""", 1)

        # guardarlos
        m4 = re.search(r"function saveConfig\(\)\{\s*\n\s*if\(!document\.getElementById\('m-config'\)[^\n]*\n", s)
        if m4:
            s = s.replace(m4.group(0), m4.group(0) + """  /* Las teclas del video y las casillas. Van aparte de las teclas de
     accion porque no compiten: una es F2 y las otras son letras. */
  try{
    var _ks=document.querySelector('.keycap[data-key="__sync"]');
    if(_ks){ var _t=_ks.textContent.trim(); if(_t && _t!=='\\u2026' && _t!=='\\u2014') CFG.keys.sync=_t; }
    var _ku=document.querySelector('.keycap[data-key="__undo"]');
    if(_ku){ var _u=_ku.textContent.trim(); if(_u && _u!=='\\u2026' && _u!=='\\u2014') CFG.keys.undo=_u; }
    var _va=document.getElementById('cfg-video-avanza');
    if(_va) CFG.videoAvanza=_va.checked;
    var _vs=document.getElementById('cfg-video-salta');
    if(_vs) CFG.videoSalta=_vs.checked;
  }catch(e){}
""", 1)
        hechos.append('seccion "Teclas del video"')

    resp = ARCH + '.antes-scout'
    if not os.path.exists(resp):
        try:
            shutil.copy2(ARCH, resp)
        except Exception:
            pass
    io.open(ARCH, 'w', encoding='utf-8').write(s)

    # y la copia de la temporada archivada
    tem = os.path.join(AQUI, 'temporadas')
    if os.path.isdir(tem):
        for d in os.listdir(tem):
            q = os.path.join(tem, d, 'panel_vivo.html')
            if os.path.exists(q):
                shutil.copy2(ARCH, q)

    for h in hechos:
        print('       %s' % h)

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
