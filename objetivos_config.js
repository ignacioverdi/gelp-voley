/* ═══════════════════════════════════════════════════════════════════════════
   LAS FORMULAS, EN UN SOLO LUGAR

   Antes cada pantalla tenia su propia copia de la cuenta: 28 copias repartidas
   en ocho archivos, con nombres de variable distintos en cada una (j.sPunto,
   a.sPunto, t.sPunto, src.Punto, k, pl, bl...). Cambiar un peso obligaba a
   acertarle a las 28. En la practica siempre quedaba alguna afuera, y una
   pantalla mostraba un numero distinto al resto sin que nadie entendiera por
   que. Tres veces seguidas paso lo mismo con el mismo cambio.

   Ahora la cuenta vive aca y todas las pantallas la llaman. Cambiar un peso
   es tocar UN solo lugar.

   Las funciones reciben un objeto con los conteos y devuelven el numero
   redondeado, o null si no hay acciones. Aceptan los distintos nombres que
   usa cada pantalla, asi que sirven tal cual esten los datos.

   ESCALA 0 a 100:  el error vale 0, el ace o la perfecta 100, el neutro 50.
     SAQUE       #  100    /  87,5   +  75    !  50    -  25    =  0
     RECEPCION   #  100    +  75     !  50    -  25    /  12,5  =  0
     DEFENSA     #  100    +  75     !  50    -  25            =  0
     ATAQUE      punto 100, bloqueado y error 0, el resto 50
   ═══════════════════════════════════════════════════════════════════════════ */
(function(){
  function n(v){ return (typeof v === 'number' && isFinite(v)) ? v : 0; }
  /* Toma el primer nombre que exista: cada pantalla llama distinto al mismo dato. */
  function g(o, nombres){
    for(var i=0;i<nombres.length;i++){
      var v=o[nombres[i]];
      if(v!==undefined && v!==null) return n(v);
    }
    return 0;
  }
  function redondear(x){ return Math.round(x); }

  window.VB_EFF = {
    /* SAQUE: # ace · / free ball · + positivo · ! neutro · - negativo · = error */
    saque: function(o){
      if(!o) return null;
      var T = g(o,['sT','T','tot','total']);
      if(!T) return null;
      var ace  = g(o,['sPunto','Punto','pts','ace','perf','k']);
      var free = g(o,['sVend','Vend','slash','over','sl','bl']);
      var pos  = g(o,['sPos','Pos','plus','pos','pl','p']);
      var ntr  = g(o,['sAdm','Adm','ntr','nt','exc','reg']);
      var neg  = g(o,['sNeg','Neg','neg','ng']);
      return redondear((ace + 0.875*free + 0.75*pos + 0.5*ntr + 0.25*neg)/T*100);
    },
    /* RECEPCION: # perfecta · + positiva · ! neutra · - negativa · / sobrepase · = error */
    recepcion: function(o){
      if(!o) return null;
      var T = g(o,['rT','T','tot','total']);
      if(!T) return null;
      /* 'over' es como llaman al sobrepase armadores y game_plan; sin el,
         esas dos pantallas daban 37 donde el resto daba 59. */
      var perf = g(o,['rPunto','Punto','pts','perf','k']);
      var pos  = g(o,['rPos','Pos','plus','pos','pl','p','mas']);
      var ntr  = g(o,['rAdm','Adm','ntr','nt','exc','reg']);
      var neg  = g(o,['rNeg','Neg','neg','ng']);
      var sob  = g(o,['rVend','Vend','over','ovp','slash','sl','bl']);
      return redondear((perf + 0.75*pos + 0.5*ntr + 0.25*neg + 0.125*sob)/T*100);
    },
    /* DEFENSA: mismo criterio que recepcion, sin sobrepase. */
    defensa: function(o){
      if(!o) return null;
      var T = g(o,['dT','defT','T','tot','total']);
      if(!T) return null;
      var perf = g(o,['dPerf','defPerf','Punto','perf','pt']);
      var buena= g(o,['dBuena','defBuena','Pos','plus','buena','pos']);
      var ntr  = g(o,['dAdm','defAdm','Adm','ntr','reg']);
      var mala = g(o,['dMala','defMala','Neg','neg','mala']);
      return redondear((perf + 0.75*buena + 0.5*ntr + 0.25*mala)/T*100);
    },
    /* ATAQUE: la formula de siempre, la eficacia clasica del voley.
       (punto - bloqueado - error) / total. NO se toco: es un estandar
       mundial y los objetivos de ataque estan calibrados sobre ella.
       Ojo: esta escala NO es la de 0 a 100 de saque y recepcion; el ataque
       puede dar negativo y eso esta bien, asi se mide en todos lados. */
    ataque: function(o){
      if(!o) return null;
      var T = g(o,['aT','T','tot','total']);
      if(!T) return null;
      var pt  = g(o,['aPunto','Punto','pts','k']);
      var blq = g(o,['aVend','Vend','slash','bl']);
      var err = g(o,['aErr','Err','err','e']);
      return redondear((pt - blq - err)/T*100);
    }
  };
})();


/* ── LA TEMPORADA QUE SE ESTA MOSTRANDO ────────────────────────────────────
   El titulo decia "2026" escrito a mano: al empezar la temporada nueva
   seguia diciendo el año viejo. Ahora lo pregunta.
   Lo busca donde ya esta, en este orden, y si no encuentra nada no muestra
   ningun año en vez de mostrar uno equivocado.
   ────────────────────────────────────────────────────────────────────────── */
window.__TEMP_TITULO = (function () {
  try {
    var t = (window.LIGA_DATA && (window.LIGA_DATA.temporada ||
             window.LIGA_DATA.season)) ||
            (window.TEMPORADA_ACTUAL) ||
            (document.body && document.body.dataset && document.body.dataset.temporada);
    if (t) return ' \u00b7 ' + t;
    var m = (location.pathname.match(/temporadas\/(\d{4}-\d{2})/) || [])[1];
    if (m) return ' \u00b7 ' + m.replace('-', '/');
  } catch (e) {}
  return '';
})();

// objetivos_config.js — NÄFELS Voley
// Configuracion compartida de baterias y objetivos
// Importar en: jugador.html, dashboard.html, historial_voley.html

window./* ── DE DONDE SALEN ESTOS OBJETIVOS ────────────────────────────────────────
   El objetivo de cada fundamento es EL MEJOR DE LA LIGA en ese fundamento,
   medido sobre los 97 partidos de la temporada 25-26.

   No es siempre el mismo equipo, y por eso no alcanzaba con copiar al campeon:

     Saque, recepcion, bloqueo #, y casi todo el ataque   Amriswil
     Bloqueo #+                                           Jona   (45,4 · Amriswil 43,0)
     Ataque tras recepcion negativa                       Schonenwerd (23,0)
     Defensa                                              NAFELS (58,0)

   En defensa el mejor era el propio equipo, asi que el objetivo se subio a 60:
   poner 58 seria pedirles lo que ya hacen y no dejaria nada por delante.

   Los otros dos cortes se reparten entre ese techo y el promedio de la liga,
   asi que el verde claro es "arriba del promedio" y el amarillo "abajo pero
   dentro de lo normal".

   Como referencia, con estos cortes el NAFELS de la 25-26 quedaba en amarillo
   en la mayoria de los fundamentos. Es correcto: no salieron campeones. El
   unico rojo claro era el ataque central, 36,4 contra 54,8 de Amriswil.

   Revisar al final de cada temporada con los partidos nuevos.               */
OBJETIVOS_CONFIG={metas:{
  sq:   { label:'% Saque (51)', obj:51, min:30,max:62, g2:51, g1:49, y:44},
  rec:  { label:'% Recepción (59)', obj:59, min:42,max:70, g2:59, g1:56, y:51},
  bqpos:{ label:'% Blq #+ (51)', obj:51, min:32,max:62, g2:51, g1:49, y:44},
  bqpt: { label:'% Blq # (22)', obj:22, min:5,max:32, g2:22, g1:19, y:13},
  atqq: { label:'% Atq Central (39)', obj:39, min:12,max:52, g2:39, g1:34, y:25},
  atqhb:{ label:'% Atq Alta (28)', obj:28, min:-5,max:40, g2:28, g1:21, y:10},
  atqx: { label:'% Atq Rápida (34)', obj:34, min:5,max:46, g2:34, g1:29, y:19},
  atqrp:{ label:'% Atq R#+ (51)', obj:51, min:12,max:64, g2:51, g1:42, y:27},
  atqri:{ label:'% Atq R! (33)', obj:33, min:0,max:46, g2:33, g1:27, y:15},
  atqrm:{ label:'% Atq R- (23)', obj:23, min:-10,max:36, g2:23, g1:16, y:5},
  atqtr:{ label:'% Atq Transición (29)', obj:29, min:5,max:40, g2:29, g1:24, y:14},
  def:  { label:'% Defensa (55)', obj:55, min:35,max:65, g2:55, g1:51, y:44}
}};

window.currentObjPartido = window.currentObjPartido || 'acumulado';
window.currentObjTipo = window.currentObjTipo || 'partido'; // 'partido' or 'entrenamiento'



function objGuardar(id, valor){
  var v = parseFloat(valor);
  if(isNaN(v)) return false;
  window.OBJ_CLUB[id] = v;
  objAplicarClub({});                     /* para no re-aplicar dos veces */
  var uno = {}; uno[id] = v;
  objAplicarClub(uno);
  try{
    localStorage.setItem('obj_club', JSON.stringify(window.OBJ_CLUB));
    if(typeof fbSet === 'function') fbSet('objetivos/' + id, v);
  }catch(e){}
  try{ window.dispatchEvent(new Event('vb-objetivos')); }catch(e){}
  return true;
}

function objAplicarClub(guardados){
  if(!guardados) return;
  Object.keys(guardados).forEach(function(id){
    var m = window.OBJETIVOS_CONFIG.metas[id];
    var v = parseFloat(guardados[id]);
    if(!m || isNaN(v)) return;
    var ancho = (m.g2 - m.y) || 10;      /* cuanto separaba el objetivo del piso */
    var paso  = (m.g2 - m.g1) || (ancho / 3);
    m.obj = v;
    m.g2  = v;
    m.g1  = v - paso;
    m.y   = v - ancho;
    /* la etiqueta muestra el objetivo real, no el de fabrica */
    m.label = String(m.label).replace(/\(-?[\d.]+%?\)/, '(' + v + '%)');
  });
  window.OBJ_CLUB = guardados;
}

function objClassify(id,val){
  /* ══ EL SEMAFORO, MEDIDO CONTRA LA LIGA DE VERDAD ═════════════════════════
     PROBLEMA 1 — los cortes no guardaban relacion entre si
     Cada fundamento tenia los suyos escritos a mano. El corte de "Neutro" iba
     del 56% al 95% del objetivo segun cual fuera, asi que 36 de 40 daba CERCA
     y 55 de 60 daba LEJOS. Sin forma de explicarlo.

     PROBLEMA 2 — eran numeros fijos
     Si cambiabas el objetivo en el panel, el semaforo seguia con los cortes
     viejos y quedaba mintiendo.

     PROBLEMA 3 — un porcentaje del objetivo tampoco alcanza
     Poner "verde si llegas al 92% del objetivo" suena razonable pero no
     significa nada: el objetivo es EL MEJOR DE LA LIGA, y estar al 92% del
     mejor puede ser excelente o mediocre segun cuanto se estiren los demas.

     LA SOLUCION — el recorrido real de la liga
     Cada fundamento ya guarda el rango de la liga: min es el peor equipo y
     obj es el mejor, medidos sobre los 97 partidos de la temporada. Entonces
     el color dice DONDE ESTAS DENTRO DE LA LIGA, que es un dato verificable
     y no una opinion:

         verde fuerte   llegaste al mejor de la liga
         verde claro    estas en el cuarto de arriba      (>= 75% del recorrido)
         amarillo       estas en la mitad de arriba       (>= 50%)
         rojo           estas en la mitad de abajo        (<  50%)

     El 50% es literalmente el medio entre el peor y el mejor. No es un numero
     elegido a dedo: es la mitad de la liga.

     Asi el tablero motiva sin mentir. "Estas en el cuarto de arriba de la
     liga" es una frase que se puede sostener con los numeros en la mano, y
     "estas en la mitad de abajo" tambien.

     Si algun fundamento necesita cortes propios, se respetan: alcanza con
     marcarlo con cortesPropios en la configuracion. */
  /* La proteccion evita que reviente si esta funcion corre antes de que
     termine de cargar la configuracion. */
  var m = (window.OBJETIVOS_CONFIG && window.OBJETIVOS_CONFIG.metas[id]) || {};
  var obj = (m.obj != null) ? m.obj : null;
  var piso = (m.min != null) ? m.min : 0;

  if (m.cortesPropios && m.g2 != null) {
    if(val>=m.g2) return{color:'#22c55e',bg:'rgba(34,197,94,.1)',   border:'rgba(34,197,94,.35)',  label:'Objetivo'};
    if(val>=m.g1) return{color:'#86efac',bg:'rgba(134,239,172,.08)',border:'rgba(134,239,172,.3)', label:'Cerca'};
    if(val>=m.y)  return{color:'#fbbf24',bg:'rgba(251,191,36,.1)',  border:'rgba(251,191,36,.3)',  label:'Neutro'};
    return              {color:'#ef4444',bg:'rgba(239,68,68,.1)',   border:'rgba(239,68,68,.3)',   label:'Lejos'};
  }

  /* donde cae dentro del recorrido de la liga: 0 = el peor, 100 = el mejor */
  var reco = (obj != null && obj > piso) ? ((val - piso) / (obj - piso) * 100) : null;
  if (reco === null) reco = (val >= (m.g2||0)) ? 100 : 0;

  if(reco>=100) return{color:'#22c55e',bg:'rgba(34,197,94,.1)',   border:'rgba(34,197,94,.35)',  label:'Objetivo'};
  if(reco>=75)  return{color:'#86efac',bg:'rgba(134,239,172,.08)',border:'rgba(134,239,172,.3)', label:'Cerca'};
  if(reco>=50)  return{color:'#fbbf24',bg:'rgba(251,191,36,.1)',  border:'rgba(251,191,36,.3)',  label:'Neutro'};
  return              {color:'#ef4444',bg:'rgba(239,68,68,.1)',   border:'rgba(239,68,68,.3)',   label:'Lejos'};
}

