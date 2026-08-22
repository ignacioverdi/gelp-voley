/* ═══════════════════════════════════════════════════════════════════════════
   selector_categoria.js — CAMBIAR DE CATEGORIA EN LA APP

   Un club puede tener Primera, Sub-21, Sub-18... Cada una tiene sus propios
   datos, en su carpeta: las pantallas son las mismas, lo que cambia es de
   donde se cargan.

   Este archivo hace dos cosas:

     1. pone el selector arriba, al lado del de temporada
     2. redirige los datos a la carpeta de la categoria elegida

   Si el club tiene UNA sola categoria no hace nada: el selector no aparece y
   todo funciona como siempre. Un club de un solo equipo no se entera de que
   esto existe.
   ═══════════════════════════════════════════════════════════════════════════ */
(function(){
  'use strict';

  var GUARDA = 'vb_categoria';

  function cats(){
    try{
      var c = window.CATEGORIAS_CLUB;
      return (c && c.length) ? c : [];
    }catch(e){ return []; }
  }

  function norm(c){
    return String(c || '').replace(/[^A-Za-z0-9]/g, '').toUpperCase();
  }

  /* La categoria elegida. La primera de la lista es la que abre por defecto:
     casi siempre Primera, que es lo que el club mira todos los dias. */
  function actual(){
    var L = cats();
    if(L.length < 2) return L[0] || 'Primera';
    var g = '';
    try{ g = localStorage.getItem(GUARDA) || ''; }catch(e){}
    return (g && L.indexOf(g) >= 0) ? g : L[0];
  }
  window.categoriaActual = actual;

  /* La carpeta donde viven los datos de esta categoria. Primera queda en la
     raiz —donde estuvo siempre— asi los clubes que ya andan no cambian. */
  function carpeta(){
    var L = cats();
    if(L.length < 2) return '';
    var c = actual();
    if(!c || c === L[0]) return '';
    return 'cat/' + norm(c) + '/';
  }
  window.carpetaCategoria = carpeta;

  /* ══ Redirigir los datos ═════════════════════════════════════════════════
     Las pantallas piden sus archivos con <script src="liga_data.js.enc">. En
     vez de tocar las 52 pantallas una por una, se intercepta la creacion de
     esas etiquetas y se les cambia la ruta.

     Solo se tocan los archivos de DATOS: las pantallas, los estilos y los
     motores se comparten entre categorias. */
  var ES_DATO = /^(liga_data|datos_|nla_|mapa_videos|plan_partido_data|scouting_rival)/;

  function redirigir(){
    var pre = carpeta();
    if(!pre) return;                    /* Primera: nada que redirigir */
    var crear = document.createElement.bind(document);
    document.createElement = function(tag){
      var el = crear(tag);
      if(String(tag).toLowerCase() !== 'script') return el;
      try{
        var setSrc = Object.getOwnPropertyDescriptor(
          HTMLScriptElement.prototype, 'src');
        Object.defineProperty(el, 'src', {
          get: function(){ return setSrc.get.call(el); },
          set: function(v){
            var s = String(v);
            var f = s.split('/').pop().split('?')[0];
            if(ES_DATO.test(f) && s.indexOf('cat/') < 0) s = pre + s;
            setSrc.set.call(el, s);
          }
        });
      }catch(e){}
      return el;
    };
  }

  /* ══ El selector ══════════════════════════════════════════════════════════
     Se pone al lado del de temporada, que es donde el entrenador ya busca
     este tipo de cosas. Si esa barra no existe en la pantalla, se muestra
     flotando arriba a la derecha. */
  function pintar(){
    var L = cats();
    if(L.length < 2) return;             /* una sola: no se muestra */

    var sel = document.createElement('select');
    sel.id = 'catSelGlobal';
    sel.title = 'Categoría';
    sel.style.cssText = 'background:var(--card2,#12132a);color:var(--txt,#e2e8f0);'
      + 'border:1px solid rgba(255,255,255,.14);border-radius:8px;padding:5px 9px;'
      + 'font-family:inherit;font-size:12px;font-weight:700;cursor:pointer;'
      + 'letter-spacing:.5px';
    sel.innerHTML = L.map(function(c){
      return '<option value="' + c + '"' + (c === actual() ? ' selected' : '') + '>'
           + c + '</option>';
    }).join('');

    sel.addEventListener('change', function(){
      try{ localStorage.setItem(GUARDA, sel.value); }catch(e){}
      location.reload();                 /* los datos se cargan al abrir */
    });

    var destino = document.querySelector('.tempbar, .topbar, header .right, header');
    if(destino){
      destino.appendChild(sel);
    } else {
      var caja = document.createElement('div');
      caja.style.cssText = 'position:fixed;top:10px;right:12px;z-index:9998';
      caja.appendChild(sel);
      document.body.appendChild(caja);
    }
  }

  redirigir();                           /* antes de que carguen los datos */
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', pintar);
  } else {
    pintar();
  }
})();

/* © 2025-2026 Ignacio Verdi · GELP VOLEY · Software propietario */
