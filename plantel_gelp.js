/* ═══════════════════════════════════════════════════════════════════════════
   plantel_gelp.js — EL PLANTEL DE GELP

   Esta es la lista REAL del club, y es la que manda en la pantalla Equipo.

   ── POR QUE EXISTE ────────────────────────────────────────────────────────
   El otro archivo —datos_equipo.js.enc— se genera al procesar los .dvw, asi
   que solo tiene a las jugadoras que YA JUGARON. Una jugadora nueva no
   aparece hasta su debut, aunque tenga cuenta y cargue wellness.

   Y si se la agrega a mano ahi, el siguiente HACER_TODO la borra: ese
   archivo se rehace de cero en cada corrida.

   Este, en cambio, nadie lo pisa.

   ── COMO SE EDITA ─────────────────────────────────────────────────────────
   Se abre con el Bloc de notas y se agrega una linea:

       { num: 4,  ap: "GARCIA",  nombre: "Lucia",  pos: "PUNTA"   },

   Posiciones que entiende la app:
       ARMADOR · OPUESTO · PUNTA · CENTRAL · LIBERO

   ── DE DONDE SALIO ────────────────────────────────────────────────────────
   De los 4 partidos cargados al 2 de septiembre de 2026:
       vs Estudiantes (3-0)  ·  vs Boca (0-3)  ·  y los dos anteriores

   ═══════════════════════════════════════════════════════════════════════════ */

window.PLANTEL_GELP = {
  temporada: "2026",

  jugadoras: [
    { num: 1,  ap: "RUELLI",             nombre: "Julieta Arianne", pos: "PUNTA"   },
    { num: 2,  ap: "NUÑEZ",              nombre: "Maria Victoria",  pos: "CENTRAL" },
    { num: 3,  ap: "FAIAZZO",            nombre: "Abril",           pos: "CENTRAL" },
    { num: 5,  ap: "BICECCI",            nombre: "Valentina",       pos: "ARMADOR" },
    { num: 6,  ap: "OYOLA",              nombre: "Martina",         pos: "LIBERO"  },
    { num: 7,  ap: "GOMEZ",              nombre: "Zoe",             pos: "LIBERO"  },
    { num: 8,  ap: "RIOS",               nombre: "Carmela",         pos: "PUNTA"   },

    /* La #9 es de inferiores y no jugo ni un punto: no se carga hasta que
       tenga minutos y datos propios. */

    { num: 10, ap: "SILBERSTEIN",        nombre: "Luna Aime",       pos: "ARMADOR" },
    { num: 11, ap: "MATICH",             nombre: "Maria Victoria",  pos: "CENTRAL" },
    { num: 12, ap: "SIRI",               nombre: "Marlen",          pos: "CENTRAL" },
    { num: 13, ap: "COSULICH MARTINEZ",  nombre: "María Luz",       pos: "ARMADOR" },
    { num: 14, ap: "GRAFF",              nombre: "Brenda",          pos: "CENTRAL" },

    { num: 16, ap: "SANABIO",            nombre: "Pamela",          pos: "PUNTA"   },

    { num: 17, ap: "LLANOS",             nombre: "Keila Ariella",   pos: "PUNTA"   },
    { num: 19, ap: "LEDESMA",            nombre: "Jazmin",          pos: "CENTRAL" },
    { num: 21, ap: "KAPLAN",             nombre: "Morena",          pos: "PUNTA"   },
    { num: 22, ap: "DIEZ",               nombre: "Valentina",       pos: "OPUESTO" }
  ],

  staff: []
};

/* La app busca la lista en .jugadores, sin importar el deporte. */
window.PLANTEL_GELP.jugadores = window.PLANTEL_GELP.jugadoras;

/* © 2025-2026 Volley-Stats · Ignacio Verdi · Software propietario */
