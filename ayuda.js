/* ═══════════════════════════════════════════════════════════════════════════
   ayuda.js — EL SIGNO DE PREGUNTA DE CADA PANTALLA

   Un boton "?" arriba a la derecha. Se toca y se abre una ventanita que
   explica, en dos minutos de lectura, que hace esa pantalla y como se usa.

   ── POR QUE ──────────────────────────────────────────────────────────────
   La app tiene 54 pantallas. Un entrenador que la abre por primera vez no
   tiene por que adivinar que hace cada una. Sin esto, la mitad de lo que
   hicimos no se usa nunca.

   ── COMO SE AGREGA A UNA PANTALLA ────────────────────────────────────────
   Una sola linea, al final del <body>:

       <script src="ayuda.js"></script>

   El resto es automatico: se fija en que pantalla esta, busca su texto y
   dibuja el boton. Si una pantalla todavia no tiene texto escrito, el boton
   no aparece —mejor nada que un cartel vacio—.

   ── LOS TRES IDIOMAS ─────────────────────────────────────────────────────
   Cada texto se escribe en es / en / de. Se usa el idioma que el usuario
   eligio con los botones ES EN DE, y cambia solo cuando lo cambia.

   ── COMO ESCRIBIR UNA AYUDA NUEVA ────────────────────────────────────────
   Se agrega al diccionario de abajo, con el nombre del archivo sin .html:

       'mi_pantalla': {
         es: { titulo:'...', que:'...', pasos:['...','...'], ojo:'...' },
         en: { ... }, de: { ... }
       }

   que    — una frase: para que sirve la pantalla
   pasos  — la lista de lo que hay que hacer, en orden
   ojo    — opcional: la advertencia que evita el error mas comun
   ═══════════════════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  /* ── Los textos ───────────────────────────────────────────────────────── */
  var AYUDA = {


    'dashboard': {
      es: {
        titulo: 'Dashboard',
        que: 'La puerta de entrada: desde acá se llega a todo el sistema.',
        pasos: [
          'Elegí el jugador y el fundamento que querés mirar.',
          'Tocá "Heat Maps" para ver los mapas de calor de cada fundamento.',
          'Cada tarjeta lleva a una pantalla distinta del sistema.'
        ]
      },
      en: {
        titulo: 'Dashboard',
        que: 'The way in: everything in the system is reachable from here.',
        pasos: [
          'Pick the player and the skill you want to look at.',
          'Tap "Heat Maps" to see the heat maps for each skill.',
          'Each card leads to a different screen of the system.'
        ]
      },
      de: {
        titulo: 'Dashboard',
        que: 'Der Einstieg: von hier aus ist alles im System erreichbar.',
        pasos: [
          'Wähle den Spieler und das Element, das du ansehen willst.',
          'Tippe auf "Heat Maps", um die Heatmaps jedes Elements zu sehen.',
          'Jede Kachel führt zu einem anderen Bildschirm des Systems.'
        ]
      }
    },

    'jugador': {
      es: {
        titulo: 'Perfil del Jugador',
        que: 'Todo lo de un jugador: sus números, su evolución y sus videos.',
        pasos: [
          'Arriba, el resumen de la temporada en cada fundamento.',
          'Abajo, sus once baterías comparadas con las del equipo.',
          'Verde llegó al objetivo, ámbar está cerca, rojo está lejos.',
          'Con "Stats" y "Rutina" pasás a su detalle y a su plan de trabajo.'
        ],
        ojo: 'Si el jugador entra con su cuenta, ve solo esta pantalla y lo suyo.'
      },
      en: {
        titulo: 'Player Profile',
        que: 'Everything about one player: their numbers, their progress and their videos.',
        pasos: [
          'At the top, the season summary for each skill.',
          'Below, their eleven target bars compared with the team\u2019s.',
          'Green reached the target, amber is close, red is far off.',
          'Use "Stats" and "Routine" for their detail and their work plan.'
        ],
        ojo: 'If the player logs in with their own account, they only see this screen and their own data.'
      },
      de: {
        titulo: 'Spielerprofil',
        que: 'Alles zu einem Spieler: seine Zahlen, seine Entwicklung und seine Videos.',
        pasos: [
          'Oben die Saisonübersicht für jedes Element.',
          'Darunter seine elf Zielbalken im Vergleich zum Team.',
          'Grün Ziel erreicht, Bernstein nah dran, Rot weit entfernt.',
          'Mit "Stats" und "Routine" geht es zu Details und Trainingsplan.'
        ],
        ojo: 'Meldet sich der Spieler selbst an, sieht er nur diesen Bildschirm und seine eigenen Daten.'
      }
    },

    'subir_partido': {
      es: {
        titulo: 'Subir un Partido',
        que: 'El archivo que scouteaste se procesa y actualiza toda la app.',
        pasos: [
          'Arrastrá el archivo .dvw del partido.',
          'Si el club tiene varias categorías, elegí a cuál pertenece.',
          'Pegá el link del video si lo tenés.',
          'Esperá a que termine: en minutos está todo actualizado.'
        ],
        ojo: 'Si la cámara cortó el partido en varios archivos, unilos antes con Unir Videos.'
      },
      en: {
        titulo: 'Upload a Match',
        que: 'The file you scouted gets processed and updates the whole app.',
        pasos: [
          'Drag in the match .dvw file.',
          'If the club has several categories, pick which one it belongs to.',
          'Paste the video link if you have one.',
          'Wait for it to finish: everything is updated within minutes.'
        ],
        ojo: 'If the camera split the match into several files, merge them first with Merge Videos.'
      },
      de: {
        titulo: 'Spiel hochladen',
        que: 'Die gescoutete Datei wird verarbeitet und aktualisiert die ganze App.',
        pasos: [
          'Ziehe die .dvw-Datei des Spiels hierher.',
          'Hat der Verein mehrere Kategorien, wähle die passende.',
          'Füge den Videolink ein, falls vorhanden.',
          'Warte bis es fertig ist: in Minuten ist alles aktualisiert.'
        ],
        ojo: 'Hat die Kamera das Spiel in mehrere Dateien geteilt, füge sie vorher mit Videos zusammenfügen zusammen.'
      }
    },

    'asociar_codigos': {
      es: {
        titulo: 'Asociar Códigos',
        que: 'Traduce el scouting de otra persona a tus propios códigos.',
        pasos: [
          'Arrastrá el archivo que te llegó.',
          'A la izquierda ves sus códigos, a la derecha los tuyos.',
          'Los idénticos se asocian solos; el resto los elegís vos.',
          'Guardá la asociación: la próxima vez que llegue un archivo de esa persona, la cargás y se aplica sola.'
        ],
        ojo: 'Sirve en las dos direcciones: también para traducir tus partidos antes de mandarlos afuera.'
      },
      en: {
        titulo: 'Match Codes',
        que: 'Translates someone else\u2019s scouting into your own codes.',
        pasos: [
          'Drag in the file you received.',
          'On the left you see their codes, on the right yours.',
          'Identical ones are matched automatically; you pick the rest.',
          'Save the mapping: next time a file arrives from that person, load it and it applies itself.'
        ],
        ojo: 'It works both ways: also to translate your matches before sending them out.'
      },
      de: {
        titulo: 'Codes zuordnen',
        que: 'Übersetzt das Scouting einer anderen Person in deine eigenen Codes.',
        pasos: [
          'Ziehe die erhaltene Datei hierher.',
          'Links siehst du ihre Codes, rechts deine.',
          'Identische werden automatisch zugeordnet; den Rest wählst du.',
          'Speichere die Zuordnung: beim nächsten Mal lädst du sie und sie wird automatisch angewendet.'
        ],
        ojo: 'Funktioniert in beide Richtungen: auch um deine Spiele vor dem Versand zu übersetzen.'
      }
    },

    'unir_video': {
      es: {
        titulo: 'Unir Videos',
        que: '¿La cámara cortó el partido en varios archivos? Acá se unen en uno.',
        pasos: [
          'Descargá el programa la primera vez. Después queda en tu computadora.',
          'Ponelo en la carpeta donde están las partes del partido.',
          'Doble click y esperá.',
          'Sale un solo archivo, listo para subir a YouTube o donde uses.'
        ],
        ojo: 'Si las partes son de la misma cámara se pegan sin recomprimir: tarda segundos y no pierde calidad.'
      },
      en: {
        titulo: 'Merge Videos',
        que: 'Did the camera split the match into several files? Here they become one.',
        pasos: [
          'Download the program the first time. After that it stays on your computer.',
          'Put it in the folder where the match parts are.',
          'Double-click and wait.',
          'You get a single file, ready to upload to YouTube or wherever you use.'
        ],
        ojo: 'If the parts come from the same camera they are joined without re-encoding: it takes seconds and loses no quality.'
      },
      de: {
        titulo: 'Videos zusammenfügen',
        que: 'Hat die Kamera das Spiel in mehrere Dateien geteilt? Hier werden sie zu einer.',
        pasos: [
          'Lade das Programm beim ersten Mal herunter. Danach bleibt es auf deinem Rechner.',
          'Lege es in den Ordner mit den Spielteilen.',
          'Doppelklick und warten.',
          'Es entsteht eine einzige Datei, bereit für YouTube oder wo auch immer.'
        ],
        ojo: 'Stammen die Teile von derselben Kamera, werden sie ohne Neukodierung verbunden: Sekunden, ohne Qualitätsverlust.'
      }
    },

    'wellness': {
      es: {
        titulo: 'Wellness',
        que: 'Cómo llega cada jugador al entrenamiento: sueño, ánimo y cansancio.',
        pasos: [
          'Cada jugador lo carga desde su celular, en treinta segundos.',
          'El cuerpo técnico ve la carga real del plantel, día a día.',
          'Sirve para ajustar el entrenamiento antes de que aparezca la lesión.'
        ],
        ojo: 'Conviene cargarlo ANTES de entrenar, no después: es para decidir la sesión, no para evaluarla.'
      },
      en: {
        titulo: 'Wellness',
        que: 'How each player arrives at training: sleep, mood and fatigue.',
        pasos: [
          'Each player fills it in from their phone, in thirty seconds.',
          'The staff sees the squad\u2019s real load, day by day.',
          'It helps adjust training before an injury shows up.'
        ],
        ojo: 'Fill it in BEFORE training, not after: it is meant to shape the session, not to review it.'
      },
      de: {
        titulo: 'Wellness',
        que: 'Wie jeder Spieler ins Training kommt: Schlaf, Stimmung und Müdigkeit.',
        pasos: [
          'Jeder Spieler füllt es in dreissig Sekunden am Handy aus.',
          'Das Trainerteam sieht die tatsächliche Belastung des Kaders, Tag für Tag.',
          'So lässt sich das Training anpassen, bevor eine Verletzung auftritt.'
        ],
        ojo: 'VOR dem Training ausfüllen, nicht danach: es soll die Einheit steuern, nicht bewerten.'
      }
    },

    'rotaciones': {
      es: {
        titulo: 'Rotaciones',
        que: 'Dónde se gana y dónde se pierde el partido, rotación por rotación.',
        pasos: [
          'Mirá el side-out de las seis rotaciones propias.',
          'Compará con el break point: ahí está la diferencia.',
          'Las rotaciones más bajas son las que hay que trabajar o esconder.'
        ],
        ojo: 'Una rotación con poco volumen puede mostrar un porcentaje engañoso. Fijate cuántas pelotas tiene.'
      },
      en: {
        titulo: 'Rotations',
        que: 'Where the match is won and lost, rotation by rotation.',
        pasos: [
          'Look at the side-out for your six rotations.',
          'Compare it with break point: that is where the difference is.',
          'The weakest rotations are the ones to work on or to hide.'
        ],
        ojo: 'A rotation with few rallies can show a misleading percentage. Check how many balls it has.'
      },
      de: {
        titulo: 'Rotationen',
        que: 'Wo das Spiel gewonnen und verloren wird, Rotation für Rotation.',
        pasos: [
          'Sieh dir den Side-out deiner sechs Rotationen an.',
          'Vergleiche mit dem Break Point: dort liegt der Unterschied.',
          'Die schwächsten Rotationen sind die, an denen zu arbeiten ist.'
        ],
        ojo: 'Eine Rotation mit wenigen Ballwechseln kann einen irreführenden Prozentsatz zeigen. Prüfe die Anzahl.'
      }
    },

    'plan_partido': {
      es: {
        titulo: 'Plan de Partido',
        que: 'Todo lo que necesitás saber del próximo rival, armado solo con los partidos que ya scouteaste.',
        pasos: [
          'Elegí el equipo rival arriba a la izquierda.',
          'Filtrá por partido si querés ver solo algunos, o dejá "todos" para la temporada entera.',
          'Cambiá de pestaña según lo que busques: direcciones de ataque, distribución del armador, zonas de recepción, saque, defensa o bloqueo.',
          'Cada jugador tiene sus filtros propios: por combinación, fase, tipo de recepción y resultado.',
          'Doble click en cualquier zona y se abre el video de esas jugadas.'
        ],
        ojo: 'Los números son golpes, no puntos. El porcentaje de al lado es la eficacia.'
      },
      en: {
        titulo: 'Match Plan',
        que: 'Everything you need to know about the next opponent, built automatically from the matches you already scouted.',
        pasos: [
          'Pick the opposing team at the top left.',
          'Filter by match to see only some, or leave "all" for the whole season.',
          'Switch tabs depending on what you need: attack directions, setter distribution, reception zones, serve, defence or block.',
          'Each player has their own filters: by combination, phase, reception type and outcome.',
          'Double-click any zone to open the video of those rallies.'
        ],
        ojo: 'The numbers are attempts, not points. The percentage next to them is efficiency.'
      },
      de: {
        titulo: 'Spielplan',
        que: 'Alles über den nächsten Gegner, automatisch aus den bereits gescouteten Spielen erstellt.',
        pasos: [
          'Wähle oben links die gegnerische Mannschaft.',
          'Filtere nach Spiel, um nur einzelne zu sehen, oder lasse "alle" für die ganze Saison.',
          'Wechsle die Registerkarte je nach Bedarf: Angriffsrichtungen, Zuspielverteilung, Annahmezonen, Aufschlag, Abwehr oder Block.',
          'Jeder Spieler hat eigene Filter: nach Kombination, Phase, Annahmeart und Ergebnis.',
          'Doppelklick auf eine Zone öffnet das Video dieser Ballwechsel.'
        ],
        ojo: 'Die Zahlen sind Schläge, keine Punkte. Der Prozentsatz daneben ist die Effizienz.'
      }
    },

    'alta_jugadores': {
      es: {
        titulo: 'Alta de Jugadores',
        que: 'Les da acceso a la app: cada jugador entra con su cuenta y ve solo lo suyo.',
        pasos: [
          'Si el club tiene varias categorías, elegí arriba a cuál van estos jugadores.',
          'Completá cada fila: número de camiseta, mail y fecha de nacimiento.',
          'Tocá el círculo del final para agregar la foto. Es opcional.',
          'Agregá tantas filas como jugadores tengas.',
          'Tocá "Revisar y continuar" y después "Crear las cuentas".'
        ],
        ojo: 'La contraseña de cada jugador es su fecha de nacimiento, en formato ddmmaaaa. La puede cambiar después.'
      },
      en: {
        titulo: 'Add Players',
        que: 'Gives players access to the app: each one logs in and sees only their own data.',
        pasos: [
          'If the club has several categories, pick at the top which one these players belong to.',
          'Fill in each row: shirt number, email and date of birth.',
          'Tap the circle at the end to add a photo. Optional.',
          'Add as many rows as you have players.',
          'Tap "Review and continue", then "Create the accounts".'
        ],
        ojo: 'Each player\u2019s password is their date of birth as ddmmyyyy. They can change it later.'
      },
      de: {
        titulo: 'Spieler anlegen',
        que: 'Gibt den Spielern Zugang zur App: jeder meldet sich an und sieht nur seine eigenen Daten.',
        pasos: [
          'Hat der Verein mehrere Kategorien, wähle oben, zu welcher diese Spieler gehören.',
          'Fülle jede Zeile aus: Trikotnummer, E-Mail und Geburtsdatum.',
          'Tippe auf den Kreis am Ende, um ein Foto hinzuzufügen. Optional.',
          'Füge so viele Zeilen hinzu, wie du Spieler hast.',
          'Tippe auf "Prüfen und weiter" und dann auf "Konten erstellen".'
        ],
        ojo: 'Das Passwort jedes Spielers ist sein Geburtsdatum als TTMMJJJJ. Es kann später geändert werden.'
      }
    },

    'cortes': {
      es: {
        titulo: 'Cortes de Video',
        que: 'Las jugadas que buscás, una atrás de otra, en el segundo exacto del contacto.',
        pasos: [
          'Elegí el equipo y la temporada.',
          'Elegí los partidos: todos, o solo los que te interesan.',
          'Marcá las acciones que querés ver. El número al lado dice cuántas hay de cada una.',
          'Tocá "Reproducir" y se van pasando solas.'
        ],
        ojo: 'Con Z volvés 2 segundos, con X adelantás, con R repetís el clip. Loop lo deja repitiendo.'
      },
      en: {
        titulo: 'Video Clips',
        que: 'The rallies you are looking for, one after another, at the exact moment of contact.',
        pasos: [
          'Pick the team and the season.',
          'Pick the matches: all of them, or only the ones you care about.',
          'Tick the actions you want to see. The number beside each says how many there are.',
          'Tap "Play" and they run one after the other.'
        ],
        ojo: 'Z goes back 2 seconds, X skips forward, R repeats the clip. Loop keeps it repeating.'
      },
      de: {
        titulo: 'Videoclips',
        que: 'Die gesuchten Ballwechsel, einer nach dem anderen, genau im Moment des Kontakts.',
        pasos: [
          'Wähle Mannschaft und Saison.',
          'Wähle die Spiele: alle oder nur die gewünschten.',
          'Markiere die Aktionen, die du sehen willst. Die Zahl daneben zeigt, wie viele es gibt.',
          'Tippe auf "Abspielen" und sie laufen nacheinander.'
        ],
        ojo: 'Z springt 2 Sekunden zurück, X vorwärts, R wiederholt den Clip. Loop wiederholt dauerhaft.'
      }
    },

    'panel_vivo': {
      es: {
        titulo: 'Scout en Vivo',
        que: 'Scouteás el partido mientras se juega, con el video al lado y las estadísticas calculándose solas.',
        pasos: [
          'Cargá los dos equipos y sus jugadores antes de empezar.',
          'Poné el video: podés usar la cámara con retraso para revisar la jugada que se te pasó.',
          'Tipeá cada acción con el teclado, igual que en DataVolley.',
          'Mirá las baterías y las direcciones actualizándose durante el partido.',
          'Al terminar, guardá el archivo. Abre en DataVolley sin convertir nada.'
        ],
        ojo: 'Antes de guardar, pasá el verificador de códigos: marca lo que no cierra, mientras todavía se puede corregir.'
      },
      en: {
        titulo: 'Live Scout',
        que: 'Scout the match as it is played, with the video beside you and the stats updating on their own.',
        pasos: [
          'Load both teams and their players before starting.',
          'Set up the video: you can use the delayed camera to review a rally you missed.',
          'Type each action with the keyboard, the same way as in DataVolley.',
          'Watch the target bars and directions update during the match.',
          'When you finish, save the file. It opens in DataVolley with no conversion.'
        ],
        ojo: 'Before saving, run the code checker: it flags what does not add up, while there is still time to fix it.'
      },
      de: {
        titulo: 'Live-Scouting',
        que: 'Scoute das Spiel während es läuft, mit Video daneben und Statistiken, die sich selbst berechnen.',
        pasos: [
          'Lade beide Mannschaften und ihre Spieler vor dem Start.',
          'Richte das Video ein: mit der verzögerten Kamera kannst du verpasste Ballwechsel prüfen.',
          'Tippe jede Aktion mit der Tastatur, genau wie in DataVolley.',
          'Beobachte, wie sich Zielbalken und Richtungen während des Spiels aktualisieren.',
          'Speichere am Ende die Datei. Sie öffnet sich in DataVolley ohne Umwandlung.'
        ],
        ojo: 'Vor dem Speichern den Code-Prüfer laufen lassen: er markiert Unstimmigkeiten, solange noch Zeit zur Korrektur ist.'
      }
    },

    'analisis': {
      es: {
        titulo: 'Análisis',
        que: 'Cómo viene el equipo contra los objetivos que fijó el club, y jugador por jugador.',
        pasos: [
          'Elegí si querés ver partidos, entrenamientos o todo junto.',
          'Mirá las baterías del equipo: cada una es un objetivo.',
          'Verde llegó, ámbar está cerca, rojo está lejos.',
          'Abajo está el mismo tablero para cada jugador del plantel.'
        ],
        ojo: 'Los objetivos los define el club y se cambian en la configuración. No son fijos.'
      },
      en: {
        titulo: 'Analysis',
        que: 'How the team is tracking against the club\u2019s targets, and player by player.',
        pasos: [
          'Choose whether to look at matches, training sessions, or both.',
          'Check the team bars: each one is a target.',
          'Green reached it, amber is close, red is far off.',
          'Below you get the same board for every player in the squad.'
        ],
        ojo: 'The targets are set by the club and can be changed in the settings. They are not fixed.'
      },
      de: {
        titulo: 'Analyse',
        que: 'Wie das Team im Vergleich zu den Vereinszielen dasteht, und Spieler für Spieler.',
        pasos: [
          'Wähle, ob du Spiele, Trainings oder beides sehen willst.',
          'Sieh dir die Team-Balken an: jeder ist ein Ziel.',
          'Grün erreicht, Bernstein nah dran, Rot weit entfernt.',
          'Darunter findest du dieselbe Übersicht für jeden Spieler des Kaders.'
        ],
        ojo: 'Die Ziele legt der Verein fest und können in den Einstellungen geändert werden. Sie sind nicht fix.'
      }
    }

  };

  /* ── Que pantalla es esta ─────────────────────────────────────────────── */
  function pantalla() {
    var p = (location.pathname || '').split('/').pop() || '';
    return p.replace(/\.html.*$/, '').toLowerCase();
  }

  /* ── Que idioma esta puesto ───────────────────────────────────────────── */
  function idioma() {
    try {
      if (window.getLang) return window.getLang();
      return localStorage.getItem('vb_lang') || 'es';
    } catch (e) { return 'es'; }
  }

  function texto() {
    var a = AYUDA[pantalla()];
    if (!a) return null;
    return a[idioma()] || a.es || null;
  }

  /* ── El cartel ────────────────────────────────────────────────────────── */
  var CERRAR = { es: 'Entendido', en: 'Got it', de: 'Verstanden' };

  function abrir() {
    var d = texto();
    if (!d) return;

    var fondo = document.createElement('div');
    fondo.id = 'ayuda-fondo';
    fondo.style.cssText =
      'position:fixed;inset:0;z-index:99999;background:rgba(3,7,18,.78);' +
      'backdrop-filter:blur(4px);display:flex;align-items:center;' +
      'justify-content:center;padding:20px;animation:ayFade .18s ease';

    var pasos = (d.pasos || []).map(function (p, i) {
      return '<li style="display:flex;gap:11px;padding:8px 0;' +
             'border-bottom:1px solid rgba(255,255,255,.06);line-height:1.55">' +
             '<span style="flex:none;width:21px;height:21px;border-radius:6px;' +
             'background:rgba(144,148,183,.13);border:1px solid rgba(144,148,183,.3);' +
             'color:#9094b7;font-size:11px;font-weight:700;display:flex;' +
             'align-items:center;justify-content:center;margin-top:1px">' +
             (i + 1) + '</span><span>' + p + '</span></li>';
    }).join('');

    fondo.innerHTML =
      '<div style="max-width:520px;width:100%;max-height:84vh;overflow:auto;' +
      'background:#0e1524;border:1px solid rgba(255,255,255,.1);border-radius:16px;' +
      'padding:26px;box-shadow:0 24px 70px rgba(0,0,0,.6)">' +

        '<div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:14px">' +
          '<div style="flex:none;width:34px;height:34px;border-radius:10px;' +
          'background:rgba(144,148,183,.13);border:1px solid rgba(144,148,183,.3);' +
          'display:flex;align-items:center;justify-content:center;font-size:17px">?</div>' +
          '<div style="flex:1;min-width:0">' +
            '<div style="font-size:19px;font-weight:800;line-height:1.2">' +
              (d.titulo || '') + '</div>' +
          '</div>' +
          '<button id="ayuda-x" aria-label="Cerrar" style="flex:none;width:30px;height:30px;' +
          'border-radius:8px;cursor:pointer;background:transparent;' +
          'border:1px solid rgba(255,255,255,.1);color:#8da0bc;font-size:15px">\u00d7</button>' +
        '</div>' +

        '<p style="color:#93a5c0;font-size:14.5px;line-height:1.6;margin:0 0 18px">' +
          (d.que || '') + '</p>' +

        '<ul style="list-style:none;margin:0 0 18px;padding:0;font-size:14px">' +
          pasos + '</ul>' +

        (d.ojo ?
          '<div style="background:rgba(144,148,183,.08);' +
          'border:1px solid rgba(144,148,183,.25);border-radius:10px;padding:12px 14px;' +
          'font-size:13.5px;line-height:1.55;color:#e8d4b0">' + d.ojo + '</div>'
          : '') +

        '<button id="ayuda-ok" style="width:100%;margin-top:18px;padding:12px;' +
        'border-radius:9px;border:none;cursor:pointer;background:#9094b7;' +
        'color:#150500;font-weight:700;font-size:14.5px">' +
          (CERRAR[idioma()] || CERRAR.es) + '</button>' +
      '</div>';

    function cerrar() {
      if (fondo.parentNode) fondo.parentNode.removeChild(fondo);
      document.removeEventListener('keydown', esc);
    }
    function esc(e) { if (e.key === 'Escape') cerrar(); }

    fondo.addEventListener('click', function (e) { if (e.target === fondo) cerrar(); });
    document.addEventListener('keydown', esc);
    document.body.appendChild(fondo);
    var x = document.getElementById('ayuda-x');
    var ok = document.getElementById('ayuda-ok');
    if (x) x.onclick = cerrar;
    if (ok) ok.onclick = cerrar;
  }

  /* ── El boton ─────────────────────────────────────────────────────────── */
  function poner() {
    if (!texto()) return;                       // sin ayuda escrita, sin boton
    if (document.getElementById('ayuda-btn')) return;

    var b = document.createElement('button');
    b.id = 'ayuda-btn';
    b.type = 'button';
    b.textContent = '?';
    b.setAttribute('aria-label', 'Ayuda');
    b.title = { es: '¿Cómo funciona esta pantalla?',
                en: 'How does this screen work?',
                de: 'Wie funktioniert dieser Bildschirm?' }[idioma()] || 'Ayuda';
    /* ── DONDE VA ─────────────────────────────────────────────────────
       El chat ya ocupa la esquina de abajo a la derecha: un circulo de
       46px en bottom:22 right:24, y su globito de aviso sube hasta 72px.
       El "?" se pone ARRIBA del chat, alineado al mismo eje, para que no
       se pisen ni en el celular.
       Si en alguna pantalla no hay chat, queda igual de comodo. */
    b.style.cssText =
      'position:fixed;right:26px;bottom:80px;z-index:8999;width:40px;height:40px;' +
      'border-radius:50%;cursor:pointer;background:rgba(144,148,183,.14);' +
      'border:1px solid rgba(144,148,183,.4);color:#9094b7;font-size:19px;' +
      'font-weight:800;line-height:1;box-shadow:0 6px 20px rgba(0,0,0,.35);' +
      'transition:transform .15s,background .15s';
    b.onmouseenter = function () {
      b.style.transform = 'translateY(-2px)';
      b.style.background = 'rgba(144,148,183,.22)';
    };
    b.onmouseleave = function () {
      b.style.transform = '';
      b.style.background = 'rgba(144,148,183,.14)';
    };
    b.onclick = abrir;
    document.body.appendChild(b);
  }

  /* si cambian el idioma, se actualiza el globito y lo que este abierto */
  window.addEventListener('langchange', function () {
    var b = document.getElementById('ayuda-btn');
    if (b) {
      b.title = { es: '¿Cómo funciona esta pantalla?',
                  en: 'How does this screen work?',
                  de: 'Wie funktioniert dieser Bildschirm?' }[idioma()] || 'Ayuda';
    }
    var f = document.getElementById('ayuda-fondo');
    if (f) { f.parentNode.removeChild(f); abrir(); }
  });

  var css = document.createElement('style');
  css.textContent = '@keyframes ayFade{from{opacity:0}to{opacity:1}}' +
                    '@media print{#ayuda-btn{display:none}}';
  document.head.appendChild(css);

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', poner);
  } else {
    poner();
  }

  window.abrirAyuda = abrir;      // por si se quiere llamar desde otro boton
})();
