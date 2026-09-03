# -*- coding: utf-8 -*-
"""
MEJORAS_2_SEPTIEMBRE.py
=======================

Aplica a un club —o a la PLANTILLA— las cuatro mejoras del 2 de septiembre.

Funciona igual sobre GELP, sobre la plantilla o sobre cualquier club: no toca
nada propio de cada uno (ni el nombre, ni la base, ni las marcas {{CLUB}}).

── QUE AGREGA ────────────────────────────────────────────────────────────────

  1. EQUIPO — el plantel completo y con nombres
     Mostraba solo a los que YA JUGARON, porque leia el archivo que se genera
     al procesar los .dvw. Un jugador nuevo no aparecia hasta su debut, aunque
     tuviera cuenta y cargara wellness. Y si se lo agregaba a mano, el
     siguiente HACER_TODO lo borraba.

     Ahora la base es el plantel del club, que es la lista real y nadie la
     pisa. Ademas se ve el nombre de pila debajo del apellido.

  2. PREPARACION FISICA — los dos pesos de una superserie
     Un "Banco Plano + Fondos" son dos ejercicios con pesos distintos. Habia
     una sola fila y no se sabia cual era cual.

  3. PIZARRON — las dos columnas de una superserie
     Lo mismo en la tabla del profe: cada serie lleva dos casilleros.

  4. WELLNESS — ver por semana, quincena o mes
     La tabla del equipo mostraba UN dia. Ahora se elige el periodo y
     promedia, mostrando cuantos dias cargo cada uno.

── COMO SE USA ───────────────────────────────────────────────────────────────
    Copiar a la carpeta del club (o de la PLANTILLA) y hacer doble clic.
    De cada pantalla tocada queda una copia .antes-mejoras
"""

import io
import os
import re
import shutil
import sys
import glob

AQUI = os.path.dirname(os.path.abspath(__file__))


def leer(f):
    try:
        return io.open(os.path.join(AQUI, f), encoding='utf-8', errors='replace').read()
    except Exception:
        return None


def guardar(f, s):
    ruta = os.path.join(AQUI, f)
    respaldo = ruta + '.antes-mejoras'
    if not os.path.exists(respaldo):
        try:
            shutil.copy2(ruta, respaldo)
        except Exception:
            pass
    io.open(ruta, 'w', encoding='utf-8').write(s)


def equipo():
    s = leer('equipo.html')
    if s is None:
        return 'no esta la pantalla'
    if 'j.pila' in s:
        return 'ya estaba'

    plantel = None
    for cand in sorted(glob.glob(os.path.join(AQUI, 'plantel_*.js'))):
        n = os.path.basename(cand)
        if 'desde_dvw' in n:
            continue
        t = io.open(cand, encoding='utf-8', errors='replace').read()
        m = re.search(r'window\.(\w+)\s*=', t)
        if m:
            plantel = (n, m.group(1))
            break
    if not plantel:
        return 'no encontre el plantel del club'

    archivo, variable = plantel

    if archivo not in s:
        m = re.search(r'<script src="datos_equipo\.js\.enc"[^>]*></script>', s)
        if not m:
            return 'no encontre donde cargar el plantel'
        s = s.replace(m.group(0),
                      '<!-- El plantel del club: la lista real, con nombre y apellido.\n'
                      '     datos_equipo.js.enc solo trae a los que YA jugaron. -->\n'
                      '<script src="' + archivo + '" onerror="void 0"></script>\n'
                      + m.group(0), 1)

    V = 'var DATA = window.EQUIPO_DATA || EQUIPO_DEMO;'
    if V not in s:
        return 'la pantalla tiene otra forma: no la toco'

    N = ('/* El plantel sale de la lista del club, no de los partidos: asi un\n'
         '   jugador nuevo aparece aunque todavia no haya debutado. */\n'
         'var DATA = (function(){\n'
         '  var base  = window.EQUIPO_DATA || EQUIPO_DEMO;\n'
         '  var lista = (window.' + variable + ' && window.' + variable + '.jugadores) || null;\n'
         '  if(!lista || !lista.length) return base;\n'
         '  var dePartidos = {};\n'
         '  (base.jugadores || []).forEach(function(j){ dePartidos[j.num] = j; });\n'
         '  return { jugadores: lista.map(function(p){\n'
         '             var e = dePartidos[p.num] || {};\n'
         "             return { num:p.num, nombre:p.ap || e.nombre || '', pila:p.nombre || '',\n"
         "                      pos:p.pos || e.pos || '', foto:e.foto || null,\n"
         "                      pais:e.pais || '', altura:e.altura || '', edad:e.edad || 0 };\n"
         '           }),\n'
         '           staff: base.staff || EQUIPO_DEMO.staff };\n'
         '})();')
    s = s.replace(V, N, 1)

    s = s.replace('DATA = window.EQUIPO_DATA;', 'DATA.__base = window.EQUIPO_DATA;', 1)

    V2 = "'<div class=\"jug-card-nombre\">' + j.nombre + '</div>' +"
    if V2 in s:
        s = s.replace(V2,
                      "'<div class=\"jug-card-nombre\">' + j.nombre +\n"
                      "        (j.pila ? '<div style=\"font-size:11px;font-weight:400;opacity:.6;'\n"
                      "                + 'letter-spacing:.5px;margin-top:2px\">' + j.pila + '</div>' : '') +\n"
                      "      '</div>' +", 1)

    guardar('equipo.html', s)
    return 'listo'