function objClassifyVsTeam(val,teamVal){
  if(teamVal===null||teamVal===undefined) return{color:'#64748b',bg:'rgba(100,116,139,.08)',border:'rgba(100,116,139,.2)',label:'—'};
  var d=val-teamVal;
  if(d>=5)  return{color:'#22c55e',bg:'rgba(34,197,94,.1)',   border:'rgba(34,197,94,.35)',  label:'Sobre equipo'};
  if(d>=0)  return{color:'#86efac',bg:'rgba(134,239,172,.08)',border:'rgba(134,239,172,.3)', label:'Cerca equipo'};
  if(d>=-8) return{color:'#fbbf24',bg:'rgba(251,191,36,.1)',  border:'rgba(251,191,36,.3)',  label:'Neutro'};
  return         {color:'#ef4444',bg:'rgba(239,68,68,.1)',   border:'rgba(239,68,68,.3)',   label:'Bajo equipo'};
}
function objCalcVals(nombreJugador){
  // Use per-partido data if selected
  if(false){ // handled above with INDIVIDUAL_SRC
    var pd = null;
    if(pd){
      if(nombreJugador){
        // Find jugador in this partido by name
        var nmC2 = nombreJugador.replace(/^\d+\s*/,'').toLowerCase();
        var pj2 = pd.jugadores ? pd.jugadores.find(function(x){
          if(!x.nombre) return false;
          var xC2 = x.nombre.replace(/^\d+\s*/,'').toLowerCase();
          return xC2 === nmC2 || xC2.split(' ')[0] === nmC2.split(' ')[0];
        }) : null;
        if(pj2 && pj2.objetivos && Object.keys(pj2.objetivos).length > 0) return pj2.objetivos;
      } else {
        // Equipo for this partido
        if(pd.equipo_obj && Object.keys(pd.equipo_obj).length > 0) return pd.equipo_obj;
        if(pd.objetivos && pd.objetivos['__equipo__']) return pd.objetivos['__equipo__'];
      }
    }
  }
  // Acumulado - use entrenamientos or partidos based on tipo
  var JUGADORES_SRC = window.currentObjTipo==='entrenamiento'
    ? (typeof ENTRENAMIENTOS_JUGADORES!=='undefined' ? ENTRENAMIENTOS_JUGADORES : null)
    : (typeof PARTIDOS_JUGADORES!=='undefined' ? PARTIDOS_JUGADORES : null);
  var INDIVIDUAL_SRC = window.currentObjTipo==='entrenamiento'
    ? (typeof ENTRENAMIENTOS_INDIVIDUAL!=='undefined' ? ENTRENAMIENTOS_INDIVIDUAL : null)
    : (typeof PARTIDOS_INDIVIDUAL!=='undefined' ? PARTIDOS_INDIVIDUAL : null);
  var EQUIPO_SRC = window.currentObjTipo==='entrenamiento'
    ? (typeof ENTRENAMIENTOS_EQUIPO_OBJ!=='undefined' ? ENTRENAMIENTOS_EQUIPO_OBJ : null)
    : (typeof PARTIDOS_EQUIPO_OBJ!=='undefined' ? PARTIDOS_EQUIPO_OBJ : null);

  // Per-sesion if selected
  if(INDIVIDUAL_SRC && window.currentObjPartido !== 'acumulado'){
    var pd2 = INDIVIDUAL_SRC.find(function(p){ return p.nombre === currentObjPartido; });
    if(pd2){
      if(nombreJugador){
        var nmC3 = nombreJugador.replace(/^\d+\s*/,'').toLowerCase();
        var pj3 = pd2.jugadores ? pd2.jugadores.find(function(x){
          if(!x.nombre) return false;
          var xC3 = x.nombre.replace(/^\d+\s*/,'').toLowerCase();
          return xC3 === nmC3 || xC3.split(' ')[0] === nmC3.split(' ')[0];
        }) : null;
        if(pj3 && pj3.objetivos && Object.keys(pj3.objetivos).length>0) return pj3.objetivos;
      } else {
        if(pd2.equipo_obj && Object.keys(pd2.equipo_obj).length>0) return pd2.equipo_obj;
      }
    }
  }

  // Acumulado from datos_partidos.js or datos_entrenamientos.js
  if(JUGADORES_SRC && nombreJugador){
    var nmClean = nombreJugador.replace(/^\d+\s*/,'').toLowerCase();
    var pj = JUGADORES_SRC.find(function(x){
      if(!x.nombre) return false;
      var xClean = x.nombre.replace(/^\d+\s*/,'').toLowerCase();
      var nmApellido = nmClean.split(' ')[0];
      var xApellido  = xClean.split(' ')[0];
      return xClean === nmClean || nmApellido === xApellido;
    });
    if(pj && pj.objetivos && Object.keys(pj.objetivos).length > 0){
      return pj.objetivos;
    }
    // Found source but no data for this jugador — return nulls instead of falling to DVW
    if(window.currentObjTipo === 'entrenamiento'){
      return {sq:null,rec:null,bqpos:null,bqpt:null,atqq:null,atqhb:null,
              atqx:null,atqrp:null,atqri:null,atqrm:null,atqtr:null};
    }
  }
  // Equipo acumulado
  if(EQUIPO_SRC && !nombreJugador && Object.keys(EQUIPO_SRC).length > 0){
    return EQUIPO_SRC;
  }
  // If entrenamiento mode and no data found, return nulls (don't show fake data)
  if(window.currentObjTipo === 'entrenamiento'){
    return {sq:null,rec:null,bqpos:null,bqpt:null,atqq:null,atqhb:null,
            atqx:null,atqrp:null,atqri:null,atqrm:null,atqtr:null};
  }
  // Fallback: calculate from HISTORIAL_DATA (DVW)
  var D=window.HISTORIAL_DATA;
  if(!D){
    if(nombreJugador) return {sq:-5,rec:29,bqpos:38,bqpt:18,atqq:41,atqhb:14,atqx:34,atqrp:42,atqri:27,atqrm:19,atqtr:28};
    return {sq:-5,rec:29,bqpos:38,bqpt:18,atqq:null,atqhb:14,atqx:null,atqrp:null,atqri:null,atqrm:null,atqtr:null};
  }
  var a={sT:0,sPunto:0,sPos:0,sVend:0,sErr:0,rT:0,rPunto:0,rPos:0,rVend:0,rErr:0,
         aT:0,aPunto:0,aVend:0,aErr:0,bT:0,bPt:0,bPtPos:0,mbT:0,mbPt:0,mbVnd:0,mbErr:0};
  var CENT=[2,10,15,17];
  D.entrenamientos.forEach(function(s){
    s.jugadores.forEach(function(j){
      if(j.n==='TOTALES EQUIPO') return;
      if(nombreJugador&&j.n!==nombreJugador) return;
      a.sT+=j.sT||0;a.sPunto+=j.sPunto||0;a.sPos+=j.sPos||0;a.sVend+=j.sVend||0;a.sErr+=j.sErr||0;
      a.rT+=j.rT||0;a.rPunto+=j.rPunto||0;a.rPos+=j.rPos||0;a.rVend+=j.rVend||0;a.rErr+=j.rErr||0;
      a.aT+=j.aT||0;a.aPunto+=j.aPunto||0;a.aVend+=j.aVend||0;a.aErr+=j.aErr||0;
      a.bT+=j.bT||0;a.bPt+=j.bPt||0;a.bPtPos+=j.bPtPos||0;
      if(!nombreJugador&&CENT.indexOf(j.c)>=0){a.mbT+=j.aT||0;a.mbPt+=j.aPunto||0;a.mbVnd+=j.aVend||0;a.mbErr+=j.aErr||0;}
    });
  });
  var v={};
  v.sq   =a.sT>0?VB_EFF.saque(a):null;
  v.rec  =a.rT>0?VB_EFF.recepcion(a):null;
  v.bqpos=a.bT>0?Math.round((a.bPt+a.bPtPos)/a.bT*100):null;
  v.bqpt =a.bT>0?Math.round(a.bPt/a.bT*100):null;
  v.atqhb=a.mbT>0?Math.round((a.mbPt-a.mbVnd-a.mbErr)/a.mbT*100):null;
  return v;
}

/* ══ Partidos y entrenamientos no se cruzan ═══════════════════════════════
   Cada pantalla guarda el filtro con un nombre y una codificacion distinta:
   el dashboard usa EQ_FILTRO con 'P' y 'E', el analisis FILTRO_TIPO igual, y
   el perfil del jugador _objTipo con 'partido' y 'entrenamiento'. Esta funcion
   las lee todas y devuelve siempre lo mismo, para que la separacion no dependa
   de que pantalla la pregunta.

   Devuelve null cuando el filtro esta en "Todos": ahi el acumulado es la suma
   de las dos cosas, que es como se venia usando. */
function batTipoActual(){
  function _norm(v){
    if(v===null || v===undefined) return null;
    v = String(v).toLowerCase();
    if(v==='p' || v==='partido'  || v==='partidos')       return 'partido';
    if(v==='e' || v==='entrenamiento' || v==='entrenamientos') return 'entrenamiento';
    return null;   /* 'todos' o cualquier otra cosa */
  }
  /* El ORDEN importa. EQ_FILTRO y FILTRO_TIPO tienen un valor explicito para
     "todos"; _objTipo no —en el analisis queda en 'partido' aunque el filtro
     este en Todos—, asi que se mira ultimo y solo donde los otros no existen.
     Manda la primera variable que exista en la pagina, incluso si dice todos. */
  try{
    if(window.EQ_FILTRO   !== undefined) return _norm(window.EQ_FILTRO);
    if(window.FILTRO_TIPO !== undefined) return _norm(window.FILTRO_TIPO);
    if(window._objTipo    !== undefined) return _norm(window._objTipo);
    /* Ultimo recurso: el filtro compartido de filtro_tipo.js, para las
       pantallas que no tienen variable propia (ranking, por ejemplo). */
    if(typeof window.vbTipoLargo === 'function') return window.vbTipoLargo();
  }catch(e){}
  return null;
}

