/* ═══════════════════════════════════════════════════════════════════════════
   mapa_videos.js — LOS VIDEOS DE CADA PARTIDO

   Una linea por partido: el codigo del partido y el link de YouTube.

   ── POR QUE SE REHIZO ─────────────────────────────────────────────────────
   Los links estaban guardados con nombres viejos:

       P2026-08-07-banco-provincia-vs-gelp   ← como se guardo
       P2026-08-07-20260807AMIS              ← como se llama ahora

   Al reprocesar los partidos, el codigo cambio y la pantalla ya no los
   encontraba: por eso los casilleros aparecian vacios aunque los videos
   estuvieran cargados.

   Aca estan con el codigo actual.

   ── COMO SE AGREGA UNO NUEVO ──────────────────────────────────────────────
   Lo mas facil es desde la pantalla "Cargar videos": se pega el link, se
   aprieta "Generar archivo de links" y se reemplaza este archivo.

   A mano tambien se puede: una linea mas, con el codigo del partido —el que
   figura como "cód" en esa pantalla— y el link.

   ═══════════════════════════════════════════════════════════════════════════ */

window.MAPA_VIDEOS = {

  /* 07/08/26 · GELP vs Banco Provincia */
  "P2026-08-07-20260807AMIS": "https://youtu.be/a1c80N0DTHE",

  /* 14/08/26 · GELP vs Velez */
  "P2026-08-14-20260814GELP": "https://youtu.be/-JRsqsJLD8Y"

  /* Faltan cargar:
       50101   13/08/26  Estudiantes vs River
       50111   21/08/26  GELP vs Estudiantes
       50113   28/08/26  Boca vs GELP            */

};

/* © 2025-2026 Volley-Stats · Ignacio Verdi · Software propietario */