def prep():
    s = leer('prep_fisica.html')
    if s is None:
        return 'no esta la pantalla'
    if '_nom2' in s:
        return 'ya estaba'

    m = re.search(r"pesosLabel\.textContent = tP\('registra'\);", s)
    if not m:
        return 'la pantalla tiene otra forma: no la toco'

    s = s.replace(m.group(0),
                  "var _nom2 = (ej.nombre2 && ej.id2) ? ej.nombre2 : null;\n"
                  "  if(_nom2){\n"
                  "    /* Superserie: la fila lleva el nombre del primer movimiento. */\n"
                  "    pesosLabel.innerHTML = '<span style=\"color:#2dd4bf;font-weight:700\">' +\n"
                  "      (ej.nombre || '') + '</span><span style=\"opacity:.55\"> · ' +\n"
                  "      tP('registra') + '</span>';\n"
                  "  } else {\n"
                  "    pesosLabel.textContent = tP('registra');\n"
                  "  }", 1)

    V = re.search(r"pesosDiv\.appendChild\(pesosGrid\);\s*\n\s*card\.appendChild\(pesosDiv\);", s)
    if not V:
        return 'no encontre donde agregar la segunda fila'

    s = s.replace(V.group(0), V.group(0) + """

  /* La segunda fila, para el otro movimiento. Usa el id2 que ya trae la
     rutina, asi el peso se guarda igual que si fuera un ejercicio suelto. */
  if(_nom2){
    var pesos2 = document.createElement('div');
    pesos2.className = 'pesos-section';
    pesos2.style.borderTop = '1px dashed rgba(255,255,255,.10)';
    var label2 = document.createElement('div');
    label2.className = 'pesos-label';
    label2.innerHTML = '<span style="color:#a5b4fc;font-weight:700">' + _nom2 +
      '</span><span style="opacity:.55"> · ' + tP('registra') + '</span>';
    pesos2.appendChild(label2);
    var grid2 = document.createElement('div');
    grid2.className = 'pesos-grid';
    for(var s2 = 1; s2 <= ej.series; s2++){
      (function(nSerie){
        var k2 = storageKey(j.num, ej.id2, nSerie);
        var item = document.createElement('div');
        item.className = 'serie-item';
        var lab = document.createElement('div');
        lab.className = 'serie-num';
        lab.textContent = tP('serie') + ' ' + nSerie;
        var inp2 = document.createElement('input');
        inp2.type = 'number';
        inp2.className = 'peso-input';
        inp2.placeholder = '\\u2014 kg';
        inp2.min = '0'; inp2.max = '500'; inp2.step = '0.5';
        inp2.value = localStorage.getItem(k2) || '';
        inp2.addEventListener('change', function(){
          var v = inp2.value.trim();
          try{ localStorage.setItem(k2, v); }catch(e){}
          try{ if(typeof fbSet !== 'undefined') fbSet('pesos/' + k2, v === '' ? null : v); }catch(e){}
        });
        item.appendChild(lab); item.appendChild(inp2);
        grid2.appendChild(item);
      })(s2);
    }
    pesos2.appendChild(grid2);
    card.appendChild(pesos2);
  }""", 1)

    guardar('prep_fisica.html', s)
    return 'listo'


