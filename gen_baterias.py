import re
# -*- coding: utf-8 -*-
"""
gen_baterias.py — Genera las baterías de los 13 partidos leyendo los DVW crudos,
usando EXACTAMENTE el mismo motor que objetivos.js (panel/scout en vivo).

Uso:  python gen_baterias.py "CARPETA DVW CASLA 2026" [salida.js]
Salida: datos_baterias.js  ->  window.BAT_PARTIDOS = {total, meta, jug, ind, eq}
"""
import os, re, sys, json, glob, unicodedata

# ── equipos (igual que build_video.py) ──
# ── LOS EQUIPOS ────────────────────────────────────────────────────────────
#    Antes iba la tabla de un club escrita a mano. Ahora los nombres salen de
#    los propios .dvw, así el motor sirve en cualquier club sin tocarlo.
TEAM_NORM = {}



# ══════════════════════════════════════════════════════════════════════════
#  LA MAQUINA DE SAQUE
#  ------------------------------------------------------------------------
#  En los entrenamientos se scoutea la maquina con un numero de camiseta que
#  no existe en el plantel (en Näfels es el 8). Eso permite hacer el
#  ejercicio, pero sus saques NO SON DE NADIE: no los tira una persona, no
#  tienen intencion ni tecnica, y sumarlos a la estadistica de saque del
#  equipo la deforma. Eran 276 de 1.424, el 19%.
#
#  Las RECEPCIONES de esos saques SI cuentan: el jugador esta entrenando
#  justamente eso, recibir pelotas potentes.
#
#  Tampoco se toca la logica de fases: el saque de la maquina igual abre el
#  punto, asi que la recepcion y el ataque posterior siguen clasificando
#  bien como side-out.
#
#  El numero sale de la configuracion del club. Si algun dia se usa otro, o
#  se agrega una segunda maquina, se cambia ahi y no en el codigo.
# ══════════════════════════════════════════════════════════════════════════

# ══ LOS TORNEOS DE ESTE CLUB ════════════════════════════════════════════════
#  Esta funcion es propia de este club: resuelve a que temporada pertenece
#  una fecha cuando el torneo cruza dos anios. El club de origen del resto
#  del archivo no la necesita, pero aca si, y sin ella las baterias quedan
#  en la temporada equivocada.
def _temp_config(date, carpeta=''):
    try:
        import config_club as _cc
        if _cc.torneos():
            t = _cc.temporada_de(date, '', carpeta)
            if t:
                tor = _cc.resolver_torneo('', carpeta)
                cfg = _cc.torneos().get(tor) or {}
                if cfg.get('cruza'):
                    return "%d/%02d" % (int(t), (int(t) + 1) % 100)
                return str(t)
    except Exception:
        pass
    return None

def _es_maquina(num):
    """Si este numero de camiseta es una maquina y no un jugador."""
    try:
        import os, json
        global _MAQ_CACHE
    except Exception:
        pass
    return str(num).lstrip('0') in _MAQUINAS


def _cargar_maquinas():
    """Los numeros de maquina salen de config_club.json si existe."""
    import os, json
    for p in ('config_club.json', 'club.json', 'CONFIG.json'):
        try:
            if os.path.exists(p):
                c = json.load(open(p, encoding='utf-8'))
                v = c.get('maquinas_saque') or c.get('maquina_saque')
                if v:
                    if not isinstance(v, (list, tuple)): v = [v]
                    return {str(x).lstrip('0') for x in v}
        except Exception:
            pass
    return {'8'}          # el valor de Näfels, por defecto

_MAQUINAS = _cargar_maquinas()


def _cargar_equipos(carpeta):
    """Arma la tabla de nombres leyendo los partidos de la carpeta."""
    import unicodedata
    global TEAM_NORM
    vistos = {}
    for f in sorted(glob.glob(os.path.join(carpeta, '*.dvw'))):
        try:
            txt = read_dvw(f)
        except Exception:
            continue
        lin = txt.split('\n')
        i = [k for k, l in enumerate(lin) if l.strip().upper() == '[3TEAMS]']
        if not i:
            continue
        for k in (1, 2):
            try:
                n = lin[i[0] + k].split(';')[1].strip()
            except Exception:
                continue
            if not n or n in vistos:
                continue
            t = unicodedata.normalize('NFKD', n).encode('ascii', 'ignore').decode()
            t = re.sub(r'\([^)]*\)', ' ', t)
            relleno = ('club', 'atletico', 'atltico', 'volley', 'voley', 'de', 'del',
                       'la', 'las', 'los', 'y', 'd', 's', 'municipio', 'universidad',
                       'ciudad', 'nacional', 'stv', 'sc', 'vbc')
            pal = [w for w in re.split(r'[^A-Za-z0-9]+', t) if w]
            ut = [w for w in pal if w.lower() not in relleno and len(w) > 2]
            corto = (ut[0].capitalize() if ut else (pal[0] if pal else n[:10]))
            vistos[n] = corto
    TEAM_NORM = dict(vistos)
    return TEAM_NORM
NUESTRO = ['']          # se completa al arrancar, con el nombre del club


def is_casla(n):
    """Si este equipo es el nuestro.

       El nombre del club sale de la carpeta de partidos —"DVW NAFELS 2026" da
       "nafels"— y se compara sin acentos. Antes estaba escrito adentro y el
       motor sólo servía para un club."""
    import unicodedata
    if not n: return False
    t = unicodedata.normalize('NFKD', n).encode('ascii', 'ignore').decode().lower()
    plano = re.sub(r'[^a-z0-9]', '', t)

    # ══ TAMBIEN POR EL NOMBRE LARGO ══════════════════════════════════════════
    #  La clave sale del nombre de la carpeta: "DVW GELP 2026" da "gelp". Pero
    #  en el .dvw el club figura con su nombre completo:
    #      "Club Gimnasia y Esgrima de La Plata"
    #  y "gelp" no aparece ahi. Resultado: parse_dvw devolvia None para TODOS
    #  los partidos, el generador decia "0 sesiones" y datos_baterias.js salia
    #  vacio (3 KB). Las baterias se dibujaban sin datos.
    #
    #  Ahora se prueba tambien con lo que declara config_club: el nombre
    #  completo y el equipo propio.
    try:
        import config_club as _cc
        for _cand in (_cc.nombre_completo(), _cc.equipo_propio()):
            if not _cand: continue
            _c = unicodedata.normalize('NFKD', _cand).encode('ascii','ignore').decode().lower()
            _c = re.sub(r'[^a-z0-9]', '', _c)
            if _c and (_c in plano or plano in _c):
                return True
    except Exception:
        pass

    clave = (NUESTRO[0] or '').lower()
    if not clave: return False
    return clave in plano or clave in t