function renderObjetivos(cid,extra){
  var el=document.getElementById(cid); if(!el) return;
  var metas=window.OBJETIVOS_CONFIG.metas;
  /* Los numeros del equipo. Se usa objGetVals —que lee del archivo de
     baterias, con el detalle partido por partido— y solo se cae a objCalcVals
     si esa no esta. Antes se usaba siempre la vieja, y el dashboard mostraba
     valores distintos a los del analisis para la misma sesion. */
  var base = (typeof objGetVals === 'function') ? objGetVals(null) : objCalcVals(null);
  var vals = Object.assign({}, base, extra||{});
  var html='<div style="font-family:Barlow Condensed,sans-serif;padding:4px 0 8px">'
    +'<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:10px">'
    +'<div style="font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#64748b">OBJETIVOS DEL EQUIPO'+(window.__TEMP_TITULO||'')+'</div>'
    +'<div style="display:flex;gap:10px;flex-wrap:wrap">'
    +[['#22c55e','Objetivo'],['#86efac','Cerca'],['#fbbf24','Neutro'],['#ef4444','Lejos']].map(function(x){
      return'<div style="display:flex;align-items:center;gap:4px;font-size:9px;color:#64748b"><div style="width:7px;height:7px;border-radius:50%;background:'+x[0]+'"></div>'+x[1]+'</div>';
    }).join('')+'</div></div>'
    /* ══ TODO EN UNA FILA, PARA QUE ENTRE EN EL TELEVISOR ══════════════════
       Antes habia DOS filas: una con el nombre y el objetivo, y abajo otra
       con la bateria. Sumaban mas de 200px de alto y en la tele habia que
       subir y bajar la pagina para ver los doce.

       Ademas el objetivo salia repetido: la etiqueta ya dice "% Saque (42)"
       y justo abajo aparecia otra vez "42%".

       Ahora es UNA sola tarjeta por fundamento, con el nombre arriba, el
       numero grande y la bateria. Entra todo en una pantalla.            */
    +'<div style="display:flex;gap:6px;width:100%;flex-wrap:nowrap">'
    +Object.keys(metas).map(function(id){
      var m=metas[id],val=vals[id]!==undefined?vals[id]:null;
      var cls=val!==null?objClassify(id,val):{color:'#334155',bg:'rgba(51,65,85,.08)',border:'rgba(51,65,85,.2)',label:'—'};
      /* El total de acciones viaja con la meta: es lo que permite leer bien el
         numero. Un 40% de 5 acciones y un 20% de 238 no valen lo mismo. */
      try{ if(vals['n_'+id]!=null) m=Object.assign({},m,{n:vals['n_'+id]}); }catch(e){}
            /* De que fila es esta bateria: el jugador o el equipo, y que sesion
         se esta viendo. Viaja con la meta para que la ventanita lo muestre. */
      try{ var _q = (row && row.label) ? String(row.label) : '';
           var _s = (typeof objNombreSesion === 'function') ? objNombreSesion() : '';
           _m = Object.assign({}, m, {__fila: _q + (_s ? ' \u00b7 ' + _s : ''),
          /* el nombre del jugador de esta fila, para el video */
          __jug: (row && (row.jug || row.nombre || row.name)) || (/equipo/i.test(_q) ? '' : (window._dbatNombre || window._objNombre || ''))});
      }catch(e){ _m = m; }
            return objSingleBat(id,val,_m,cls,m.obj);
    }).join('')+'</div></div>';
  el.innerHTML=html;
}
function objPct(v,mn,mx){return Math.max(0,Math.min(100,(v-mn)/(mx-mn)*100));}
function fmtEff(v){
  /* ══ SIEMPRE REDONDO ══════════════════════════════════════════════════════
     Antes esto NO redondeaba: si le llegaba 55.34 escribia "55.34%". Por eso
     aparecian porcentajes con decimales en distintas pantallas, segun de
     donde viniera el numero.

     Como fmtEff la usan todas las pantallas, arreglarlo aca los deja redondos
     en todo el sistema de una sola vez. */
  if(v === null || v === undefined || isNaN(v)) return '\u2014';
  var n = Math.round(Number(v));
  return (n < 0 ? '-' : '') + Math.abs(n) + '%';
}

/* ══════════════════════════════════════════════════════════════════════════
   LA VENTANITA DEL DETALLE
   --------------------------------------------------------------------------
   La primera version mostraba la cuenta: acciones x peso = puntos, y abajo
   "8712 puntos repartidos entre 158 acciones = 55".

   Eso es la aritmetica, no el entendimiento. Ningun jugador piensa en "8712
   puntos", y saber la formula no le dice que hacer el martes que viene.

   Un jugador necesita tres cosas, en este orden:

     1. COMO RECIBE, en algo que pueda imaginar: "de cada 10 pelotas".
        158 acciones no se visualizan; 10 si.
     2. QUE LE ESTA COSTANDO el numero. No cuanto suma lo bueno, sino cuanto
        le RESTA lo malo, que es donde se puede mejorar.
     3. QUE LE FALTA para el objetivo, en acciones concretas. "Te faltan 5"
        no sirve; "convertir 15 errores en suficientes" si.

   La cuenta completa queda abajo, plegada, para el cuerpo tecnico.
   ══════════════════════════════════════════════════════════════════════════ */


/* ══ LA VENTANITA EN LOS TRES IDIOMAS ════════════════════════════════════════
   Todo lo que escribe esta ventana estaba fijo en castellano: "158 pelotas
   que recibe", "LO QUE MÁS TE CUESTA", "convertir 16 errores en suficientes".
   Con el club en ingles quedaba mezclado y se leia mal.

   Se usa el traductor del sistema —lang.js— si esta cargado; si no, una tabla
   propia con lo mismo, para que funcione igual en las pantallas que no lo
   tienen. */
var OBJ_T = {
  en: {
    '% Blq #+':'% Block #+',
    '% Blq #':'% Block #',
    '% Atq R#+':'% Atk after R#+',
    '% Atq R!':'% Atk after R!',
    '% Atq R-':'% Atk after R-',
    '% Atq Transición':'% Atk in transition',
    'Objetivo':'Target',
    'Cerca':'Close',
    'Lejos':'Far',
    'Ver estas':'Watch these',
    'Ver estos':'Watch these',
    'acciones en video':'actions on video',
    'ataques en video':'attacks on video',
    'el peor de la liga':'worst in the league',
    'el mejor':'best',
    '% Recepción':'% Reception',
    '% Saque':'% Serve',
    '% Defensa':'% Defense',
    '% Bloqueo #+':'% Block #+',
    '% Bloqueo #':'% Block #',
    '% Ataque':'% Attack',
    '% Atq Central':'% Middle Atk',
    '% Atq Alta':'% High-ball Atk',
    '% Atq Rápida':'% Quick Atk',
    'estás al':'you are at',
    'del recorrido':'of the way there',
    'acc.':'act.',
    'obj':'tgt',
    'no fallar':'do not miss',
    'ataques más en punto':'more attacks into points',
    'pelotas entre errores y bloqueados':'balls between errors and blocks',
    'Todavía no hay ataques de este tipo.':'No attacks of this type yet.',
    'puntos.':'points.',
    'pelotas que recibe':'balls received', 'saques que pega':'serves hit',
    'ataques de central':'middle attacks', 'ataques de pelota alta':'high-ball attacks',
    'ataques rápidos':'quick attacks', 'ataques':'attacks', 'bloqueos':'blocks',
    'pelotas que defiende':'balls dug', 'acciones':'actions',
    'objetivo':'target', 'de cada 10':'out of 10', 'Tus':'Your',
    'Cómo se llega a':'How you get to', 'Lo que más te cuesta':'What costs you most',
    'Para llegar a':'To reach', 'convertir':'turn', 'en':'into',
    'no regalar':'stop giving away', 'pasás de':'you go from', 'a':'to',
    'y llegás al objetivo.':'and you hit the target.',
    'Después hay que subir calidad.':'After that you need better quality.',
    'Ningún cambio por separado alcanza. La palanca más grande:':'No single change is enough. The biggest lever:',
    'Estás por encima del objetivo.':'You are above target.',
    'El equipo apunta a':'The team aims for', 'y vos vas':'and you are',
    'arriba.':'above.',
    'Hace falta subir la calidad general.':'Overall quality needs to improve.',
    'Ojo: son pocas pelotas.':'Careful: few balls.',
    'Ojo: son pocas acciones.':'Careful: few actions.',
    'Con':'With', 'ataque':'attack', 'una sola cambia el número':'a single one moves the number',
    'puntos. Este porcentaje todavía no dice mucho: mirálo cuando haya más.':'points. This percentage does not say much yet: check it when there are more.',
    ', una sola cambia bastante el número. Mirálo cuando haya más.':', a single one moves the number a lot. Check it when there are more.',
    'Cada pelota vale según cómo quedó:':'Each ball counts by how it ended:',
    'vale':'counts', 'El resultado es el promedio.':'The result is the average.',
    'No es un promedio como en recepción: es una RESTA. Cuenta cuántos puntos netos deja cada ataque, por eso puede dar negativo.':'This is not an average like reception: it is a SUBTRACTION. It counts net points per attack, which is why it can go negative.',
    'puntos':'points', 'bloqueados':'blocked', 'errores':'errors',
    'Lo que regalás':'What you give away', 'de tus':'of your',
    'ataques terminan en punto del rival':'attacks end in a point for the opponent',
    'te bajan':'they cost you',
    'bloqueos terminaron en punto':'blocks ended in a point',
    'en punto y':'in a point and', 'en positivo':'positive', 'sobre':'out of',
    'Punto':'Point', 'Sigue en juego':'Still in play', 'Bloqueado':'Blocked', 'Error':'Error',
    'Perfecta':'Perfect', 'Positiva':'Positive', 'Suficiente':'Fair', 'Pobre':'Poor',
    'Sobrepase':'Overpass', 'Ace':'Ace', 'Free ball':'Free ball', 'Positivo':'Positive',
    'Neutro':'Neutral', 'Negativo':'Negative', 'Buena':'Good', 'Neutra':'Neutral', 'Mala':'Poor',
    'Saque':'Serve', 'Recepción':'Reception', 'Defensa':'Defense',
    'Bloqueo #+':'Block #+', 'Bloqueo #':'Block #',
    'Atq Central':'Middle Atk', 'Atq Alta':'High-ball Atk', 'Atq Rápida':'Quick Atk',
    'Atq tras recepción #+':'Atk after reception #+', 'Atq tras recepción !':'Atk after reception !',
    'Atq tras recepción -':'Atk after reception -', 'Atq en transición':'Atk in transition',
    'Todavía no hay acciones de este fundamento.':'No actions for this skill yet.',
    'Para este fundamento todavía no hay desglose guardado.':'No breakdown stored for this skill yet.',
    'Corré HACER_TODO y volvé a entrar.':'Run HACER_TODO and come back in.',
    'Cerrar':'Close',
    'El resultado es el PROMEDIO. Por eso 50 no es "la mitad de bien": 50 es lo que vale una pelota neutra.':'The result is the AVERAGE. That is why 50 is not "half good": 50 is what a neutral ball is worth.',
    'No pude identificar al jugador para traer sus acciones.':'I could not identify the player to fetch their actions.',
    'El reproductor no está cargado en esta pantalla.':'The player is not loaded on this screen.'
  },
  de: {
    '% Blq #+':'% Block #+',
    '% Blq #':'% Block #',
    '% Atq R#+':'% Angriff nach R#+',
    '% Atq R!':'% Angriff nach R!',
    '% Atq R-':'% Angriff nach R-',
    '% Atq Transición':'% Angriff im Umschalten',
    'Objetivo':'Ziel',
    'Cerca':'Nah',
    'Lejos':'Weit',
    'Ver estas':'Diese ansehen',
    'Ver estos':'Diese ansehen',
    'acciones en video':'Aktionen im Video',
    'ataques en video':'Angriffe im Video',
    'el peor de la liga':'Schlechtester der Liga',
    'el mejor':'Bester',
    '% Recepción':'% Annahme',
    '% Saque':'% Aufschlag',
    '% Defensa':'% Abwehr',
    '% Bloqueo #+':'% Block #+',
    '% Bloqueo #':'% Block #',
    '% Ataque':'% Angriff',
    '% Atq Central':'% Angriff Mitte',
    '% Atq Alta':'% Hoher Angriff',
    '% Atq Rápida':'% Schneller Angriff',
    'estás al':'du bist bei',
    'del recorrido':'des Weges',
    'acc.':'Akt.',
    'obj':'Ziel',
    'no fallar':'nicht vergeben',
    'ataques más en punto':'weitere Angriffe zu Punkten',
    'pelotas entre errores y bloqueados':'Bälle zwischen Fehlern und Blocks',
    'Todavía no hay ataques de este tipo.':'Noch keine Angriffe dieser Art.',
    'puntos.':'Punkte.',
    'pelotas que recibe':'angenommene Bälle', 'saques que pega':'Aufschläge',
    'ataques de central':'Angriffe Mitte', 'ataques de pelota alta':'hohe Angriffe',
    'ataques rápidos':'schnelle Angriffe', 'ataques':'Angriffe', 'bloqueos':'Blocks',
    'pelotas que defiende':'abgewehrte Bälle', 'acciones':'Aktionen',
    'objetivo':'Ziel', 'de cada 10':'von 10', 'Tus':'Deine',
    'Cómo se llega a':'So kommt man auf', 'Lo que más te cuesta':'Was dich am meisten kostet',
    'Para llegar a':'Um zu erreichen', 'convertir':'wandle', 'en':'in',
    'no regalar':'nicht verschenken', 'pasás de':'du gehst von', 'a':'auf',
    'y llegás al objetivo.':'und erreichst das Ziel.',
    'Después hay que subir calidad.':'Danach braucht es mehr Qualität.',
    'Ningún cambio por separado alcanza. La palanca más grande:':'Keine einzelne Änderung reicht. Der grösste Hebel:',
    'Estás por encima del objetivo.':'Du liegst über dem Ziel.',
    'El equipo apunta a':'Das Team zielt auf', 'y vos vas':'und du bist',
    'arriba.':'darüber.',
    'Hace falta subir la calidad general.':'Die Qualität muss insgesamt steigen.',
    'Ojo: son pocas pelotas.':'Achtung: wenige Bälle.',
    'Ojo: son pocas acciones.':'Achtung: wenige Aktionen.',
    'Con':'Mit', 'ataque':'Angriff', 'una sola cambia el número':'ein einziger verschiebt die Zahl',
    'puntos. Este porcentaje todavía no dice mucho: mirálo cuando haya más.':'Punkte. Dieser Prozentwert sagt noch wenig: schau später nochmal.',
    ', una sola cambia bastante el número. Mirálo cuando haya más.':', eine einzige verschiebt die Zahl deutlich. Schau später nochmal.',
    'Cada pelota vale según cómo quedó:':'Jeder Ball zählt je nach Ausgang:',
    'vale':'zählt', 'El resultado es el promedio.':'Das Ergebnis ist der Durchschnitt.',
    'No es un promedio como en recepción: es una RESTA. Cuenta cuántos puntos netos deja cada ataque, por eso puede dar negativo.':'Das ist kein Durchschnitt wie bei der Annahme, sondern eine SUBTRAKTION: Nettopunkte pro Angriff, darum kann es negativ werden.',
    'puntos':'Punkte', 'bloqueados':'geblockt', 'errores':'Fehler',
    'Lo que regalás':'Was du verschenkst', 'de tus':'deiner',
    'ataques terminan en punto del rival':'Angriffe enden mit einem Punkt für den Gegner',
    'te bajan':'das kostet dich',
    'bloqueos terminaron en punto':'Blocks endeten mit einem Punkt',
    'en punto y':'als Punkt und', 'en positivo':'positiv', 'sobre':'von',
    'Punto':'Punkt', 'Sigue en juego':'Noch im Spiel', 'Bloqueado':'Geblockt', 'Error':'Fehler',
    'Perfecta':'Perfekt', 'Positiva':'Positiv', 'Suficiente':'Ausreichend', 'Pobre':'Schwach',
    'Sobrepase':'Überpass', 'Ace':'Ass', 'Free ball':'Freeball', 'Positivo':'Positiv',
    'Neutro':'Neutral', 'Negativo':'Negativ', 'Buena':'Gut', 'Neutra':'Neutral', 'Mala':'Schwach',
    'Saque':'Aufschlag', 'Recepción':'Annahme', 'Defensa':'Abwehr',
    'Bloqueo #+':'Block #+', 'Bloqueo #':'Block #',
    'Atq Central':'Angriff Mitte', 'Atq Alta':'Hoher Angriff', 'Atq Rápida':'Schneller Angriff',
    'Atq tras recepción #+':'Angriff nach Annahme #+', 'Atq tras recepción !':'Angriff nach Annahme !',
    'Atq tras recepción -':'Angriff nach Annahme -', 'Atq en transición':'Angriff im Umschalten',
    'Todavía no hay acciones de este fundamento.':'Noch keine Aktionen für dieses Element.',
    'Para este fundamento todavía no hay desglose guardado.':'Für dieses Element ist noch keine Aufschlüsselung gespeichert.',
    'Corré HACER_TODO y volvé a entrar.':'Führe HACER_TODO aus und komm zurück.',
    'Cerrar':'Schliessen',
    'El resultado es el PROMEDIO. Por eso 50 no es "la mitad de bien": 50 es lo que vale una pelota neutra.':'Das Ergebnis ist der DURCHSCHNITT. Darum heisst 50 nicht "halb gut": 50 ist der Wert eines neutralen Balls.',
    'No pude identificar al jugador para traer sus acciones.':'Ich konnte den Spieler nicht identifizieren.',
    'El reproductor no está cargado en esta pantalla.':'Der Player ist auf diesem Bildschirm nicht geladen.'
  }
};