def pizarron():
    s = leer('pizarron.html')
    if s is None:
        return 'no esta la pantalla'
    if 'esSuper' in s:
        return 'ya estaba'

    m = re.search(r"bloques\[b\.nombre\]\.ejercicios\[e\.id\]=\{[^}]*\};", s)
    if m and 'id2' not in m.group(0):
        s = s.replace(m.group(0),
                      m.group(0)[:-2] + ',id2:e.id2,nombre2:e.nombre2,reps2:e.reps2,video2:e.video2};', 1)

    m = re.search(r'id:e\.id, nombre:e\.nombre, series:e\.series,', s)
    if m:
        s = s.replace(m.group(0),
                      m.group(0) + '\n            id2:e.id2, nombre2:e.nombre2, reps2:e.reps2, video2:e.video2,', 1)

    m = re.search(r"'<div class=\"ej-nombre\">' \+ ejNombre\(ej\.id, ej\.nombre\) \+ '</div>' \+", s)
    if m:
        s = s.replace(m.group(0),
                      "'<div class=\"ej-nombre\">' + ejNombre(ej.id, ej.nombre)\n"
                      "        + (ej.nombre2 ? ' <span style=\"opacity:.75\">+</span> ' + ejNombre(ej.id2, ej.nombre2)\n"
                      "             + ' <span class=\"ej-badge\" style=\"background:rgba(129,140,248,.18);'\n"
                      "             + 'color:#a5b4fc;font-size:9px;vertical-align:middle\">SUPERSERIE</span>'\n"
                      "           : '')\n"
                      "        + '</div>' +", 1)

    s = s.replace("'<span class=\"ej-badge badge-r\">' + ej.reps + ' REPS</span>' +",
                  "'<span class=\"ej-badge badge-r\">' + ej.reps + (ej.reps2 ? ' + ' + ej.reps2 : '') + ' REPS</span>' +", 1)

    m = re.search(r"var thead = '<thead><tr><th>#</th><th>Jugador</th><th>Posici\u00f3n</th>';\s*\n\s*for\(var s=1; s<=ej\.series; s\+\+\) thead \+= '<th class=\"center\">SERIE '\+s\+'</th>';\s*\n\s*thead \+= '</tr></thead>';", s)
    if not m:
        guardar('pizarron.html', s)
        return 'parcial: los nombres si, las columnas no (otra forma)'

    s = s.replace(m.group(0),
                  "/* Si el ejercicio es combinado, cada serie lleva DOS columnas. */\n"
                  "    var esSuper = !!(ej.nombre2 && ej.id2);\n"
                  "    var thead = '<thead><tr><th>#</th><th>Jugador</th><th>Posici\u00f3n</th>';\n"
                  "    for(var s=1; s<=ej.series; s++){\n"
                  "      if(esSuper){\n"
                  "        thead += '<th class=\"center\" style=\"font-size:9px;color:#2dd4bf\">S'+s+' \u00b7 '+\n"
                  "                 (ej.nombre||'').slice(0,12)+'</th>';\n"
                  "        thead += '<th class=\"center\" style=\"font-size:9px;color:#a5b4fc\">S'+s+' \u00b7 '+\n"
                  "                 (ej.nombre2||'').slice(0,12)+'</th>';\n"
                  "      } else {\n"
                  "        thead += '<th class=\"center\">SERIE '+s+'</th>';\n"
                  "      }\n"
                  "    }\n"
                  "    thead += '</tr></thead>';", 1)

    i = s.find('// Series editables')
    j = s.find('tbody.appendChild(tr)', i)
    if i > 0 and j > i:
        s = s[:i] + """/* Una celda por movimiento, con la misma clave que usa la app del
           jugador: lo que carga cada uno se ve aca y al reves. */
        function celdaPeso(numJug, idEj, serie){
          var td = document.createElement('td');
          td.className = 'peso-cell';
          var storKey = sk(numJug, idEj, serie);
          var saved = localStorage.getItem(storKey) || '';
          var inp = document.createElement('input');
          inp.type = 'number';
          inp.className = 'peso-inp' + (saved ? ' filled' : '');
          inp.placeholder = '\\u2014';
          inp.value = saved;
          inp.min = 0; inp.max = 500; inp.step = 0.5;
          if(typeof fbGet !== 'undefined'){
            (function(k, input){
              fbGet('pesos/'+k, function(val){
                if(val !== null && val !== ''){
                  input.value = val; input.classList.add('filled');
                  localStorage.setItem(k, val);
                }
              });
            })(storKey, inp);
          }
          inp.addEventListener('input', (function(k, input){
            return function(){
              var v = this.value;
              localStorage.setItem(k, v);
              input.classList.toggle('filled', v !== '');
              if(typeof fbSet !== 'undefined') fbSet('pesos/'+k, v);
              updateLastUpdate();
            };
          })(storKey, inp));
          td.appendChild(inp);
          return td;
        }

        for(var serie=1; serie<=ej.series; serie++){
          tr.appendChild(celdaPeso(j.num, ej.id, serie));
          if(esSuper) tr.appendChild(celdaPeso(j.num, ej.id2, serie));
        }

        """ + s[j:]

    guardar('pizarron.html', s)
    return 'listo'