def norm_team(name):
    n=(name or '').strip()
    if n in TEAM_NORM: return TEAM_NORM[n]
    base=re.sub(r'\(NLA[^)]*\)','',n)
    base=re.sub(r'\b(Club|Atl[eé]tico|Ciudad de|Nautico|Universidad( Nacional)?( de)?|Municipio de|Ferro Carril|S\. y D\.|de|Volley|Volleyball)\b','',base,flags=re.I)
    return re.sub(r'\s+',' ',base).strip() or 'Rival'

# ══════════ MOTOR DE BATERÍAS — PORT EXACTO DE objetivos.js ══════════
def _bat_nuevo():
    na=lambda:{'#':0,'/':0,'=':0,'T':0}
    # 'D' = defensa. Se agrego porque el recuadro de Defensa del dashboard era
    # el unico que quedaba en cero: se contaba desde el archivo de VIDEO, que
    # el dashboard ni siquiera carga, asi que nunca se llenaba. Los .dvw traen
    # la defensa como cualquier otro fundamento.
    # El '-' (negativo) no se guardaba: hasta ahora ninguna formula lo usaba,
    # valia cero igual que el neutro. La escala nueva SI lo usa, asi que hay
    # que contarlo o restaria siempre cero y no cambiaria nada.
    # El '!' (neutro) tampoco se guardaba: con la escala vieja valia cero y
    # daba igual. En la escala de 0 a 100 el neutro vale 50, asi que si no se
    # cuenta, cada saque neutro puntuaria 0 y el numero se hunde.
    return {'S':{'#':0,'+':0,'!':0,'-':0,'/':0,'=':0,'T':0},
            'R':{'#':0,'+':0,'!':0,'-':0,'/':0,'=':0,'T':0},
            # el bloqueo guardaba solo # y +: la columna Error salia vacia
        'B':{'#':0,'+':0,'!':0,'-':0,'/':0,'=':0,'T':0},
            'D':{'#':0,'+':0,'!':0,'-':0,'=':0,'T':0},
            'Aall':na(),'cent':na(),'alta':na(),'rap':na(),
            'rp':na(),'ri':na(),'rm':na(),'tr':na()}

def _calc_baterias(codes, side):
    pl={}
    def get(num):
        if num not in pl: pl[num]=_bat_nuevo()
        return pl[num]
    last_rec=None; rec_valida=False
    for line in codes:
        l=(line or '').strip()
        if len(l)<5: continue
        pfx=l[0]; body=l[1:].split(';')[0]
        if len(body)<5 or not re.match(r'^\d\d', body): continue
        num=body[0:2]; skill=body[2]; res=body[4]
        if skill=='S':
            last_rec=None; rec_valida=False
            # La maquina abre el punto pero su saque no es de nadie.
            if pfx==side and not _es_maquina(num):
                P=get(num); P['S']['T']+=1
                if res in P['S']: P['S'][res]+=1
        elif skill=='D' and pfx==side:
            Pd=get(num); Pd['D']['T']+=1
            if res in Pd['D']: Pd['D'][res]+=1
        elif skill=='R' and pfx==side:
            last_rec=res; rec_valida=True
            Pr=get(num); Pr['R']['T']+=1
            if res in Pr['R']: Pr['R'][res]+=1
        elif pfx!=side and skill in ('A','D','E','B'):
            rec_valida=False
                # ══ EL FREE BALL CIERRA LA FASE DE RECEPCION ═══════════════════
        # Un ataque que sale de un free ball es TRANSICION. El side-out es
        # lo que viene de recibir el SAQUE del rival, nada mas.
        #
        # El motor no conocia la letra F, asi que esa linea era invisible y
        # ARRASTRABA la recepcion anterior del mismo punto. Caso real del
        # 08/09:
        #     *20RM=   recepcion MAL      *20FH#   free ball
        #     *04EQ+   armado         *07AQ#   ataque
        # Ese ataque se contaba como "tras recepcion mala" cuando en
        # realidad sale del free ball: es transicion.
        elif skill=='F' and pfx==side:
            last_rec=None; rec_valida=False
        elif skill=='B' and pfx==side:
            Pb=get(num); Pb['B']['T']+=1
            if res in Pb['B']: Pb['B'][res]+=1
        elif skill=='A' and pfx==side:
            tipo=body[3]  # Q=central · H=alta · T=rápida
            if last_rec is not None and rec_valida:
                rec_valida=False
                cat='rp' if last_rec in ('#','+') else 'ri' if last_rec=='!' else 'rm' if last_rec=='-' else 'tr'
            else:
                cat='tr'
            Pa=get(num)
            Pa['Aall']['T']+=1
            if res in Pa['Aall']: Pa['Aall'][res]+=1
            if tipo=='Q':
                Pa['cent']['T']+=1
                if res in Pa['cent']: Pa['cent'][res]+=1
            elif tipo=='T':
                Pa['rap']['T']+=1
                if res in Pa['rap']: Pa['rap'][res]+=1
            elif tipo=='H':
                Pa['alta']['T']+=1
                if res in Pa['alta']: Pa['alta'][res]+=1
            Pa[cat]['T']+=1
            if res in Pa[cat]: Pa[cat][res]+=1
    # equipo = suma de todos
    eq=_bat_nuevo()
    for n in list(pl.keys()):
        P=pl[n]
        for sec in P:
            for k in P[sec]: eq[sec][k]+=P[sec][k]
    pl['__EQUIPO__']=eq
    return pl