function objIdioma(){
  try{ return localStorage.getItem('vb_lang') || 'es'; }catch(e){ return 'es'; }
}

/* Traduce un texto de la ventanita. Primero prueba lang.js —asi comparte las
   traducciones con el resto de la app— y si no lo tiene usa la tabla de aca. */
function ot(txt){
  var L = objIdioma();
  if(L === 'es') return txt;
  try{ if(typeof t === 'function'){ var r = t(txt); if(r && r !== txt) return r; } }catch(e){}
  var d = OBJ_T[L];
  return (d && d[txt]) ? d[txt] : txt;
}

var OBJ_DETALLE = {
  sq:   {d:'sqD',  nom:'Saque',      pl:'saques que pega',
         filas:[['p','Ace',100,'#22c55e','#'],['f','Free ball',87.5,'#4ade80','/'],
                ['o','Positivo',75,'#86efac','+'],['n','Neutro',50,'#fbbf24','!'],
                ['m','Negativo',25,'#fb923c','-'],['e','Error',0,'#ef4444','=']]},
  rec:  {d:'recD', nom:'Recepción',  pl:'pelotas que recibe',
         filas:[['p','Perfecta',100,'#22c55e','#'],['o','Positiva',75,'#86efac','+'],
                ['n','Suficiente',50,'#fbbf24','!'],['m','Pobre',25,'#fb923c','-'],
                ['s','Sobrepase',12.5,'#f87171','/'],['e','Error',0,'#ef4444','=']]},
  def:  {d:'defD', nom:'Defensa',    pl:'pelotas que defiende',
         filas:[['p','Perfecta',100,'#22c55e','#'],['o','Buena',75,'#86efac','+'],
                ['n','Neutra',50,'#fbbf24','!'],['m','Mala',25,'#fb923c','-'],
                ['e','Error',0,'#ef4444','=']]},
  bqpos:{d:'bqD',  nom:'Bloqueo #+', tipo:'bq',  pl:'bloqueos',
         filas:[['p','Punto',null,'#22c55e','#'],['o','Positivo',null,'#86efac','+']]},
  /* ══ LOS ATAQUES ══════════════════════════════════════════════════════
     El ataque NO se cuenta como el resto. No es un promedio ponderado sino
     una resta: (puntos - bloqueados - errores) / total. Por eso puede dar
     negativo y por eso lleva su propia explicacion.

     'tipo:atq' le avisa a la ventana que use esa forma. */
  atqq: {d:'atqD', k:'q',  nom:'Atq Central',    tipo:'atq', pl:'ataques de central'},
  atqhb:{d:'atqD', k:'hb', nom:'Atq Alta',       tipo:'atq', pl:'ataques de pelota alta'},
  atqx: {d:'atqD', k:'x',  nom:'Atq Rápida',     tipo:'atq', pl:'ataques rápidos'},
  atqrp:{d:'atqD', k:'rp', nom:'Atq tras recepción #+', tipo:'atq', pl:'ataques'},
  atqri:{d:'atqD', k:'ri', nom:'Atq tras recepción !',  tipo:'atq', pl:'ataques'},
  atqrm:{d:'atqD', k:'rm', nom:'Atq tras recepción -',  tipo:'atq', pl:'ataques'},
  atqtr:{d:'atqD', k:'tr', nom:'Atq en transición',     tipo:'atq', pl:'ataques'},
  bqpt: {d:'bqD',  nom:'Bloqueo #',  tipo:'bqpt',pl:'bloqueos',
         filas:[['p','Punto',null,'#22c55e','#']]}
};


/* El plural en castellano: "error" -> "errores", "positiva" -> "positivas". */

/* ══ QUE SESION SE ESTA VIENDO ══════════════════════════════════════════════
   La ventanita tiene que decir de donde salen los numeros: del acumulado, de
   un entrenamiento suelto o de un partido. Sin eso el jugador ve "53%" y no
   sabe si es de hoy o de toda la temporada.

   Cada pantalla guarda esa eleccion en un lugar distinto —el selector de
   sesion, el boton PARTIDO/ENTRENAMIENTO—, asi que se leen los que existen y
   se arma una etiqueta corta. */
function objNombreSesion(){
  try{
    var partes = [];

    /* partido o entrenamiento */
    var t = null;
    try{ t = window._objTipo || (typeof ppTipoActual==='function' ? ppTipoActual() : null); }catch(e){}
    if(t === 'P' || t === 'partido')       partes.push('Partidos');
    else if(t === 'E' || t === 'entrenamiento') partes.push('Entrenamientos');

    /* la sesion elegida en el desplegable */
    var sel = document.getElementById('objSesion') || document.getElementById('_dbatSel')
           || document.getElementById('batSel')    || document.getElementById('sesionSel');
    if(sel && sel.options && sel.selectedIndex >= 0){
      var txt = (sel.options[sel.selectedIndex].text || '').trim();
      /* el acumulado ya se entiende con "Partidos"/"Entrenamientos" */
      if(txt && !/^(acumulado|cumulative|gesamt)/i.test(txt)) partes.push(txt);
      else if(!partes.length) partes.push(txt);
    }
    return partes.join(' \u00b7 ');
  }catch(e){ return ''; }
}


/* ══ CUANDO NINGUN CAMBIO SOLO ALCANZA ══════════════════════════════════════
   Antes se decia "hace falta subir la calidad general", que es la forma
   elegante de no decir nada. Ahora se calcula la palanca mas grande que el
   jugador tiene a mano —cortar lo que regala— y se muestra cuanto gana. */

/* ══════════════════════════════════════════════════════════════════════════
   LA VENTANITA DEL ATAQUE
   --------------------------------------------------------------------------
   El ataque se cuenta distinto a todo lo demas:

       (puntos - bloqueados - errores) / total

   No es un promedio: es cuantos puntos NETOS deja cada ataque. Por eso puede
   dar negativo, y por eso no sirve mostrar "de cada 10" con pesos.

   Lo que un atacante necesita ver:
     · cuantos fueron punto y cuantos se perdieron
     · que el numero es una RESTA, no un porcentaje de acierto
     · cuantas pelotas tiene que dejar de regalar para llegar al objetivo
   ══════════════════════════════════════════════════════════════════════════ */