def wellness():
    s = leer('wellness.html')
    if s is None:
        return 'no esta la pantalla'
    if 'eqPeriodo' in s:
        return 'ya estaba'

    V = '<div><label class="fld">D\u00eda</label><input type="date" id="eqFecha"></div>'
    if V not in s:
        return 'la pantalla tiene otra forma: no la toco'

    s = s.replace(V, '<div><label class="fld">Hasta el d\u00eda</label><input type="date" id="eqFecha"></div>\n'
                     '          <div><label class="fld">Per\u00edodo</label>\n'
                     '            <select id="eqPeriodo">\n'
                     '              <option value="1">Solo ese d\u00eda</option>\n'
                     '              <option value="7">\u00daltima semana</option>\n'
                     '              <option value="15">\u00daltima quincena</option>\n'
                     '              <option value="30">\u00daltimo mes</option>\n'
                     '            </select>\n'
                     '          </div>', 1)

    s = s.replace("document.getElementById('eqFecha').onchange=renderTeam;",
                  "document.getElementById('eqFecha').onchange=renderTeam;\n"
                  "  document.getElementById('eqPeriodo').onchange=renderTeam;", 1)

    m = re.search(r"var dayRows=\[\];\s*\n\s*roster\(\)\.forEach\(function\(j\)\{\s*\n\s*var es=all\.filter\(function\(e\)\{ return e\.num===j\.num && e\.date===date && \(!ses\|\|e\.sesion===ses\); \}\);", s)
    if not m:
        guardar('wellness.html', s)
        return 'parcial: el selector si, el promedio no (otra forma)'

    s = s.replace(m.group(0),
                  "/* El periodo elegido: promedia todas las encuestas de cada jugador\n"
                  "     en ese rango, en vez de mostrar un solo dia. */\n"
                  "  var dias = parseInt(document.getElementById('eqPeriodo').value, 10) || 1;\n"
                  "  var hasta = new Date(date + 'T12:00:00');\n"
                  "  var desde = new Date(hasta);\n"
                  "  desde.setDate(desde.getDate() - (dias - 1));\n"
                  "  function enRango(f){\n"
                  "    var d = new Date(f + 'T12:00:00');\n"
                  "    return d >= desde && d <= hasta;\n"
                  "  }\n\n"
                  "  var dayRows=[];\n"
                  "  roster().forEach(function(j){\n"
                  "    var es=all.filter(function(e){\n"
                  "      return e.num===j.num && enRango(e.date) && (!ses||e.sesion===ses);\n"
                  "    });", 1)

    m2 = re.search(r"dayRows\.push\(\{j:j, pct:pct, rpe:rpe, prom:prom, ses:[^}]*\}\);", s)
    if m2:
        s = s.replace(m2.group(0),
                      "var diasDistintos = {};\n"
                      "    es.forEach(function(e){ diasDistintos[e.date] = 1; });\n    "
                      + m2.group(0)[:-3] + ", cuantas:Object.keys(diasDistintos).length});", 1)

    m3 = re.search(r"var h='<table><thead><tr><th>Jugador</th><th>Pos</th><th>RPE</th>", s)
    if m3:
        s = s.replace(m3.group(0),
                      "var h='<table><thead><tr><th>Jugador</th><th>Pos</th>'\n"
                      "    + (dias>1 ? '<th>Carg\u00f3</th>' : '')\n"
                      "    + '<th>RPE</th>", 1)

    m4 = re.search(r"\+'<td class=\"muted\">'\+\(POSAB\[r\.j\.pos\]\|\|r\.j\.pos\)\+'</td>'", s)
    if m4:
        s = s.replace(m4.group(0), m4.group(0) +
                      "\n      + (dias>1\n"
                      "          ? '<td class=\"muted\" style=\"white-space:nowrap\"><b style=\"color:'\n"
                      "            + (r.cuantas>=dias*0.6?'var(--green)':r.cuantas>=dias*0.3?'var(--orange)':'var(--red)')\n"
                      "            + '\">' + r.cuantas + '</b><span style=\"opacity:.5\"> de ' + dias + '</span></td>'\n"
                      "          : '')", 1)

    guardar('wellness.html', s)
    return 'listo'


def main():
    print()
    print('  ' + '=' * 62)
    print('     MEJORAS DEL 2 DE SEPTIEMBRE')
    print('  ' + '=' * 62)
    print()

    if not glob.glob(os.path.join(AQUI, '*.html')):
        print('     No encontre pantallas en esta carpeta.')
        print('     Copia este programa a la carpeta del club o de la plantilla.')
        print()
        return 1

    tareas = [('EQUIPO \u2014 plantel completo y con nombres', equipo),
              ('PREP. FISICA \u2014 los dos pesos de la superserie', prep),
              ('PIZARRON \u2014 las dos columnas de la superserie', pizarron),
              ('WELLNESS \u2014 ver por semana, quincena o mes', wellness)]

    print('     Se van a aplicar 4 mejoras.')
    print('     De cada pantalla queda una copia .antes-mejoras')
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
    for nombre, fn in tareas:
        try:
            res = fn()
        except Exception as e:
            res = 'ERROR: %s' % e
        print('     %-46s %s' % (nombre, res))

    print()
    print('  ' + '-' * 62)
    print('     Ahora corre REVISAR_ANTES_DE_PUBLICAR.py')
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