def _roundpy(x):
    # redondeo bancario (igual que round() de Python, que objetivos.js imita)
    import decimal
    return int(decimal.Decimal(x).quantize(0, rounding=decimal.ROUND_HALF_EVEN))

def _bat_to_pcts(P):
    def atk(d): return _roundpy((d['#']-d['/']-d['='])/d['T']*100) if d['T'] else None
    S,R,B=P['S'],P['R'],P['B']
    D=P.get('D') or {'#':0,'+':0,'-':0,'=':0,'T':0}
    return {
        # El dashboard ya buscaba defT / defPerf / defErr / def: estaba escrito
        # el lector pero nadie generaba el dato.
        # ══ EL DESGLOSE, PARA QUE EL JUGADOR VEA DE DONDE SALE EL NUMERO ══════
        #  Antes solo se exportaba el porcentaje y el total. El jugador veia
        #  "39%" y no tenia como saber que hizo para llegar ahi.
        #
        #  Ahora va tambien cuantas acciones de cada valoracion, asi la
        #  ventanita puede mostrar la cuenta completa:
        #     12 perfectas x100 + 30 positivas x75 + ... / 80 = 57
        'sqD':  {'p':S['#'], 'f':S.get('/',0), 'o':S['+'], 'n':S.get('!',0),
                 'm':S.get('-',0), 'e':S['=']},
        'recD': {'p':R['#'], 'o':R['+'], 'n':R.get('!',0), 'm':R.get('-',0),
                 's':R.get('/',0), 'e':R['=']},
        'defD': {'p':D['#'], 'o':D['+'], 'n':D.get('!',0), 'm':D.get('-',0),
                 'e':D['=']},
        'bqD':  {'p':B['#'], 'o':B['+'], 'n':B.get('!',0), 'm':B.get('-',0),
                 's':B.get('/',0), 'e':B.get('=',0), 't':B['T']},
        'defT':    D['T'],
        'defPerf': D['#'],
        'defErr':  D['='],
        # Tambien las intermedias: sin ellas la pantalla no puede recalcular la
        # efectividad de un subconjunto de sesiones, y promediar porcentajes de
        # dias distintos da un numero que no significa nada.
        'defBuena': D['+'],
        'defMala':  D['-'],
        # Misma escala 0-100 que el resto: perfecta 100, buena 75, neutra 50,
        # mala 25, error 0. Estaba en la escala vieja y daba -44 mientras la
        # pantalla mostraba 27 para lo mismo.
        'def':     _roundpy((D['#']+0.75*D['+']+0.5*D['!']+0.25*D['-'])/D['T']*100) if D['T'] else None,
        # ══ SAQUE Y RECEPCION: ESCALA SIMETRICA ══════════════════════════════
        # Antes los pesos eran chicos y asimetricos, y sobre todo el saque
        # negativo y el neutro valian LO MISMO (cero). Un saque que el rival
        # recibe perfecto no puede puntuar igual que uno que lo incomoda.
        #
        # Ahora la escala es simetrica alrededor del neutro: lo que suma un
        # positivo es exactamente lo que resta un negativo, y los extremos
        # valen 1. Se mide QUE TAN BIEN SE EJECUTO la accion, no cuanto
        # ayudo despues a ganar el punto: son dos preguntas distintas y esta
        # es la que le sirve al entrenador para corregir.
        #
        #   SAQUE        #  +1     /  +0,75   +  +0,5   !  0   -  -0,5   =  -1
        #   RECEPCION    #  +1     +  +0,5    !   0     -  -0,5   /  -0,75   =  -1
        #
        # El free ball del saque (/) entra entre el positivo y el ace: la
        # pelota vuelve sin ataque y eso es casi tan bueno como un punto.
        # El sobrepase de recepcion (/) entra entre el negativo y el error:
        # la pelota cruza y el rival ataca de una, pero todavia se puede
        # defender.
        #
        # OJO al leer los numeros: en esta escala el saque del equipo da
        # negativo casi siempre, porque el 44% de los saques son negativos y
        # antes valian cero. No es que se saque peor: cambio la vara. Los
        # objetivos de la pantalla hay que reajustarlos a esta escala.
        # ── DE 0 A 100, NO DE -100 A +100 ────────────────────────────────────
        # Mismo criterio de antes, misma jerarquia, mismo orden. Lo unico que
        # cambia es DONDE esta el cero.
        #
        # Con el cero en el medio, cualquier equipo con muchos negativos caia
        # por debajo de cero, y en saque masculino el negativo es el 40-47% de
        # las acciones: los OCHO equipos de la liga daban negativo, campeon
        # incluido. Un numero donde todos son negativos no dice si estas bien
        # o mal.
        #
        # Corriendo la escala con (valor + 1) / 2, cada valoracion queda:
        #
        #   SAQUE       #  100    /  87,5   +  75    !  50    -  25    =  0
        #   RECEPCION   #  100    +  75     !  50    -  25    /  12,5  =  0
        #
        # Y el numero se lee solo: 50 es "todo neutro", 25 "todo negativo",
        # 75 "todo positivo". Es el criterio del Serve Effectiveness Rating,
        # que tampoco usa negativos.
        #
        # Equivalencia exacta con la escala anterior: nuevo = (viejo + 100) / 2
        'sq':    _roundpy((S['#'] + 0.875*S['/'] + 0.75*S['+'] + 0.5*S['!'] + 0.25*S['-'])/S['T']*100) if S['T'] else None,
        'rec':   _roundpy((R['#'] + 0.75*R['+'] + 0.5*R['!'] + 0.25*R['-'] + 0.125*R['/'])/R['T']*100) if R['T'] else None,
        'bqpos': _roundpy((B['#']+B['+'])/B['T']*100) if B['T'] else None,
        'bqpt':  _roundpy(B['#']/B['T']*100) if B['T'] else None,
        'atqq':  atk(P['cent']),
        'atqhb': atk(P['alta']),
        'atqx':  atk(P['rap']),
        'atqrp': atk(P['rp']),
        'atqri': atk(P['ri']),
        'atqrm': atk(P['rm']),
        'atqtr': atk(P['tr']),
        # ══ SOBRE CUANTAS ACCIONES ESTA HECHA CADA CUENTA ═══════════════════
        # Un 40% de 5 acciones y un 20% de 238 no valen lo mismo. Mostrar los
        # dos iguales engana. No se filtra ni se esconde nada —el numero es
        # real y se va a acomodar solo a medida que se carguen entrenamientos—
        # pero al lado va sobre cuanto esta calculado, que es lo que permite
        # leerlo bien.
        'n_sq':    S['T'],
        'n_rec':   R['T'],
        'n_bqpos': B['T'],
        'n_bqpt':  B['T'],
        'n_def':   D['T'],
        # ══ EL DESGLOSE DE CADA ATAQUE ═══════════════════════════════════════
        #  El ataque no se cuenta como los demas fundamentos. No es un
        #  promedio ponderado sino una RESTA:
        #      (puntos - bloqueados - errores) / total
        #  Por eso puede dar negativo, y por eso la ventanita necesita
        #  mostrarlo distinto.
        #
        #  Se exporta: punto, bloqueado, error y total. Lo que queda —los
        #  ataques que siguieron en juego— sale de restar.
        'atqD': {
            'q':  {'p':P['cent']['#'], 'b':P['cent']['/'], 'e':P['cent']['='], 't':P['cent']['T']},
            'hb': {'p':P['alta']['#'], 'b':P['alta']['/'], 'e':P['alta']['='], 't':P['alta']['T']},
            'x':  {'p':P['rap']['#'],  'b':P['rap']['/'],  'e':P['rap']['='],  't':P['rap']['T']},
            'rp': {'p':P['rp']['#'],   'b':P['rp']['/'],   'e':P['rp']['='],   't':P['rp']['T']},
            'ri': {'p':P['ri']['#'],   'b':P['ri']['/'],   'e':P['ri']['='],   't':P['ri']['T']},
            'rm': {'p':P['rm']['#'],   'b':P['rm']['/'],   'e':P['rm']['='],   't':P['rm']['T']},
            'tr': {'p':P['tr']['#'],   'b':P['tr']['/'],   'e':P['tr']['='],   't':P['tr']['T']},
        },
        'n_atqq':  P['cent']['T'],
        'n_atqhb': P['alta']['T'],
        'n_atqx':  P['rap']['T'],
        'n_atqrp': P['rp']['T'],
        'n_atqri': P['ri']['T'],
        'n_atqrm': P['rm']['T'],
        'n_atqtr': P['tr']['T'],
    }