function objAtaqueDetalle(cfg, D, vals, id, meta, quien){
  /* El nombre del jugador de ESTA ventana. Sale de la meta que guardo la
     bateria; si no vino, se cae a las globales de cada pantalla. */
  var _jugNom = '';
  try{
    _jugNom = (meta && meta.__jug) || window._dbatNombre || window._objNombre || '';
  }catch(e){}

  var P = D.p||0, B = D.b||0, E = D.e||0, T = D.t||0;
  var sigue = Math.max(0, T - P - B - E);
  var neto  = P - B - E;
  var val   = T ? (neto/T*100) : null;
  var obj   = (meta && meta.obj!=null) ? meta.obj : null;
  var nombre = ot(cfg.nom);

  if(!T){
    objPintarDetalle(nombre, obj,
      '<div style="color:#64748b;font-size:12px;padding:8px 0">'+ot('Todavía no hay ataques de este tipo.')+'</div>',
      null, null, null, quien);
    return;
  }

  /* El quinto dato es la clave para el video: el signo que busca en el
     scout. "Sigue en juego" no tiene, porque no es una valoracion. */
  var FIL = [
    ['#', 'Punto',          P,     '#22c55e', 'p'],
    /* «Sigue en juego» no es una valoracion: es lo que queda despues del
       punto, la bloqueada y el error. En video son los + , ! y - . */
    ['\u25b8','Sigue en juego', sigue, '#64748b', '+,!,-'],
    ['/', 'Bloqueado',      B,     '#fb923c', 'b'],
    ['=', 'Error',          E,     '#ef4444', 'e']
  ];

  var barra = '', lista = '';
  FIL.forEach(function(f){
    if(!f[2]) return;
    barra += '<div title="'+ot(f[1])+': '+f[2]+'" style="width:'+(f[2]/T*100)+'%;background:'+f[3]+'"></div>';
    lista += '<div style="display:flex;align-items:center;gap:8px;padding:3.5px 0">'
      + '<span style="width:19px;height:19px;border-radius:4px;background:'+f[3]+';color:#0f172a;'
      +    'font-weight:900;font-size:13px;display:flex;align-items:center;justify-content:center;'
      +    'flex:none;font-family:monospace">'+f[0]+'</span>'
      + '<span style="flex:1;color:#cbd5e1">'+ot(f[1])+'</span>'
      /* El numero se toca. "Sigue en juego" no: no es una valoracion del
         scout sino lo que queda al restar, no hay un signo que buscar. */
      + (f[4]
         ? '<span onclick="objVerVideo(\''+id+'\',\''+f[4]+'\',\''+(quien||'').replace(/\'/g,'')+'\','+f[2]+',\''+String(_jugNom||'').replace(/\'/g,'')+'\')" '
           + 'title="'+ot('Ver estos')+' '+f[2]+' '+ot('ataques en video')+'" '
           + 'style="font-weight:900;color:#e2e8f0;min-width:30px;text-align:right;font-size:14px;'
           + 'cursor:pointer;text-decoration:underline;text-decoration-color:rgba(148,163,184,.4);'
           + 'text-underline-offset:3px">'+f[2]+'</span>'
         : '<span style="font-weight:900;color:#e2e8f0;min-width:30px;text-align:right;font-size:14px">'+f[2]+'</span>')
      + '<span style="color:#64748b;min-width:56px;text-align:right;font-size:11px">'
      +    (f[2]/T*10).toFixed(1)+' '+ot('de cada 10')+'</span>'
      + '</div>';
  });

  /* la cuenta: es una resta, y se dice */
  var cuenta = '<div style="margin-top:11px;padding:9px 11px;background:rgba(148,163,184,.07);'
    + 'border-radius:8px;font-size:11.5px;color:#94a3b8;line-height:1.7">'
    + '<div style="font-size:10px;font-weight:800;letter-spacing:.7px;color:#64748b;'
    +      'text-transform:uppercase;margin-bottom:3px">'+ot('Cómo se llega a')+' '+Math.round(val)+'%</div>'
    + '<b style="color:#86efac">'+P+'</b> '+ot('puntos')+' \u2212 <b style="color:#fb923c">'+B+'</b> '+ot('bloqueados')
    + ' \u2212 <b style="color:#f87171">'+E+'</b> '+ot('errores')+' = <b style="color:#cbd5e1">'+neto+'</b>'
    + '<br><b style="color:#cbd5e1">'+neto+'</b> \u00f7 <b style="color:#cbd5e1">'+T+'</b>'
    + ' = <b style="color:#e2e8f0;font-size:14px">'+Math.round(val)+'%</b>'
    + '<div style="margin-top:5px;color:#64748b">'
    + ot('No es un promedio como en recepción: es una RESTA. Cuenta cuántos puntos netos deja cada ataque, por eso puede dar negativo.')
    + '</div>'
    + '</div>';

  /* lo que cuesta */
  var cuesta = '';
  if(B || E){
    cuesta = '<div style="margin-top:13px">'
      + '<div style="font-size:10px;font-weight:800;letter-spacing:.7px;color:#64748b;'
      +      'text-transform:uppercase;margin-bottom:5px">'+ot('Lo que regalás')+'</div>'
      + '<div style="font-size:12px;color:#cbd5e1;line-height:1.6">'
      + '<b>'+(B+E)+'</b> '+ot('de tus')+' '+T+' '+ot('ataques terminan en punto del rival')
      + ' \u2014 '+ot('te bajan')+' <b style="color:#f87171">'+Math.round((B+E)/T*100)+'</b> '+ot('puntos.')
      + '</div></div>';
  }

  /* que le falta */
  var meta_txt = '';
  if(obj != null){
    if(Math.round(val) >= Math.round(obj)){
      meta_txt = '<div style="margin-top:13px;padding:10px 12px;background:rgba(34,197,94,.1);'
        + 'border:1px solid rgba(34,197,94,.3);border-radius:8px;font-size:12px;color:#86efac;line-height:1.5">'
        + '<b>Estás por encima del objetivo.</b> El equipo apunta a '+obj+'.</div>';
    } else {
      /* cada pelota que se deja de regalar suma 1 al neto */
      var faltan = Math.ceil((obj - val) * T / 100);
      var op = [];
      if(E >= faltan) op.push(ot('no fallar')+' <b>'+faltan+'</b> '+ot('de tus')+' '+E+' '+objPlural('Error',E));
      else if(B + E >= faltan) op.push(ot('no regalar')+' <b>'+faltan+'</b> '+ot('pelotas entre errores y bloqueados'));
      if(faltan <= T - P) op.push(ot('convertir')+' <b>'+faltan+'</b> '+ot('ataques más en punto'));
      meta_txt = '<div style="margin-top:13px;padding:10px 12px;background:rgba(251,191,36,.09);'
        + 'border:1px solid rgba(251,191,36,.28);border-radius:8px;font-size:12px;color:#cbd5e1;line-height:1.6">'
        + '<div style="color:#fbbf24;font-weight:800;margin-bottom:4px">'+ot('Para llegar a')+' '+obj+'</div>'
        + (op.length ? op.map(function(o){ return '\u2022 '+o; }).join('<br>')
                     : 'Con '+T+' ataques hace falta un salto grande: conviene mirarlo sobre más partidos.')
        + '</div>';
    }
  }

  /* ══ CUANDO SON MUY POCAS ACCIONES, HAY QUE DECIRLO ═══════════════════
     Caso real: Bartholet tenia -33% en "ataque tras recepcion #+". Suena
     grave. Pero son 3 ataques, y uno solo salio bloqueado.

     Un jugador ve -33% y se preocupa por algo que no significa nada: con 3
     pelotas, una bloqueada te manda a -33 y una de punto te manda a +33. El
     numero cambia 66 puntos por UNA accion.

     Ocultarlo seria peor. Mostrarlo sin avisar, tambien. Asi que se avisa. */
  var aviso = '';
  if(T < 10){
    aviso = '<div style="margin-top:11px;padding:9px 11px;background:rgba(148,163,184,.1);'
      + 'border:1px solid rgba(148,163,184,.25);border-radius:8px;font-size:11.5px;'
      + 'color:#cbd5e1;line-height:1.55">'
      + '<b style="color:#94a3b8">'+ot('Ojo: son pocas pelotas.')+'</b><br>'
      + ot('Con')+' '+T+' '+(T>1?ot('ataques'):ot('ataque'))+', '+ot('una sola cambia el número')+' '
      + Math.round(200/T)+' '+ot('puntos. Este porcentaje todavía no dice mucho: mirálo cuando haya más.')+'</div>';
  }

  var cuerpo = ''
   + '<div style="display:flex;height:9px;border-radius:5px;overflow:hidden;margin-bottom:11px">'+barra+'</div>'
   + '<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px">'
   +   '<span style="font-size:10px;font-weight:800;letter-spacing:.7px;color:#64748b;'
   +        'text-transform:uppercase">'+ot('Tus')+' '+T+' '+ot(cfg.pl||'ataques')+'</span>'
   +   '<span style="font-size:10px;color:#475569">'+ot('de cada 10')+'</span>'
   + '</div>'
   + '<div style="font-size:12.5px">'+lista+'</div>'
   + aviso + cuenta + cuesta + (T<10 ? '' : meta_txt);

  objPintarDetalle(nombre, obj, cuerpo, val, T, cfg.pl, quien);
}

function objMejorPalanca(cfg, D, total, suma, val, obj){
  var neutro = null;
  cfg.filas.forEach(function(f){ if(f[2]===50) neutro = f; });
  if(!neutro) return ot('Hace falta subir la calidad general.');
  var mejor = null;
  cfg.filas.forEach(function(f){
    if(f[2]==null || f[2] >= 50) return;
    var n = D[f[0]]||0; if(!n) return;
    var gana = (neutro[2] - f[2]) * n / total;
    if(!mejor || gana > mejor.gana) mejor = {f:f, n:n, gana:gana};
  });
  if(!mejor) return ot('Hace falta subir la calidad general.');
  var nuevo = val + mejor.gana;
  var txt = ot('Ningún cambio por separado alcanza. La palanca más grande:')+'<br>'
    + '\u2022 '+ot('no regalar')+' <b>' + mejor.n + ' ' + objPlural(mejor.f[1], mejor.n) + '</b>'
    + ' \u2192 '+ot('pasás de')+' <b>' + fmtEff(val) + '</b> a <b>' + fmtEff(nuevo) + '</b>';
  txt += (Math.round(nuevo) >= Math.round(obj)) ? ' '+ot('y llegás al objetivo.')
                                                : '. '+ot('Después hay que subir calidad.');
  return txt;
}

function objPlural(p, n){
  /* ══ EL PLURAL, EN EL IDIOMA QUE CORRESPONDA ══════════════════════════════
     Antes esto devolvia siempre castellano y el consejo quedaba mezclado:
     "turn 16 errors into suficientes". Ahora se traduce PRIMERO la palabra y
     despues se pluraliza segun el idioma. */
  var base = ot(String(p||''));
  var L = objIdioma();
  /* En castellano e ingles va en minuscula: aparece en medio de una frase
     —"turn 16 errors into fair balls"— y con mayuscula se lee raro.
     En aleman NO: ahi los sustantivos llevan mayuscula siempre. */
  if(L !== 'de') base = base.charAt(0).toLowerCase() + base.slice(1);
  if(n === 1) return base;
  if(L === 'es') return /[aeiou]$/.test(base) ? base + 's' : base + 'es';
  if(L === 'en') return /(s|x|z|ch|sh)$/i.test(base) ? base + 'es' : base + 's';
  return base;   /* aleman: el plural no siempre suma -s */
}


/* ══ DE LA VENTANITA AL REPRODUCTOR ═══════════════════════════════════════════
   El jugador toca "18" al lado de Error y ve esas 18 pelotas.

   La primera version que hice mostraba cualquier accion. El motivo: yo
   recorria los datos de video a mi manera, sin entender que el codigo de la
   sesion que traen las acciones NO es la clave del mapa de videos.

   Ahora el reproductor usa exactamente los datos y la logica de
   plan_partido, que ya tenia todo esto resuelto. Verificado contra el: para
   el mismo codigo devuelve el mismo video.

   Las claves internas de la ventana y lo que entiende el reproductor:
       fundamento   sq · rec · def · blq · atk
       valoracion   la letra del scout: # + ! - / = */
var OBJ_FUND = { sq:'sq', rec:'rec', def:'def', bqpos:'blq', bqpt:'blq',
                 atqq:'atk', atqhb:'atk', atqx:'atk',
                 atqrp:'atk', atqri:'atk', atqrm:'atk', atqtr:'atk' };


/* Del nombre que muestra la pantalla al numero de camiseta que necesita el
   reproductor. Se busca en PP_DATA, que es la misma fuente de las acciones. */
function objNumeroDe(nombre){
  /* ══ DEL NOMBRE AL NUMERO DE CAMISETA ═════════════════════════════════════
     Antes esto buscaba en PP_DATA. Pero PP_DATA venia de plan_partido_data.js,
     que eran ~1 MB que cargabamos solo para esto. Al sacarlo de las pantallas
     —que era lo correcto— objNumeroDe se quedo sin nada donde buscar y el
     enlace no se armaba.

     Ahora busca en el PLANTEL, que ya esta cargado en todas las pantallas y
     es la fuente unica de nombres y numeros del club. Sin descargar nada. */
  var n = String(nombre||'').trim().toUpperCase();
  if(!n) return null;

  /* si ya vino un numero */
  var d = n.match(/^#?\s*(\d{1,2})\b/);
  if(d) return Number(d[1]);

  function _cmp(a, b){
    a = String(a||'').trim().toUpperCase();
    b = String(b||'').trim().toUpperCase();
    if(!a || !b) return false;
    return a === b || a.indexOf(b) >= 0 || b.indexOf(a) >= 0;
  }

  /* 1. el plantel del club */
  try{
    var P = window.PLANTEL || window.PLANTEL_NAFELS || window.PLANTEL_CLUB;
    if(P && P.length){
      for(var i=0;i<P.length;i++){
        var j = P[i];
        if(_cmp(j.ap, n) || _cmp(j.nombre, n) || _cmp(j.name, n)
           || _cmp((j.ap||'') + ' ' + (j.nom||''), n)) return Number(j.num);
      }
    }
  }catch(e){}

  /* 2. lo que muestre la propia pantalla: "#11 BARTHOLET" */
  try{
    var els = document.querySelectorAll('#obj-jug-grid > *, .jug-card, .player-card');
    for(var k=0;k<els.length;k++){
      var t = (els[k].textContent||'').toUpperCase();
      var m = t.match(/#\s*(\d{1,2})/);
      if(m && t.indexOf(n) >= 0) return Number(m[1]);
    }
  }catch(e){}

  /* 3. PP_DATA, si esta (plan_partido la tiene) */
  try{
    var D = window.PP_DATA || {};
    for(var eq in D){
      var L = (D[eq] && D[eq].players) || [];
      for(var x=0;x<L.length;x++){ if(_cmp(L[x].name, n)) return Number(L[x].num); }
    }
  }catch(e){}

  return null;
}




/* Si la etiqueta de la fila nombra a un jugador, en los tres idiomas. */
function _esJugadorFila(t){
  return /jugador|player|spieler|joueur/i.test(String(t||''));
}

function objVerVideo(id, clave, nombreFila, cuantas, jugNombre){
  /* ══ EN EL PANEL EN VIVO, EL REPRODUCTOR DE AL LADO ══════════════════════
     Durante el partido cortes.html no sirve: necesita el .dvw ya subido y
     procesado, y todavia no existe. Ademas descarga 17 MB, que entre set y
     set es una eternidad.

     El panel en vivo tiene su propio reproductor —rvAbrir()— que usa el video
     que ya esta en pantalla y el segundo que guarda cada codigo. Si esa
     funcion existe, se usa esa. En las demas pantallas nada cambia. */
  if(typeof window.rvAbrir === 'function' && typeof window.rvBuscar === 'function'){
    try{
      var _c = OBJ_DETALLE[id];
      var _sk = ({sq:'S', rec:'R', def:'D', bqpos:'B', bqpt:'B'})[id]
                || (String(id).indexOf('atq')===0 ? 'A' : null);
      if(_sk){
        var _num = null;
        var _m = String(jugNombre||'').match(/(\d{1,2})/);
        if(_m) _num = parseInt(_m[1],10);
        var _ev = (clave && clave.length===1 && '#+!-/='.indexOf(clave)>=0) ? clave : null;
        var _lista = window.rvBuscar(_sk, _ev, _num);
        if(_lista.length){
          window.rvAbrir(_lista, (nombreFila||'') + ' · ' + _lista.length);
          return;
        }
      }
    }catch(e){}
  }

  /* ══ AL REPRODUCTOR QUE YA EXISTE ═════════════════════════════════════════
     cortes.html ya hace TODO esto: tiene las acciones filtradas, ordenadas,
     con su video, y el reproductor armado. Lo usan 9 pantallas del sistema
     —dashboard, los mapas de calor, informe de equipo, ataque_jugador—.

     Yo habia escrito un reproductor entero al lado. Era trabajo de mas y
     traia errores nuevos. Lo unico que hacia falta era pasarle los filtros.

     Los parametros son los suyos, tal cual los lee:
         num   el numero de camiseta (vacio = todo el equipo)
         sk    Saque · Recepción · Ataque · Bloqueo · Defensa · Armado
         ev    la valoracion: #  +  !  -  /  =
     La barra va codificada porque si no rompe la direccion. */
  try{
    var cfg = OBJ_DETALLE[id];
    if(!cfg) return;

    var sig = null;
    (cfg.filas||[]).forEach(function(f){ if(f[0] === clave) sig = f[4]; });
    if(!sig) sig = ({p:'#', b:'/', e:'='})[clave] || null;
    if(!sig) return;

    /* ══ CUANDO ES EL EQUIPO ══════════════════════════════════════════════
       Yo daba por equipo solo si la fila decia "Equipo". Pero las baterias
       del BLOQUE DE EQUIPO —las de arriba, sin jugador elegido— vienen con la
       fila VACIA, no con la palabra. Entonces las tomaba como de un jugador,
       no encontraba a nadie y saltaba el cartel.

       Ahora es al reves, que es lo correcto: se trata como jugador SOLO si
       hay un nombre de jugador. Sin nombre es el equipo, en cualquier idioma
       y con la fila vacia. */
    var jug = '';
    var _nomFila = String(nombreFila||'');
    var _esEquipo = !_nomFila
                 || /equipo|team|mannschaft|équipe|equipe/i.test(_nomFila)
                 || (!jugNombre && !_esJugadorFila(_nomFila));
    if(!_esEquipo){
      var nom = jugNombre || '';
      if(!nom){
        try{ nom = window._dbatNombre || window._objNombre || ''; }catch(e){}
      }
      var n = objNumeroDe(nom);
      if(!n){
        alert('No pude identificar al jugador para traer sus acciones.');
        return;
      }
      jug = String(n);
    }

    var q = [];
    if(jug) q.push('num=' + jug);
    q.push('sk=' + encodeURIComponent(OBJ_SKILL_NOMBRE[id] || ''));
    q.push('ev=' + encodeURIComponent(sig));

    /* ══ EL EQUIPO, LA RECEPCION Y EL TIPO ════════════════════════════════
       Antes el link llevaba jugador, fundamento y valoracion nada mas, y
       cortes abria con TODAS las acciones de ese numero: las del rival con
       el mismo dorsal incluidas, y sin distinguir de donde venia el ataque.
          team  de que equipo
          rq    con que recepcion se llego (#, + , ! , -)
          ty    el tipo de pelota (Q central, H alta, T rapida) */
    try{
      var _eq = '';
      if(window.CLUB_SLUG) _eq = window.CLUB_SLUG;
      else if(window.TEAM) _eq = window.TEAM;
      else if(window.LIGA_DATA){
        var _ks = Object.keys(window.LIGA_DATA);
        if(_ks.length === 1) _eq = _ks[0];
      }
      if(_eq) q.push('team=' + encodeURIComponent(_eq));

      var _rq = ({atqrp:'#,+', atqri:'!', atqrm:'-'})[id];
      if(_rq) q.push('rq=' + encodeURIComponent(_rq));
      else if(id === 'atqtr') q.push('ph=TR');

      var _ty = ({atqq:'Q', atqhb:'H', atqx:'T'})[id];
      if(_ty) q.push('ty=' + _ty);
    }catch(e){}

    window.open('cortes.html?' + q.join('&'), '_blank');
  }catch(e){}
}

/* El nombre del fundamento como lo espera cortes.html. */
var OBJ_SKILL_NOMBRE = {
  sq:'Saque', rec:'Recepción', def:'Defensa', bqpos:'Bloqueo', bqpt:'Bloqueo',
  atqq:'Ataque', atqhb:'Ataque', atqx:'Ataque',
  atqrp:'Ataque', atqri:'Ataque', atqrm:'Ataque', atqtr:'Ataque'
};


function objTocarBat(mid){
  try{
    var d = (window.__objMeta||{})[mid];
    if(!d) return;
    /* Los valores vienen guardados con la bateria: son los de SU fila y los
       de la sesion que esta elegida. No se adivinan. */
    var vals = d.vals;
    if(!vals && d.meta && d.meta.vals) vals = d.meta.vals;
    if(!vals){ try{ if(typeof objGetVals === 'function') vals = objGetVals(null); }catch(e){} }
    objAbrirDetalle(d.id, vals || {}, d.meta, d.quien);
  }catch(e){}
}

function objCerrarDetalle(){
  var v = document.getElementById('obj-detalle');
  if(v) v.remove();
  document.removeEventListener('keydown', objEscDetalle);
}
function objEscDetalle(e){ if(e.key==='Escape') objCerrarDetalle(); }
function objVerCuenta(){
  var c = document.getElementById('obj-cuenta');
  var b = document.getElementById('obj-cuenta-btn');
  if(!c) return;
  var ab = c.style.display === 'none';
  c.style.display = ab ? 'block' : 'none';
  if(b) b.textContent = ab ? 'ocultar la cuenta' : 'ver la cuenta completa';
}

function objAbrirDetalle(id, vals, meta, quien){
  objCerrarDetalle();
  var cfg = OBJ_DETALLE[id];
  var D   = cfg ? (vals && vals[cfg.d]) : null;
  /* Los ataques viven todos dentro de 'atqD', cada uno con su clave. */
  if(cfg && cfg.k && D) D = D[cfg.k] || null;
  var val = (vals && vals[id]!=null) ? vals[id] : null;
  var obj = (meta && meta.obj!=null) ? meta.obj : null;
  var nombre = ot((cfg && cfg.nom) || '')  || (cfg && cfg.nom) || String((meta&&meta.label)||'').replace(/\s*\(-?\d+\)\s*$/,'');

  if(!cfg || !D){
    objPintarDetalle(nombre, obj,
      '<div style="color:#64748b;font-size:12px;padding:8px 0;line-height:1.5">'
      + 'Para este fundamento todavía no hay desglose guardado.<br>Corré HACER_TODO y volvé a entrar.</div>');
    return;
  }

  /* ══ EL ATAQUE SE EXPLICA CON UNA RESTA ═══════════════════════════════ */
  if(cfg.tipo === 'atq'){
    objAtaqueDetalle(cfg, D, vals, id, meta, quien);
    return;
  }

  /* El nombre del jugador de ESTA ventana. Sale de la meta que guardo la
     bateria; si no vino, se cae a las globales de cada pantalla. */
  var _jugNom = '';
  try{
    _jugNom = (meta && meta.__jug) || window._dbatNombre || window._objNombre || '';
  }catch(e){}

  var total = 0, suma = 0;
  cfg.filas.forEach(function(f){
    var n = D[f[0]] || 0; total += n;
    if(f[2]!=null) suma += n * f[2];
  });
  if(cfg.tipo) total = D.t || total;
  if(!total){
    objPintarDetalle(nombre, obj,
      '<div style="color:#64748b;font-size:12px;padding:8px 0">Todavía no hay acciones de este fundamento.</div>');
    return;
  }

  /* ── 1. LA BARRA Y EL "DE CADA 10" ─────────────────────────────────────── */
  var barra = '', lista = '';
  cfg.filas.forEach(function(f){
    var n = D[f[0]] || 0;
    if(!n) return;
    var pc = n/total*100;
    barra += '<div title="'+ot(f[1])+': '+n+'" style="width:'+pc+'%;background:'+f[3]+'"></div>';
    var de10 = (n/total*10);
    /* El SIGNO va primero y bien visible: es el codigo que el jugador ve en
       el video y en la planilla. Sin el, "Perfecta" y "#" son dos idiomas.
       Despues el total, que es lo que de verdad hizo, y recien al final el
       "de cada 10", que sirve para imaginarlo. */
    lista += '<div style="display:flex;align-items:center;gap:8px;padding:3.5px 0">'
      + '<span style="width:19px;height:19px;border-radius:4px;background:'+f[3]+';color:#0f172a;'
      +    'font-weight:900;font-size:13px;display:flex;align-items:center;justify-content:center;'
      +    'flex:none;font-family:monospace">'+(f[4]||'')+'</span>'
      + '<span style="flex:1;color:#cbd5e1">'+ot(f[1])+'</span>'
      /* ══ EL NUMERO SE TOCA Y SE ABRE EL VIDEO ══════════════════════════
         Tocas "18" al lado de Error y ves esas 18 pelotas. El subrayado
         suave avisa que se puede tocar sin ensuciar la lectura. */
      + '<span onclick="objVerVideo(\''+id+'\',\''+f[0]+'\',\''+(quien||'').replace(/\'/g,'')+'\','+n+',\''+String(_jugNom||'').replace(/\'/g,'')+'\')" '
      +    'title="'+ot('Ver estas')+' '+n+' '+ot('acciones en video')+'" '
      +    'style="font-weight:900;color:#e2e8f0;min-width:30px;text-align:right;font-size:14px;'
      +    'cursor:pointer;text-decoration:underline;text-decoration-color:rgba(148,163,184,.4);'
      +    'text-underline-offset:3px">'+n+'</span>'
      + '<span style="color:#64748b;min-width:56px;text-align:right;font-size:11px">'
      /* SIEMPRE con un decimal. Con 1362 acciones, 260 y 336 pelotas daban
         "2 de 10" las dos: el redondeo borraba justo lo que se queria
         mostrar. Con decimal se ve 1.9 contra 2.5. */
      +    de10.toFixed(1)+' '+ot('de cada 10')+'</span>'
      + '</div>';
  });

  /* ── 2. QUE LE ESTA COSTANDO ───────────────────────────────────────────── */
  var cuesta = '';
  if(!cfg.tipo){
    var pierde = cfg.filas.filter(function(f){ return f[2]!=null && f[2]<100 && (D[f[0]]||0)>0; })
      .map(function(f){ return {nom:f[1], n:D[f[0]], p:(100-f[2])*D[f[0]]/total, c:f[3]}; })
      .sort(function(a,b){ return b.p-a.p; }).slice(0,2);
    if(pierde.length){
      cuesta = '<div style="margin-top:13px">'
        + '<div style="font-size:10px;font-weight:800;letter-spacing:.7px;color:#64748b;'
        +      'text-transform:uppercase;margin-bottom:5px">'+ot('Lo que más te cuesta')+'</div>';
      pierde.forEach(function(x){
        cuesta += '<div style="display:flex;align-items:center;gap:7px;padding:3px 0;font-size:12px">'
          + '<span style="width:9px;height:9px;border-radius:2px;background:'+x.c+';flex:none"></span>'
          + '<span style="flex:1;color:#cbd5e1">'+x.n+' '+objPlural(x.nom,x.n)+'</span>'
          + '<span style="color:#f87171;font-weight:800">\u2212'+Math.round(x.p)+'</span></div>';
      });
      cuesta += '</div>';
    }
  }

  /* ── 3. QUE LE FALTA PARA EL OBJETIVO ──────────────────────────────────── */
  var meta_txt = '';
  if(!cfg.tipo && obj!=null && val!=null){
    if(val >= obj){
      meta_txt = '<div style="margin-top:13px;padding:10px 12px;background:rgba(34,197,94,.1);'
        + 'border:1px solid rgba(34,197,94,.3);border-radius:8px;font-size:12px;color:#86efac;line-height:1.5">'
        + '<b>Estás por encima del objetivo.</b> El equipo apunta a '+obj+' y vos vas '
        + Math.round(val-obj)+' arriba.</div>';
    } else {
      /* ══ QUE TIENE QUE PASAR PARA LLEGAR AL OBJETIVO ════════════════════
         La primera version proponia subir cada pelota UN escalon. Eso da
         consejos que nadie puede usar: "convertir 31 positivas en perfectas"
         es pedirle a un jugador que sea perfecto.

         Un entrenador no dice eso. Dice "no me regales pelotas": primero se
         corta lo que se REGALA —errores y sobrepases— y recien despues se
         busca calidad. Asi que:

           · las pelotas MALAS (por debajo de neutra) se llevan a NEUTRA.
             Es lo mas realista: no fallar.
           · las de neutra para arriba suben un escalon.

         Y se muestra primero lo que salga de arreglar lo peor. */
      var falta = (obj - val) * total;
      var opciones = [];
      var neutro = null;
      cfg.filas.forEach(function(f){ if(f[2]===50) neutro = f; });
      cfg.filas.forEach(function(f,i){
        if(f[2]==null || i===0) return;
        var n = D[f[0]]||0; if(!n) return;
        var destino = (neutro && f[2] < 50) ? neutro : cfg.filas[i-1];
        var gana = destino[2] - f[2];
        if(gana <= 0) return;
        var cuantas = Math.ceil(falta/gana);
        if(cuantas>0 && cuantas<=n){
          opciones.push({
            txt: ot('convertir')+' <b>'+cuantas+' '+objPlural(f[1],cuantas)
                 +'</b> '+ot('en')+' '+objPlural(destino[1],cuantas),
            malo: (f[2] < 50) ? 0 : 1,
            n: cuantas
          });
        }
      });
      /* primero arreglar lo peor; entre iguales, lo que pide menos cambios */
      opciones.sort(function(a,b){ return (a.malo-b.malo) || (a.n-b.n); });
      meta_txt = '<div style="margin-top:13px;padding:10px 12px;background:rgba(251,191,36,.09);'
        + 'border:1px solid rgba(251,191,36,.28);border-radius:8px;font-size:12px;color:#cbd5e1;line-height:1.6">'
        + '<div style="color:#fbbf24;font-weight:800;margin-bottom:4px">'+ot('Para llegar a')+' '+obj+'</div>'
        + (opciones.length
            ? opciones.slice(0,2).map(function(o){ return '\u2022 '+o.txt; }).join('<br>')
            : objMejorPalanca(cfg, D, total, suma, val, obj))
        + '</div>';
    }
  }
  if(cfg.tipo){
    meta_txt = '<div style="margin-top:13px;padding:10px 12px;background:rgba(148,163,184,.08);'
      + 'border-radius:8px;font-size:12px;color:#94a3b8;line-height:1.5">'
      + (cfg.tipo==='bqpt' ? (D.p||0)+' bloqueos terminaron en punto'
                           : (D.p||0)+' en punto y '+(D.o||0)+' en positivo')
      + ' sobre <b style="color:#cbd5e1">'+total+'</b>.</div>';
  }

  /* ── la cuenta, plegada, para el cuerpo tecnico ─────────────────────────── */
  var tabla = '';
  if(!cfg.tipo){
    cfg.filas.forEach(function(f){
      var n = D[f[0]]||0; if(!n) return;
      tabla += '<tr><td style="padding:3px 6px;color:#94a3b8">'+ot(f[1])+'</td>'
        + '<td style="padding:3px 6px;text-align:right;color:#cbd5e1">'+n+'</td>'
        + '<td style="padding:3px 6px;text-align:right;color:#64748b">\u00d7'+f[2]+'</td>'
        + '<td style="padding:3px 6px;text-align:right;color:#94a3b8">'+Math.round(n*f[2])+'</td></tr>';
    });
    tabla = '<table style="width:100%;border-collapse:collapse;font-size:11px">'+tabla+'</table>'
      + '<div style="margin-top:6px;color:#64748b;font-size:11px;line-height:1.5">'
      + Math.round(suma)+' \u00f7 '+total+' = <b style="color:#94a3b8">'+(val!=null?fmtEff(val):'\u2014')+'</b>'
      + '<br>Es un promedio: 100 es una pelota perfecta, 50 una neutra.</div>';
  }

  /* ══ LA CUENTA, A LA VISTA ═══════════════════════════════════════════════
     Estaba plegada detras de "ver la cuenta completa". Pero la pregunta que
     el jugador se hace primero es "de donde sale ese numero", asi que tiene
     que verla sin buscarla.

     Se muestra en dos renglones cortos: la suma de lo que vale cada pelota,
     y la division por el total. Nada de tablas. */
  var cuentaVisible = '';
  if(!cfg.tipo){
    var partes = [];
    cfg.filas.forEach(function(f){
      var n = D[f[0]]||0;
      if(n) partes.push(n+'\u00d7'+f[2]);
    });
    cuentaVisible = '<div style="margin-top:11px;padding:9px 11px;background:rgba(148,163,184,.07);'
      + 'border-radius:8px;font-size:11.5px;color:#94a3b8;line-height:1.7">'
      + '<div style="font-size:10px;font-weight:800;letter-spacing:.7px;color:#64748b;'
      +      'text-transform:uppercase;margin-bottom:3px">'+ot('Cómo se llega a')+' '
      +      (val!=null?fmtEff(val):'\u2014')+'</div>'
      + partes.join(' + ')
      + '<br><b style="color:#cbd5e1">'+Math.round(suma)+'</b> \u00f7 <b style="color:#cbd5e1">'
      + total+'</b> = <b style="color:#e2e8f0;font-size:14px">'+(val!=null?fmtEff(val):'\u2014')+'</b>'
      + '</div>';
  }

  /* El mismo aviso que en el ataque: con pocas acciones el numero se mueve
     demasiado por una sola pelota y no significa nada todavia. */
  var aviso2 = '';
  if(total < 15){
    aviso2 = '<div style="margin-top:11px;padding:9px 11px;background:rgba(148,163,184,.1);'
      + 'border:1px solid rgba(148,163,184,.25);border-radius:8px;font-size:11.5px;'
      + 'color:#cbd5e1;line-height:1.55">'
      + '<b style="color:#94a3b8">'+ot('Ojo: son pocas acciones.')+'</b><br>'
      + ot('Con')+' '+total+', '+ot('una sola cambia bastante el número. Mirálo cuando haya más.')+'</div>';
  }

  var cuerpo = ''
   + '<div style="display:flex;height:9px;border-radius:5px;overflow:hidden;margin-bottom:11px">'+barra+'</div>'
   + '<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px">'
   +   '<span style="font-size:10px;font-weight:800;letter-spacing:.7px;color:#64748b;'
   +        'text-transform:uppercase">'+ot('Tus')+' '+total+' '+ot(cfg.pl||'acciones')+'</span>'
   +   '<span style="font-size:10px;color:#475569">'+ot('de cada 10')+'</span>'
   + '</div>'
   + '<div style="font-size:12.5px">'+lista+'</div>'
   + aviso2 + cuentaVisible + cuesta + (total<15 ? '' : meta_txt)
   /* La leyenda de pesos se arma con la MISMA tabla que hace la cuenta.
      Si algun dia cambia la escala, este texto cambia solo. */
   + (cfg.tipo ? '' :
      '<div style="margin-top:9px;font-size:10.5px;color:#475569;line-height:1.5">'
      + ot('Cada pelota vale según cómo quedó:')+' '
      + cfg.filas.map(function(f){ return f[4]+' '+ot('vale')+' '+String(f[2]).replace('.',','); }).join(' \u00b7 ')
      + '. '+ot('El resultado es el promedio.')+'</div>');

  objPintarDetalle(nombre, obj, cuerpo, val, total, cfg.pl, quien);
}

function objPintarDetalle(nombre, obj, cuerpo, val, total, pl, quien){
  var cab = ''
   + '<div style="display:flex;align-items:flex-start;justify-content:space-between;gap:10px;'
   +      'padding:12px 14px;border-bottom:1px solid rgba(148,163,184,.16)">'
   +   '<div>'
   /* ══ DE QUIEN Y DE QUE SESION ══════════════════════════════════════
      Antes la ventana no lo decia. Si tocabas la bateria de un jugador y
      veias numeros, no habia forma de estar seguro de que fueran suyos y
      no del equipo. Ahora lo dice arriba, junto al fundamento. */
   +     (quien ? '<div style="font-size:10px;font-weight:800;letter-spacing:.8px;'
   +          'color:#22c55e;text-transform:uppercase;margin-bottom:1px">'+quien+'</div>' : '')
   +     '<div style="font-size:13px;font-weight:800;letter-spacing:.6px;color:#e2e8f0;'
   +          'text-transform:uppercase">'+nombre+'</div>'
   +     (total!=null
        ? '<div style="font-size:10.5px;color:#64748b;margin-top:2px">'+total+' '+ot(pl||'acciones')
          + (obj!=null ? ' \u00b7 '+ot('objetivo')+' '+obj : '')+'</div>'
        : (obj!=null ? '<div style="font-size:10.5px;color:#64748b;margin-top:2px">'+ot('objetivo')+' '+obj+'</div>' : ''))
   +   '</div>'
   +   (val!=null
       ? '<div style="font-size:27px;font-weight:900;color:#e2e8f0;line-height:1">'+fmtEff(val)+'</div>'
       : '')
   + '</div>';

  var html = ''
   + '<div id="obj-detalle" style="position:fixed;inset:0;z-index:9000;display:flex;'
   +      'align-items:center;justify-content:center;background:rgba(2,6,23,.74);padding:16px">'
   + '<div style="background:#0f172a;border:1px solid rgba(148,163,184,.25);border-radius:14px;'
   +      'max-width:340px;width:100%;max-height:88vh;overflow:auto;'
   +      'box-shadow:0 20px 55px rgba(0,0,0,.65);font-family:Barlow Condensed,sans-serif">'
   +   '<div style="position:sticky;top:0;background:#0f172a;z-index:1">'+cab+'</div>'
   +   '<div style="padding:12px 14px 14px">'+cuerpo+'</div>'
   +   '<div style="padding:0 14px 13px">'
   +     '<button onclick="objCerrarDetalle()" style="width:100%;padding:8px;background:rgba(148,163,184,.1);'
   +        'border:1px solid rgba(148,163,184,.2);border-radius:8px;color:#cbd5e1;font-size:12px;'
   +        'font-weight:700;cursor:pointer;font-family:inherit">'+ot('Cerrar')+'</button>'
   +   '</div>'
   + '</div></div>';

  var cont = document.createElement('div');
  cont.innerHTML = html;
  var nodo = cont.firstChild;
  nodo.addEventListener('click', function(e){ if(e.target===nodo) objCerrarDetalle(); });
  document.body.appendChild(nodo);
  document.addEventListener('keydown', objEscDetalle);
}

function objSingleBat(id,val,meta,cls,objLine,vals){
  /* ══ 'vals' ES EL DATO DE ESTA FILA ══════════════════════════════════════
     Sin esto la ventanita mostraba SIEMPRE los numeros del equipo, aunque
     tocaras la bateria de un jugador. Y tampoco distinguia si estabas viendo
     el acumulado, un entrenamiento o un partido.

     La pantalla ya tiene los valores correctos de cada fila —los usa para
     pintar la bateria—; lo unico que faltaba era pasarlos. Ahora viajan con
     la bateria y la ventana muestra exactamente lo que se esta viendo. */
  /* ══ UNA SOLA VERSION, IGUAL EN TODOS LADOS ═══════════════════════════════
     Habia CINCO copias de esta funcion y CUATRO eran distintas entre si:
     algunas con el nombre del fundamento, otras sin el; algunas con el total
     de acciones, otras sin. La bateria se veia de una forma u otra segun por
     que pantalla entraras.

     Esta es la unica version. Si hay que cambiar algo, se cambia aca y vale
     para todas.

     Muestra: el fundamento, el valor, la bateria con la linea del objetivo,
     sobre cuantas acciones esta hecha la cuenta, y el objetivo. */
  var fh = (val!==null) ? objPct(val, meta.min, meta.max) : 0;
  var oh = objPct(objLine, meta.min, meta.max);
  var txt = (val!==null) ? fmtEff(val) : '\u2014';
  /* El nombre del globo salia de la etiqueta sin pasar por el traductor: la
     bateria decia "% Reception" y el globo "% Recepción". */
  var nombre = ot(String(meta.label||'').replace(/\s*\(-?\d+\)\s*$/, ''));
  var n = (meta.n!=null) ? meta.n : null;
  var tip = nombre;
  try{
    if(val!==null && meta.obj!=null && meta.min!=null && meta.obj>meta.min){
      var reco = Math.round((val-meta.min)/(meta.obj-meta.min)*100);
      tip = nombre+': '+val+'%'+(n!=null?' '+ot('sobre')+' '+n+' '+ot('acciones'):'')
          + ' \u00b7 '+ot('el peor de la liga')+' '+meta.min+'%, '+ot('el mejor')+' '+meta.obj+'%'
          + ' \u00b7 '+ot('estás al')+' '+reco+'% '+ot('del recorrido');
    }
  }catch(e){}
  /* La bateria se toca y se abre el detalle. */
  var _mid = 'b'+id+'_'+Math.random().toString(36).slice(2,8);
  try{ window.__objMeta = window.__objMeta || {}; window.__objMeta[_mid] = {id:id, meta:meta, vals:vals||null,
      quien:(meta&&meta.__fila)||null,
      jug:(meta&&meta.__jug)||null}; }catch(e){}
  return '<div id="'+_mid+'" title="'+tip+'" onclick="objTocarBat(\''+_mid+'\')" '
    + 'style="flex:1;min-width:60px;max-width:110px;display:flex;cursor:pointer;'
    + 'flex-direction:column;align-items:center;gap:3px;padding:7px 3px 6px;'
    + 'border:1px solid '+cls.border+';border-radius:9px;background:'+cls.bg+';'
    + 'position:relative;overflow:hidden;font-family:Barlow Condensed,sans-serif">'
    + '<div style="position:absolute;top:0;left:0;right:0;height:3px;background:'+cls.color+'"></div>'
    + '<div style="font-size:10px;font-weight:800;letter-spacing:.3px;text-transform:uppercase;'
    + 'color:#94a3b8;line-height:1.1;text-align:center;white-space:nowrap;overflow:hidden;'
    + 'text-overflow:ellipsis;max-width:100%">'+nombre+'</div>'
    + '<div style="font-size:22px;font-weight:900;line-height:1;color:'+cls.color+'">'+txt+'</div>'
    + '<div style="width:32px;height:72px;display:flex;flex-direction:column;align-items:center">'
      + '<div style="width:14px;height:5px;border-radius:3px 3px 0 0;background:'+cls.color+';opacity:.7;flex-shrink:0"></div>'
      + '<div style="position:relative;width:32px;flex:1;border-radius:4px;overflow:hidden;border:2px solid '+cls.color+'">'
        + '<div style="position:absolute;inset:0;background:#07080f"></div>'
        + (val!==null ? '<div style="position:absolute;bottom:0;left:0;right:0;height:'+fh+'%;background:'+cls.color+';opacity:.85"></div>' : '')
        + '<div style="position:absolute;left:0;right:0;bottom:'+oh+'%;height:2px;background:#fff;opacity:.85"></div>'
      + '</div>'
    + '</div>'
    + (n!=null ? '<div style="font-size:8px;font-weight:700;color:#8395ac">'+n+' '+ot('acc.')+'</div>' : '')
    + '<div style="font-size:8px;font-weight:700;color:#64748b">'+ot('obj')+' '+objLine+'</div>'
    + '</div>';
}

/* ══ ESTA ES LA UNICA BATERIA DEL SISTEMA ═══════════════════════════════════
   Se publica con un nombre propio —__objSingleBatReal— para que las copias
   viejas de objetivos.js, utils.js e historial_voley.html puedan reenviar
   aca sin pisarla, cargue quien cargue ultimo.

   Antes, en analisis.html y panel_voley.html ganaba la copia vieja y la
   bateria no se podia tocar. Ahora da igual el orden: la que dibuja es
   siempre esta. */
window.__objSingleBatReal = objSingleBat;

function renderObjetivos(cid,extra){
  var el=document.getElementById(cid); if(!el) return;
  var metas=window.OBJETIVOS_CONFIG.metas;
  var vals=Object.assign({},typeof objGetVals!=="undefined"?objGetVals(null):objCalcVals(null),extra||{});
  var html='<div style="font-family:Barlow Condensed,sans-serif;padding:4px 0 8px">'
    +'<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:10px">'
    +'<div style="font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#64748b">OBJETIVOS DEL EQUIPO'+(window.__TEMP_TITULO||'')+'</div>'
    +'<div style="display:flex;gap:10px;flex-wrap:wrap">'
    +[['#22c55e',ot('Objetivo')],['#86efac',ot('Cerca')],['#fbbf24',ot('Neutro')],['#ef4444',ot('Lejos')]].map(function(x){
      return'<div style="display:flex;align-items:center;gap:4px;font-size:9px;color:#64748b"><div style="width:7px;height:7px;border-radius:50%;background:'+x[0]+'"></div>'+x[1]+'</div>';
    }).join('')+'</div></div>'
    /* ══ UNA SOLA FILA, PARA QUE ENTRE EN EL TELEVISOR ══════════════════
       OJO: hay DOS renderObjetivos en este archivo y la que manda es ESTA,
       la segunda, porque se declara despues. Modificar solo la de arriba no
       cambia nada en pantalla.

       Antes eran dos filas —una con el nombre y el objetivo, otra con la
       bateria— que sumaban mas de 200px. En la tele habia que subir y bajar
       la pagina para ver los doce. Y el objetivo salia repetido: la etiqueta
       ya dice "% Saque (42)" y abajo aparecia otra vez "42%".            */
    +'<div style="display:flex;gap:6px;width:100%;flex-wrap:nowrap">'
    +Object.keys(metas).map(function(id){
      var m=metas[id],val=vals[id]!==undefined?vals[id]:null;
      var cls=val!==null?objClassify(id,val):{color:'#334155',bg:'rgba(51,65,85,.08)',border:'rgba(51,65,85,.2)',label:'—'};
      /* El total de acciones viaja con la meta: es lo que permite leer bien el
         numero. Un 40% de 5 acciones y un 20% de 238 no valen lo mismo. */
      try{ if(vals['n_'+id]!=null) m=Object.assign({},m,{n:vals['n_'+id]}); }catch(e){}
      return objSingleBat(id,val,m,cls,m.obj);
    }).join('')+'</div></div>';
  el.innerHTML=html;
}

function renderObjetivosJugador(cid,nombre,extra){
  var el=document.getElementById(cid); if(!el) return;
  var metas=window.OBJETIVOS_CONFIG.metas;
  /* Los numeros del jugador, de la misma fuente que el resto. */
  var _bj = (typeof objGetVals === 'function') ? objGetVals(nombre) : objCalcVals(nombre);
  var jugVals=Object.assign({},_bj,extra||{});
  var eqVals=(typeof objGetVals === 'function') ? objGetVals(null) : objCalcVals(null);
  var rows=[{label:'Jugador',vals:jugVals,isJug:true},{label:'Equipo',vals:eqVals,isJug:false}];
  var html='<div style="font-family:Barlow Condensed,sans-serif;padding:4px 0 8px">'
    +'<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:10px">'
    +'<div style="font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#64748b">MI PERFORMANCE VS EQUIPO</div>'
    +'<div style="display:flex;gap:10px;flex-wrap:wrap">'
    /* La leyenda decia "Sobre equipo" / "Bajo equipo" porque el jugador se
       comparaba contra su propio equipo. Ahora se compara contra el objetivo,
       igual que la fila del equipo, asi que dice lo mismo que las demas. */
    +[['#22c55e',ot('Objetivo')],['#86efac',ot('Cerca')],['#fbbf24',ot('Neutro')],['#ef4444',ot('Lejos')]].map(function(x){
      return'<div style="display:flex;align-items:center;gap:4px;font-size:9px;color:#64748b"><div style="width:7px;height:7px;border-radius:50%;background:'+x[0]+'"></div>'+x[1]+'</div>';
    }).join('')+'</div></div>'
    /* ══ SE SACO LA FILA DE ENCABEZADO ════════════════════════════════════
       Repetia el nombre y el objetivo de cada fundamento arriba de las
       tarjetas, y las tarjetas YA los muestran: el nombre arriba y "obj 42"
       abajo. Quedaba todo escrito dos veces —"% SERVE (42)" y "42%" en el
       encabezado, "% SERVE" y "obj 42" en la tarjeta— y ocupaba una fila
       entera de alto sin agregar nada. */
    ;
  rows.forEach(function(row){
    html+='<div style="display:flex;align-items:center;gap:8px;width:100%;margin-bottom:8px">'
      +'<div style="width:64px;flex-shrink:0;font-size:10px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:#94a3b8;text-align:right;padding-right:8px">'+row.label+'</div>'
      +Object.keys(metas).map(function(id){
        var m=metas[id],val=row.vals[id]!==undefined?row.vals[id]:null;
        var cls,objLine;
        if(row.isJug){
          /* ══ EL MISMO OBJETIVO PARA TODOS ═══════════════════════════════
             Antes al jugador se lo comparaba contra el promedio de SU EQUIPO
             en vez de contra el objetivo. Eso traia dos problemas:

               · parecia que a cada uno se le pedia algo distinto: la fila del
                 jugador decia "obj 75" y la del equipo "obj 60". Ese 75 no
                 era un objetivo, era el numero del equipo.

               · un jugador podia estar "sobre el equipo" y aun asi lejos del
                 objetivo. El verde decia que estaba bien cuando no lo estaba.

             El objetivo es uno solo y lo fija el cuerpo tecnico: el del
             equipo. Ahora las dos filas se miden contra lo mismo. */
          cls=val!==null?objClassify(id,val):{color:'#334155',bg:'rgba(51,65,85,.08)',border:'rgba(51,65,85,.2)',label:'—'};
          objLine=m.obj;
        } else {
          cls=val!==null?objClassify(id,val):{color:'#334155',bg:'rgba(51,65,85,.08)',border:'rgba(51,65,85,.2)',label:'—'};
          objLine=m.obj;
        }
        return objSingleBat(id,val,m,cls,objLine);
      }).join('')+'</div>';
  });
  html+='</div>';
  el.innerHTML=html;
}
function buildObjSubfiltro(nombreJugador){
  var row = document.getElementById('obj-partido-row');
  if(!row) return;
  if(typeof PARTIDOS_META === 'undefined'){ row.style.display='none'; return; }
  row.innerHTML = '';
  row.style.display = 'flex';

  // Label
  var lbl = document.createElement('span');
  lbl.style.cssText = 'font-size:9px;color:#475569;letter-spacing:2px;text-transform:uppercase;align-self:center;margin-right:4px';
  lbl.textContent = 'VER:';
  row.appendChild(lbl);

  // Acumulado button
  var b = document.createElement('button');
  b.className = 'obj-sfbtn' + (currentObjPartido==='acumulado'?' on':'');
  b.textContent = 'Acumulado';
  b.onclick = function(){
    window.window.currentObjPartido = 'acumulado';
    document.querySelectorAll('.obj-sfbtn').forEach(function(x){x.classList.remove('on');});
    b.classList.add('on');
    renderObjetivosJugador('objetivos-jugador', nombreJugador);
  };
  row.appendChild(b);

  // Per-partido buttons
  PARTIDOS_META.forEach(function(m){
    var btn = document.createElement('button');
    btn.className = 'obj-sfbtn' + (window.currentObjPartido===m.nombre?' on':'');
    var label = m.rival||m.nombre;
    if(m.resultado) label += ' ('+m.resultado+')';
    btn.textContent = label;
    btn.onclick = function(){
      window.currentObjPartido = m.nombre;
      document.querySelectorAll('.obj-sfbtn').forEach(function(x){x.classList.remove('on');});
      btn.classList.add('on');
      renderObjetivosJugador('objetivos-jugador', nombreJugador);
    };
    row.appendChild(btn);
  });
}
function setObjTipo(tipo, btn){
  window.currentObjTipo = tipo;
  window.window.currentObjPartido = 'acumulado';
  document.querySelectorAll('.obj-tfbtn').forEach(function(b){
    b.classList.remove('on','partido','ent');
  });
  btn.classList.add('on', tipo==='partido'?'partido':'ent');
  // Rebuild subfiltro for this tipo
  var currentJugNombre = null;
  var titleEl = document.querySelector('.player-name-title');
  if(titleEl) currentJugNombre = titleEl.dataset.nombre;
  buildObjSubfiltro(currentJugNombre || '');
  renderObjetivosJugador('objetivos-jugador', currentJugNombre || '');
}