# ══════════ LECTURA DVW ══════════
def parse_dvw(path):
    txt=open(path,encoding='latin-1',errors='ignore').read()
    def sec(a,b):
        m=re.search(r'\['+a+r'\](.*?)(?:\['+b+r'\]|\Z)',txt,re.S); return m.group(1) if m else ''
    teamlines=[l.split(';')[1] for l in sec('3TEAMS','3MORE').strip().splitlines()[:2] if ';' in l]
    if len(teamlines)<2: return None
    home_name=norm_team(teamlines[0]); away_name=norm_team(teamlines[1])
    casla_home=is_casla(teamlines[0]); casla_away=is_casla(teamlines[1])
    if not (casla_home or casla_away): return None  # solo partidos de CASLA
    side='*' if casla_home else 'a'
    rival=away_name if casla_home else home_name

    base=os.path.basename(path)
    # El codigo oficial del partido tiene 5 o 6 digitos. Antes, si no aparecia,
    # se aceptaba cualquier numero de 4 a 6 y terminaba agarrando el ANIO de la
    # fecha: los entrenamientos quedaban todos con el id "2026". Y como abajo se
    # descartan los ids repetidos, el segundo entrenamiento de la temporada
    # desaparecia sin aviso. Ahora, sin codigo, el id se arma con fecha+rival.
    mcode=re.search(r'&?\s*(\d{5,6})\b', base)
    mdate=re.search(r'(\d{4}-\d{2}-\d{2})',base)
    date=mdate.group(1) if mdate else ''
    code=mcode.group(1) if mcode else ''

    # roster CASLA: num -> nombre (para keyear por nombre como el perfil)
    psec = sec('3PLAYERS-H','3PLAYERS-V') if casla_home else sec('3PLAYERS-V','3ATTACKCOMBINATION')
    names={}
    for l in psec.strip().splitlines():
        c=l.split(';')
        if len(c)>10 and c[1].strip().isdigit():
            nn=c[1].strip().zfill(2)
            nom=(c[9].strip()+' '+c[10].strip()).strip() if len(c)>10 else c[9].strip()
            names[nn]=re.sub(r'\s+',' ',nom).strip()

    scout=txt.split('[3SCOUT]')[-1].strip().splitlines()
    # resultado (sets) — simple: contar de la meta si está
    return {'code':code,'rival':rival,'date':date,'side':side,'names':names,'scout':scout,
            'turno':_turno(base),
            # cual de los dos equipos es el nuestro: en un entrenamiento el
            # rival pasa a ser este mismo, sin mirar lo que diga el archivo
            'nuestro': home_name if casla_home else away_name}

def season_from_date(date):
    """Temporada 'YYYY/YY' desde la fecha. Arranca en agosto, igual que en
    gen_plan_partido.py: una practica del 30 de julio cae en la anterior.

    Antes de eso se le pregunta a config_club: si el club tiene torneos
    configurados, la temporada sale de ahi. Es lo que permite que un torneo
    que NO cruza de anio quede bien etiquetado, en vez de forzarle el
    '2026/27' que sirve solo cuando todos cruzan."""
    try:
        _t = _temp_config(date)
        if _t: return _t
        p=date.split('-'); y=int(p[0]); m=int(p[1]); st=y if m>=8 else y-1
        return "%d/%02d"%(st,(st+1)%100)
    except Exception: return None

def _norm_temp(t):
    """Deja la temporada en el formato que usa ESTE club.

    ══ POR QUE NO SIEMPRE ES 'YYYY/YY' ═══════════════════════════════════════
    Antes esto convertia siempre '2026' en '2026/27'. Sirve para las ligas que
    cruzan de anio —agosto a mayo—, pero no para las que empiezan y terminan
    en el mismo:

        HACER_TODO pasa      '2026'
        _norm_temp lo hacia  '2026/27'
        season_from_date da  '2026'
        -> no coincidian y SE DESCARTABAN TODOS LOS PARTIDOS

    El sintoma era mudo: "0 sesiones", datos_baterias.js de 2 KB y las
    baterias dibujadas pero sin datos. Ningun error, nada en rojo.

    Ahora se le pregunta a config_club si el torneo cruza de anio. Si cruza,
    se convierte como antes; si no, se deja tal cual.
    """
    if not t: return None
    t=str(t).strip()
    if not re.fullmatch(r'\d{4}', t):
        return t

    cruza = None
    try:
        import config_club as _cc
        _tor = _cc.torneos() or {}
        for _cfg in _tor.values():
            if isinstance(_cfg, dict) and 'cruza' in _cfg:
                cruza = bool(_cfg.get('cruza')); break
    except Exception:
        pass

    # Sin config_club que opine, se mantiene lo de antes.
    if cruza is None: cruza = True
    if not cruza: return t
    y=int(t); return "%d/%02d"%(y,(y+1)%100)

def _temp_de_carpeta(folder):
    """El ano que lleva el nombre de la carpeta -> temporada que arranca ese ano."""
    m=re.search(r'(20\d{2})', os.path.basename(os.path.normpath(folder)))
    if not m: return None
    y=int(m.group(1)); return "%d/%02d"%(y,(y+1)%100)

def _slug(t):
    t=unicodedata.normalize('NFKD', t or '').encode('ascii','ignore').decode()
    return re.sub(r'[^A-Za-z0-9]+','', t).upper()[:12] or 'SIN'


def _turno(nombre_archivo):
    """Doble turno: manana y tarde el mismo dia.

    El DVW NO trae la hora (el campo de [3MATCH] viene vacio), asi que el
    turno se saca del nombre del archivo. Se aceptan las formas que se usan
    en la practica, en castellano, ingles y aleman.

    Sin marca devuelve '' y la sesion se trata como unica del dia. Si hay dos
    sin marca, el _mk_id les pone -2 y no se pisan igual.
    """
    # Sufijo corto al final del nombre: "...-M.dvw" o "...-T.dvw". Es lo que
    # pone el panel al exportar. Se mira SOLO al final, para no confundirlo
    # con una M o una T que aparezca en el nombre del equipo.
    import os as _os
    _base = _os.path.splitext(_os.path.basename(nombre_archivo or ''))[0].upper()
    if _base.endswith('-M'): return 'M'
    if _base.endswith('-T'): return 'T'
    n = (nombre_archivo or '').upper()
    # Palabras largas: alcanza con que aparezcan.
    for pal, t in [('MORNING','M'), ('MANANA','M'), ('MAÑANA','M'), ('MORGEN','M'),
                   ('VORMITTAG','M'), ('TURNO1','M'),
                   ('AFTERNOON','T'), ('TARDE','T'), ('NACHMITTAG','T'), ('ABEND','T'),
                   ('EVENING','T'), ('NOCHE','T'), ('TURNO2','T')]:
        if pal in n: return t
    # Siglas cortas: tienen que ser palabra suelta. Sin esto, "AMRISWIL"
    # se leia como "AM" y el partido contra Amriswil quedaba marcado
    # como entrenamiento de manana.
    for pal, t in [('AM','M'), ('T1','M'), ('PM','T'), ('T2','T')]:
        if re.search(r'(?<![A-Z0-9])' + pal + r'(?![A-Z0-9])', n): return t
    return ''


def _plantel_club():
    """Los numeros del plantel del club, de plantel_<club>.js."""
    global _PC
    try:
        return _PC
    except NameError:
        pass
    import glob as _g, re as _r, os as _o
    out = {}
    for f in _g.glob(_o.path.join(_o.path.dirname(_o.path.abspath(__file__)), 'plantel_*.js')):
        try: t = open(f, encoding='utf-8', errors='replace').read()
        except Exception: continue
        for m in _r.finditer(r'\{\s*num:\s*(\d+)[^}]*?ap:\s*"([^"]*)"', t):
            out[int(m.group(1))] = m.group(2).strip()
    _PC = out
    return out


def _es_nuestro_equipo(nombre):
    """Si este nombre de equipo es el club del sistema."""
    if not nombre:
        return False
    import unicodedata as _u, re as _r
    def _p(x):
        x = _u.normalize('NFKD', x or '').encode('ascii', 'ignore').decode()
        return _r.sub(r'[^a-z0-9]', '', x.lower())
    clave = ''
    try:
        if 'NUESTRO' in globals() and NUESTRO and NUESTRO[0]:
            clave = _p(NUESTRO[0])
    except Exception:
        pass
    if not clave:
        # el nombre del plantel: plantel_nafels.js -> nafels
        import glob as _g, os as _o
        for f in _g.glob(_o.path.join(_o.path.dirname(_o.path.abspath(__file__)), 'plantel_*.js')):
            clave = _p(_o.path.basename(f)[8:-3])
            if clave: break
    # ══ TAMBIEN POR EL NOMBRE LARGO ══════════════════════════════════════════
    #  En los .dvw el club figura con su nombre completo:
    #      "Club Gimnasia y Esgrima de La Plata"
    #  y el sistema lo buscaba solo por la sigla del plantel ("gelp"). No
    #  coincidian, asi que NINGUN partido se reconocia como propio: el
    #  generador decia "Equipos: 0" y datos_baterias.js salia vacio.
    #
    #  Ahora tambien se prueba con el nombre completo de config_club.
    try:
        import config_club as _cc
        _largo = _p(_cc.nombre_completo() or '')
        _propio = _p(_cc.equipo_propio() or '')
        _n = _p(nombre)
        if _largo and (_largo in _n or _n in _largo):
            return True
        if _propio and (_propio in _n or _n in _propio):
            return True
    except Exception:
        pass

    if not clave:
        try:
            import config_club as _cc
            clave = _p(_cc.club())
        except Exception:
            pass
    if not clave:
        return False
    n = _p(nombre)
    return clave in n or n in clave


def _mk_id(code, tipo, date, rival, usados, turno=''):
    """Un id estable y unico por sesion. Con codigo oficial se usa ese; si no
    —el caso de los entrenamientos— se arma con el tipo, la fecha y el rival."""
    base = code if code else ('%s%s-%s%s' % ('E' if tipo=='entrenamiento' else 'P',
                                             date or 'sinfecha', _slug(rival),
                                             ('-'+turno) if turno else ''))
    i, k = base, 2
    while i in usados:
        i = '%s-%d' % (base, k); k += 1
    usados.add(i)
    return i


def elegir_mejor_copia(archivos, parse):
    """Cuando el mismo entrenamiento aparece dos veces, se queda el mas completo.

    POR QUE HACE FALTA
    El panel arma el nombre del .dvw con la fecha, los equipos y el turno:

        &2026-09-15 AXP-ENTRENAMIENTO-T.dvw

    Ese nombre es SIEMPRE EL MISMO para una sesion. Si se exporta dos veces
    —a mitad del entrenamiento y otra vez al final, que es lo razonable—
    Windows no pisa el primero: guarda el segundo como

        &2026-09-15 AXP-ENTRENAMIENTO-T (1).dvw

    Y si los dos van a la carpeta, el sistema ve DOS entrenamientos donde hay
    uno solo. Peor: el que exportaste a mitad tiene MENOS acciones, y si se
    procesara ese se estarian perdiendo datos sin que nadie lo note.

    Aca se agrupan por (fecha, turno, rival) y se elige el que MAS acciones
    tiene, que es siempre el mas completo. Los otros se descartan y se avisa
    por pantalla, con nombre y cantidad, para que se vea que paso.
    """
    import collections, os
    grupos = collections.OrderedDict()
    for f in archivos:
        r = parse(f)
        if not r: continue
        clave = (r.get('date',''), r.get('turno',''), _slug(r.get('rival','')))
        grupos.setdefault(clave, []).append((f, r, len(r.get('scout') or [])))

    elegidos = []
    for clave, lista in grupos.items():
        if len(lista) == 1:
            elegidos.append(lista[0][:2]); continue
        lista.sort(key=lambda x: -x[2])          # el de mas acciones primero
        mejor = lista[0]
        print('[baterias] MISMA SESION EN %d ARCHIVOS (%s turno %s):'
              % (len(lista), clave[0], clave[1] or '-'))
        for f, r, n in lista:
            marca = '  <-- ME QUEDO CON ESTE' if f == mejor[0] else '      descartado'
            print('           %-52s %4d acciones%s' % (os.path.basename(f)[:52], n, marca))
        elegidos.append(mejor[:2])
    return elegidos


# ══════════════════════════════════════════════════════════════════════════
#  EL MISMO JUGADOR, ESCRITO DISTINTO EN CADA ARCHIVO
#  ------------------------------------------------------------------------
#  Los jugadores se identificaban por el NOMBRE que trae cada .dvw. Pero el
#  nombre lo escribe el scout a mano, y no siempre igual. En los archivos de
#  Näfels aparecen estas tres:
#
#      #2   BRUDERER  /  GIAN        (apellido en uno, nombre en el otro)
#      #7   SCHMID    /  SCHIMD      (una letra cambiada)
#      #20  SCHMID    /  SCHIMD
#
#  Resultado: el mismo jugador quedaba partido en DOS fichas con la mitad de
#  las acciones cada una, y en el listado del dashboard directamente no
#  aparecia —el #2 Bruderer faltaba—.
#
#  El numero de camiseta SI es confiable: es el que se tipea en cada codigo y
#  el que usa DataVolley. Asi que el jugador se identifica por numero, y el
#  nombre se toma del archivo mas reciente que lo tenga.
# ══════════════════════════════════════════════════════════════════════════
def _unificar_por_numero(matches):
    """Un nombre por numero de camiseta, para todos los archivos."""
    #  CUAL DE LAS VERSIONES GANA
    #  Antes ganaba la mas larga, y con "SCHMID ROY" / "SCHIMD ROY" —que miden
    #  igual— quedaba la primera que apareciera: podia quedar el error de
    #  tipeo como nombre oficial del jugador.
    #
    #  Ahora gana la que MAS VECES aparece en los archivos: si el scout la
    #  escribio bien cuatro veces y mal una, queda la buena. Si empatan, se
    #  prefiere la que esta toda en mayusculas —el formato del resto del
    #  plantel— y recien despues la mas larga.
    import collections as _c
    cuenta = _c.defaultdict(_c.Counter)
    for m in matches:
        for num, nom in (m.get('names') or {}).items():
            if not nom: continue
            n = str(num).lstrip('0') or str(num)
            cuenta[n][nom] += 1

    canon = {}
    for n, opciones in cuenta.items():
        canon[n] = sorted(
            opciones.items(),
            key=lambda x: (-x[1], 0 if x[0].isupper() else 1, -len(x[0]), x[0])
        )[0][0]
    for m in matches:
        nombres = m.get('names') or {}
        nuevo = {}
        for num, P in (m.get('jug') or {}).items():
            pass
        # reescribir jug con el nombre canonico
        rev = {}
        for num, nom in nombres.items():
            n = str(num).lstrip('0') or str(num)
            rev[nom] = canon.get(n, nom)
        jug2 = {}
        for nom, P in (m.get('jug') or {}).items():
            jug2[rev.get(nom, nom)] = P
        m['jug'] = jug2
        m['names'] = {k: canon.get(str(k).lstrip('0') or str(k), v) for k, v in nombres.items()}
    return canon

def build(fuentes, out='datos_baterias.js', filtro_temp=None):
    """fuentes: lista de (carpeta, tipo) con tipo 'partido' o 'entrenamiento'.

    Salida COMPATIBLE HACIA ATRAS: total, meta, jug, ind y eq siguen siendo el
    acumulado de TODO, que es el criterio de "Todos". Se agregan:
        · meta[i].tipo e ind[i].tipo  -> de que carpeta salio cada sesion
        · porTipo.<tipo>.{total,jug,eq} -> el acumulado de cada tipo por separado
    Una pagina que todavia no sepa de tipos sigue leyendo lo de siempre."""
    filtro_temp = _norm_temp(filtro_temp)
    matches=[]; usados=set()
    for folder, tipo in fuentes:
        if not folder or not os.path.isdir(folder):
            print('[baterias] aviso: no existe la carpeta "%s", la salteo' % folder); continue
        # La temporada de un ENTRENAMIENTO sale de la CARPETA, no de la fecha.
        # Es lo que hace update_db_entrenamientos_nafels.py, que le estampa a
        # cada practica la temporada que recibe por linea de comandos. Y tiene
        # sentido: la pretemporada de julio pertenece al ano que arranca, aunque
        # por fecha caiga en la temporada anterior. Los PARTIDOS, en cambio, van
        # por fecha, como en gen_plan_partido.py.
        temp_carpeta = _temp_de_carpeta(folder) if tipo=='entrenamiento' else None
        if filtro_temp and temp_carpeta and temp_carpeta != filtro_temp:
            print('[baterias] "%s" es de la %s, no de la %s: la salteo' % (folder, temp_carpeta, filtro_temp))
            continue
        _todos = sorted(glob.glob(os.path.join(folder,'*.dvw')))
        for f, r in elegir_mejor_copia(_todos, parse_dvw):
            if filtro_temp and not temp_carpeta and season_from_date(r['date']) != filtro_temp: continue
            # ══ EN UN ENTRENAMIENTO NO HAY RIVAL ═══════════════════════════
            # El scout escribe cualquier cosa en el casillero del visitante
            # —PRUEBA, CAMPANA, lo que sea— y eso terminaba inventando equipos
            # en el sistema. En una practica los dos lados son el club, punto.
            # Asi lo escribe DataVolley y asi se toma aca, sin depender de lo
            # que diga el archivo.
            if tipo == 'entrenamiento':
                r['rival'] = r.get('nuestro') or r['rival']
            sid=_mk_id(r['code'], tipo, r['date'], r['rival'], usados, r.get('turno',''))
            pl=_calc_baterias(r['scout'], r['side'])
            jug={}
            for num,P in pl.items():
                if num=='__EQUIPO__': continue
                # ══ SOLO LOS DEL PLANTEL ══════════════════════════════════
                #  En los entrenamientos aparecen numeros que no son
                #  jugadores del equipo:
                #     #8  la MAQUINA DE SAQUE, que se scoutea con un numero
                #         para poder hacer el ejercicio
                #     #6  un invitado que entreno un dia suelto
                #
                #  Ya los habiamos sacado del plan de partido, pero el
                #  dashboard lee de ESTE motor y seguian apareciendo. Sus
                #  acciones quedan en la base —existieron— pero no ensucian
                #  las baterias del equipo.
                #
                #  El filtro usa plantel_<club>.js, la fuente unica. Si
                #  manana el invitado se suma, se lo agrega ahi y aparece
                #  solo. De los RIVALES no se filtra: no tenemos su plantel.
                if _es_nuestro_equipo(r.get('nuestro') or r.get('rival')):
                    if _plantel_club() and int(num) not in _plantel_club():
                        continue
                nom=r['names'].get(num)
                if not nom: continue
                jug[nom]=_bat_to_pcts(P)
            eq=_bat_to_pcts(pl['__EQUIPO__']) if '__EQUIPO__' in pl else {}
            matches.append({'id':sid,'tipo':tipo,'rival':r['rival'],'fecha':r['date'],'turno':r.get('turno',''),
                            'jug':jug,'eq':eq,'_acum':pl,'names':r['names']})

    # un solo nombre por numero de camiseta, antes de acumular nada
    _canon = _unificar_por_numero(matches)
    for _n, _nom in sorted(_canon.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 99):
        pass
    matches.sort(key=lambda m:(m['fecha'], m['id']))

    def acumular(lista):
        """Suma los contadores crudos y recien al final saca los porcentajes.
        Promediar porcentajes daria mal: un partido de 3 saques pesaria igual
        que uno de 40."""
        acc={}
        for m in lista:
            for num,P in m['_acum'].items():
                if num=='__EQUIPO__': continue
                nom=m['names'].get(num)
                if not nom: continue
                if nom not in acc: acc[nom]=_bat_nuevo()
                for sec2 in P:
                    for k in P[sec2]: acc[nom][sec2][k]+=P[sec2][k]
        jug_a={nom:_bat_to_pcts(acc[nom]) for nom in acc}
        # ── EL TOTAL DEL EQUIPO INCLUYE A TODOS ──────────────────────────────
        # Antes el acumulado se armaba sumando solo a los jugadores con nombre
        # reconocido, porque arriba se saltean los que no lo tienen ("if not
        # nom: continue"). Pero el total POR SESION si los cuenta, asi que el
        # numero del acumulado no coincidia con el de las sesiones: 37 contra
        # 39 con las mismas cuatro practicas.
        #
        # Cada sesion ya trae su __EQUIPO__, que es la suma de TODOS los
        # jugadores. Sumando esos, el acumulado y las sesiones dicen lo mismo.
        # Los promedios por jugador siguen igual: ahi si hace falta el nombre.
        eq_acc=_bat_nuevo()
        for m in lista:
            E=m['_acum'].get('__EQUIPO__')
            if not E: continue
            for sec2 in E:
                for k in E[sec2]: eq_acc[sec2][k]+=E[sec2][k]
        return jug_a, _bat_to_pcts(eq_acc)

    jug_acum, eq_acum = acumular(matches)
    porTipo={}
    for tipo in ('partido','entrenamiento'):
        sub=[m for m in matches if m['tipo']==tipo]
        j_t, e_t = acumular(sub)
        porTipo[tipo]={'total':len(sub),'jug':j_t,'eq':e_t,
                       'ids':[m['id'] for m in sub]}

    meta=[{'id':m['id'],'tipo':m['tipo'],'rival':m['rival'],'nombre':m['rival'],'fecha':m['fecha'],
           'turno':m.get('turno','')} for m in matches]
    ind=[{'id':m['id'],'tipo':m['tipo'],'jug':m['jug'],'eq':m['eq']} for m in matches]
    OUT={'total':len(matches),'meta':meta,'jug':jug_acum,'ind':ind,'eq':eq_acum,
         'porTipo':porTipo,'temporada':filtro_temp or ''}
    open(out,'w',encoding='utf-8').write('window.BAT_PARTIDOS='+json.dumps(OUT,ensure_ascii=False,separators=(',',':'))+';')
    print('[baterias] %d sesiones -> %s   (partidos: %d · entrenamientos: %d)' % (
        len(matches), out, porTipo['partido']['total'], porTipo['entrenamiento']['total']))
    for m in matches:
        print('   %-11s %-14s %-9s (%d jugadores)' % (m['fecha'], m['rival'], m['tipo'], len(m['jug'])))

def autodetect_dvw():
    dirs=[d for d in glob.glob('DVW*') if os.path.isdir(d) and glob.glob(os.path.join(d,'*.dvw'))]
    return max(dirs,key=lambda d:len(glob.glob(os.path.join(d,'*.dvw')))) if dirs else None

def _autodetect(patron):
    d=[x for x in glob.glob(patron) if os.path.isdir(x) and glob.glob(os.path.join(x,'*.dvw'))]
    return max(d,key=lambda x:len(glob.glob(os.path.join(x,'*.dvw')))) if d else None

if __name__=='__main__':
    args=sys.argv[1:]
    partidos=[]; entrenamientos=[]; out=None; temp=None

    if any(a.startswith('--') for a in args):
        # ── forma nueva: las dos carpetas en una sola corrida ──
        i=0
        while i < len(args):
            a=args[i]
            if   a=='--partidos'        and i+1<len(args): partidos.append(args[i+1]); i+=2
            elif a=='--entrenamientos'  and i+1<len(args): entrenamientos.append(args[i+1]); i+=2
            elif a in ('--out','-o')    and i+1<len(args): out=args[i+1]; i+=2
            elif a=='--temporada'       and i+1<len(args): temp=args[i+1] or None; i+=2
            else:
                print('[baterias] ERROR: no entiendo el argumento "%s"' % a); sys.exit(1)
        if not partidos and not entrenamientos:
            partidos      = [x for x in [_autodetect('DVW *')] if x and 'ENTREN' not in x.upper()]
            entrenamientos= [x for x in [_autodetect('DVW *ENTREN*')] if x]
    else:
        # ── forma vieja: gen_baterias.py CARPETA [SALIDA] ──
        #    Se mantiene para los .bat que llaman a una carpeta sola (la capsula).
        #    El tipo se deduce del nombre: si dice ENTRENAMIENTOS, es practica.
        folder = args[0] if len(args)>0 else (autodetect_dvw() or '')
        out    = args[1] if len(args)>1 else None
        if not folder or not os.path.isdir(folder):
            print('[baterias] ERROR: no encontre la carpeta de DVW.'); sys.exit(1)
        if 'ENTREN' in os.path.basename(folder).upper(): entrenamientos=[folder]
        else:                                            partidos=[folder]

    fuentes=[(f,'partido') for f in partidos]+[(f,'entrenamiento') for f in entrenamientos]
    fuentes=[(f,t) for f,t in fuentes if f]
    if not fuentes:
        print('[baterias] ERROR: no hay ninguna carpeta de DVW para procesar.'); sys.exit(1)

    # El club sale del nombre de la carpeta: "DVW NAFELS 2026" -> "nafels".
    # Es lo mismo que hace el resto de los motores. Se deduce UNA vez, con la
    # primera carpeta que exista: las dos son del mismo club, y la palabra
    # ENTRENAMIENTOS se descarta para que las dos den el mismo nombre.
    import unicodedata as _u
    _ref = next((f for f,t in fuentes if os.path.isdir(f)), None)
    if not _ref:
        print('[baterias] ERROR: ninguna de las carpetas indicadas existe.'); sys.exit(1)
    _b = os.path.basename(os.path.normpath(_ref))
    _b = _u.normalize('NFKD', _b).encode('ascii', 'ignore').decode()
    _pal = [w for w in re.split(r'[^A-Za-z]+', _b)
            if w and w.upper() not in ('DVW', 'ENTRENAMIENTOS', 'SEASON')]
    NUESTRO[0] = (_pal[0].lower() if _pal else '')
    print('[baterias] Club: %s' % (NUESTRO[0] or '(no lo pude deducir)'))

    # La tabla de equipos se arma con TODAS las carpetas: los rivales de los
    # partidos y los de las practicas no son los mismos.
    for f,t in fuentes:
        if os.path.isdir(f):
            print('[baterias] %-14s %s' % (t, f))
            _cargar_equipos(f)
    print('[baterias] Equipos: %d' % len(TEAM_NORM))

    build(fuentes, out or 'datos_baterias.js', temp)
    print('\nLISTO. Ahora publica datos_baterias.js con PUBLICAR_EN_GITHUB.bat')
