# Fondale — colline del golfo e profilo della città

Legenda: **[V]** verificato (fonte citata) · **[S]** stima o deduzione, da confermare.
Geo-scout, 2026-11-19. Dati e script in `ref/dem/` (vedi `ref/dem/README.md`); grafico in `docs/qa/fondale_profilo.png`.

Fonti:
- **Copernicus DEM GLO-30** (DSM a 30 m), licenza "Copernicus WorldDEM-30", Full, Free & Open [V, testo letto dal PDF ufficiale].
- **OpenStreetMap**: cime `natural=peak/saddle` ed edifici con `building:levels`/`height` (Overpass API, 2026-11-19), © OpenStreetMap contributors (ODbL).
- **CORINE Land Cover 2018** (Copernicus Land Monitoring Service / EEA), dati "full, open and free" [V].
- Foto in `ref/foto/` (la foto Alamy `vista montagne.jpg` solo come riferimento visivo). Nessun dato Google.

---

## 1. Riepilogo per chi modella

- Dalla passeggiata si vede un **anfiteatro di colline da sud (180°) a nord (0°) passando per ovest**: la cresta più alta
  vista dal giocatore è a **SO-O (220°-285°), 3-4 km, 9-10° sopra l'orizzonte**: Monte Coregna, Monte Santa Croce,
  Monte Biassa, Monte Parodi [V DEM + OSM]. È la "montagna" delle foto.
- A **NO-N (290°-360°)** le colline sono più lontane (5-8 km) e più basse in angolo (4-6,7°); tra 307° e 345° il primo piano è
  occupato dal **colle del centro città** (~90 m s.l.m. nel DSM, a ~600 m, fino a 8,4°) [V DEM; identificazione S].
- A **NE-E (0°-120°)** le colline di Pitelli/Montalbano/Lerici sono basse: 2-3° [V]. Dietro spuntano di 0,1-0,3° i crinali
  dell'Appennino e delle Apuane a 35-50 km [V DEM; nomi S].
- **Bocca del golfo a SE (124°-154°): mare aperto**, orizzonte marino a ~6,5 km [V]. È il varco visibile nella foto del cannone.
- **Curvatura terrestre trascurabile** entro 10 km (0,03° a 8 km), da considerare solo per i crinali oltre 30 km (§7.4).
- L'**antenna del ponte** vista dalla partenza (187°, 6,2°, 293 m) si staglia esattamente davanti alla cresta del
  **Monte Castellana (191°, 6,7°)**: nel gioco la cresta va resa più chiara (foschia) perché l'antenna bianca resti leggibile (pilastro 2).

---

## 2. Punti di vista usati

Occhi a **3,3 m s.l.m.** = banchina +1,5 m [S, `ref/sezione.md`] + 1,8 m. Coordinate nella terna del progetto (`ref/area.md`).

| Punto | X, Y (m) | UE (uu) | File |
|---|---|---|---|
| Partenza del giocatore | 240, 84,5 | (24000, −8450, 180) | `ref/dem/orizzonte_spawn_*.csv` |
| Imbocco del ponte (origine) | 0, 0 | (0, 0) | `orizzonte_imbocco_ponte_*.csv` |
| Metà del Blocco 1 | 125, 84,5 | (12500, −8450) | `orizzonte_meta_blocco_*.csv` |
| Fine passeggiata (NE) | 550, 84,5 | (55000, −8450) | `orizzonte_fine_passeggiata_*.csv` |

Due varianti per punto: `_colline` (solo terreno oltre 1,5 km: la cresta da modellare) e `_tutto` (da 250 m, include città e
alberi perché il DEM è un DSM). Passo 1°, 360°. Per la partenza anche un profilo a 0,25° (usato nel grafico).

---

## 3. Profilo dell'orizzonte dalla partenza (sintesi, ogni 15°)

Elevazione = angolo della cresta sopra l'orizzontale (curvatura e rifrazione incluse). Fonte: DEM [V]; i nomi vengono da OSM.

| Azimut | Elev. | Dist. cresta | Quota | Cosa si vede |
|---|---|---|---|---|
| 0° N | 4,3° | 4,1 km | 316 m | colline sopra Termo/Melara (Monte Arsò, M. Croce dietro) |
| 15° | 4,5° | 4,4 km | 352 m | idem, crinale verso Sarzana |
| 30°-38° | 2,7-2,9° | 35 km | 1700-1840 m | **Appennino** (zona M. Orsaro-Marmagna [S]) appena sopra le colline vicine (2,6-3°) |
| 41° (asse passeggiata NE) | 3,0° | 4,4 km | 237 m | colline di Pitelli [S] |
| 52° | 2,7° | 13,6 km | 665 m | **Monte Grosso** (665 m, OSM), colli di Arcola/Vezzano [S] |
| 58°-64° | 2,4-2,7° | 38 km | 1700-1890 m | Appennino/Apuane [S] |
| 69°-74° | 1,9-2,2° | 48-50 km | 1810-2030 m | **Alpi Apuane** settentrionali [S nome] |
| 78° | 2,0° | 13 km | 629 m | Col di Paghezzana (OSM) |
| 90° E | 2,9° | 32 km | 1744 m | Apuane; davanti colline di Lerici a 2,5-3° |
| 104°-114° | 2,1-2,7° | 8,6-10 km | 350-456 m | **Lerici**: M. Castellazzo 352, M. Branzi 363, M. Rocchetta 456, M. Bandita 385 (OSM) |
| 120° | 1,3° | 11,6 km | 283 m | la costa scende verso Tellaro / Punta Corvo |
| **124°-154°** | **−0,06°** | 6,5 km | 0 | **mare aperto** (bocca del golfo; diga foranea non rilevabile nel DEM) |
| 156°-165° | 0,2-1,4° | 4,5-7 km | 20-170 m | punta del Varignano / Le Grazie, isola Palmaria dietro [S] |
| 180° S | 3,5° | 5,1 km | 312 m | **Monte Muzzerone** (325 m, 179°) sopra Portovenere |
| 187° | — | 293 m | 35 m | **antenna del ponte** (6,2°) |
| 191° | 6,7° | 4,1 km | 483 m | **Monte Castellana** (483 m) |
| 205° | 4,9-5,2° | 4,1 km | 358 m | sella: Bocca dei Cavallin (358 m) |
| 221° (asse passeggiata SO) | 8,4° | 3,2 km | ~500 m | fianco del Monte Coregna |
| 223° | 9,0° | 3,1 km | 500 m | **Monte Coregna** (500 m) |
| 243° | **10,3°** | 3,0 km | 543 m | **Monte Santa Croce** (543 m): punto più alto in angolo |
| 255° | 6,0° | 4,9 km | 530 m | sella: Colle del Telegrafo (516 m) |
| 272° | 9,5° | 3,7 km | 621 m | **Monte Biassa** (621 m) |
| 281° | 9,7° | 3,9 km | 673 m | **Monte Parodi** (673 m) |
| 291° | 6,2° | 7,2 km | 785 m | **Monte Capri** (785 m) |
| 297° | 6,7° | 5,6 km | 662 m | **Monte Due Gemelli o Bermego** (662 m) |
| 300°-305° | 4,1-5,1° | 5,5-6,9 km | 500-560 m | crinale verso il Monte Carmo/Sarara |
| 307°-345° | (4-5,5° colline) | — | — | **colle del centro città**, ~90 m s.l.m. a 0,5-0,6 km, **5-8,4°**: copre le colline dietro [V DEM; S nome: Castello San Giorgio / Poggio] |
| 319° | 4,3° | 4,7 km | 348 m | Monte Visseggi (348 m) |
| 351° | 4,9° | 7,0 km | 610 m | **Monte Croce** (610 m) |

Dagli altri punti la forma è la stessa; cambiano gli angoli: la cresta massima (M. Santa Croce) è a 10,9° dall'imbocco del
ponte, 10,6° da metà blocco, 10,2° dalla partenza, 9,3° dalla fine della passeggiata [V].

---

## 4. Cime e selle (OSM) visibili dalla partenza

Elenco completo (145 elementi, 43,98-44,24 N / 9,62-10,05 E) in `ref/dem/cime_osm.csv`, con azimut e distanza da origine e
partenza, elevazione angolare e visibilità calcolata sul DEM. Quote OSM [V OSM], confrontate con il DEM (scarto ≤ 20 m,
DSM con alberi). "Sulla cresta" = la cima forma l'orizzonte entro 0,15°.

| Cima | Quota OSM | Azimut (origine) | Dist. origine | Azimut / dist. / elev. dalla partenza | Sulla cresta? |
|---|---|---|---|---|---|
| Monte Muzzerone | 325 | 178,3° | 4,9 km | 179,4° / 5,1 km / 3,6° | sì |
| Monte Castellana | 483 | 190,1° | 3,8 km | 190,8° / 4,1 km / 6,7° | sì |
| Monte Coregna | 500 | 224,7° | 2,9 km | 222,9° / 3,1 km / 9,0° | sì |
| Monte Santa Croce | 543 | 246,9° | 2,8 km | 243,5° / 3,0 km / 10,3° | sì (massimo) |
| Monte Biassa | 621 | 275,5° | 3,6 km | 271,7° / 3,7 km / 9,5° | sì |
| Monte Parodi | 673 | 284,4° | 3,8 km | 280,6° / 3,9 km / 9,8° | sì |
| Monte Verrugoli | 745 | 276,0° | 4,9 km | 273,2° / 5,0 km / 8,4° | no, dietro al Biassa |
| Monte Capri | 785 | 292,9° | 7,2 km | 290,9° / 7,2 km / 6,2° | sì |
| Monte Due Gemelli o Bermego | 662 | 299,7° | 5,6 km | 297,1° / 5,6 km / 6,7° | sì |
| Monte Visseggi | 348 | 321,6° | 4,8 km | 318,9° / 4,7 km / 4,2° | sì (ma dietro il colle cittadino) |
| Monte Croce | 610 | 352,2° | 7,2 km | 351,2° / 7,0 km / 4,9° | sì |
| Monte Grosso (Arcola [S]) | 665 | 51,5° | 13,8 km | 52,0° / 13,6 km / 2,7° | sì |
| Monte Castellazzo | 352 | 102,6° | 9,2 km | 104,1° / 9,2 km / 2,1° | sì |
| Monte Rocchetta | 456 | 110,5° | 9,6 km | 112,0° / 9,5 km / 2,7° | sì |

Castellazzo e Rocchetta sono sulla **sponda di Lerici**
(sud-est). Le selle sulla cresta SO (Bocca dei Cavallin 358 m, Sella Scogliarini 491 m, Colle del Telegrafo 516 m) danno le
"tacche" del profilo.

---

## 5. Copertura del suolo e colore

CORINE 2018 sulle celle **visibili dalla partenza oltre 1,5 km** (`ref/dem/copertura_per_azimut_spawn.csv`). CORINE ha
un'unità minima di 25 ha: le case sparse finiscono nelle classi "agricole complesse" (242/243), non in "urbano".

| Fascia di azimut | Bosco | Terrazze / coltivi / oliveti con case sparse | Urbano | Lettura per il colore [S] |
|---|---|---|---|---|
| 0°-30° (N-NNE) | 60-84 % conifere/misto | 6-40 % | 0-4 % | verde scuro di pino con radure |
| 30°-75° (NE-ENE, Pitelli/Arcola) | 0-21 % | 44-69 % | 9-37 % | verde oliva chiaro punteggiato di case, frazioni |
| 75°-120° (E-ESE, Lerici) | 60-82 % (latifoglie + conifere) | 1-24 % | 0-10 % | bosco scuro, industria/porto in basso (22 % a 90-105°) |
| 124°-154° | — | — | — | mare |
| 150°-195° (Varignano, Muzzerone) | 56-79 % conifere/misto | 4-66 % | 11-31 % | pino scuro, case delle Grazie e di Fezzano sulla riva |
| 195°-240° (Coregna, Santa Croce; Marola, Cadimare, Fabiano) | 31-60 % | **31-49 %** | 1-4 % | **fascia bassa a terrazze con case sparse (foto), bosco sopra** |
| 240°-300° (Biassa, Parodi, Capri) | 62-83 % latifoglie (castagno [S]) | 6-38 % | 0-2 % | verde medio-scuro uniforme, terrazze nella fascia bassa |
| 300°-345° | solo 109 celle visibili | | | coperta dal colle cittadino: case della città |

Colori base proposti (sRGB, [S], da tarare sulle foto): bosco latifoglie (62, 86, 48) · conifere (48, 70, 44) · misto (55, 78, 46) ·
terrazze/coltivi con case (104, 116, 70) · oliveti (118, 124, 86) · macchia (88, 98, 60) · urbano (186, 160, 132) ·
industria/porto (150, 148, 142). Una mappa colore già pronta sulla griglia locale è in `ref/dem/morin_local_30m_colore_clc.png`
(base per l'albedo, da ammorbidire e arricchire di rumore).

Le foto confermano: terrazze e case chiare (bianco, crema, ocra, rosa) con tetti in coppi, a gruppi lungo le strade a mezza costa,
solo nella fascia bassa (fino a ~250-300 m s.l.m. [S]); sopra, bosco continuo; nessuna roccia nuda visibile da questo lato [S].

---

## 6. Profilo della città (entro ~1 km)

Fonte: OSM, 168 edifici entro 1,2 km con piani o altezza (`ref/dem/edifici_osm_1200m.csv`). La cortina di Viale Italia
(120-210 m) **non ha piani in OSM** [V]: resta coperta dal fondale blockout (`docs/uefn_blockout.md`).

- **Distribuzione [V OSM]**: 5 piani (41 edifici), 6 piani (20), 4 (19), 3 (24), 7-8 piani (11), 1-2 (35). Quasi tutti `house`
  importati da "Regione Liguria". Altezza stimata = piani × 3,2 m + 1,3 m (piano terra commerciale) [S].
- **Settore 295°-325°, 400-600 m** (oltre i Giardini pubblici, verso piazza Europa [S]): blocco di 5-8 piani, 17-27 m;
  ad es. way 205836671 e 205836940 (8 piani, X 55, Y 534), 205841791 (7 piani, X 39, Y 487). Dalla partenza 3-4° sopra
  l'orizzonte, cioè **sotto le chiome dei pini e delle palme dei giardini** (6-10°): visibili solo nei varchi [S].
- **Settore 30°-35°, 0,8-1,2 km** (lato Molo Italia/Viale San Bartolomeo [S]): 6-8 piani, 20-27 m.
- **Dubbi da verificare**: way 205844543 "18 piani" (X 105, Y 839): il DSM mostra solo +7 m sul circondario → probabile errore
  di tag o torre sottile [S]; way 849487393 "15 piani" nell'area militare (X −358, Y 216): DSM 7 m → quasi certamente errore [S].
  Gli edifici `height=15` dell'area militare/arsenale (X −300…−490, Y 200…490) sono capannoni plausibili [S].
- **Colle del centro**: il DSM sale a ~90 m s.l.m. a 0,5-0,6 km (azimut 307°-345° dalla partenza), cioè la città costruita
  sul pendio con il castello [S]. Dalla partenza vale **5-8,4°**: più delle colline dietro. È coerente con la foto dal ponte (case
  sul pendio a destra dell'antenna). Va modellato come parte del fondale cittadino (terreno + blocchi), non con il DEM grezzo.

---

## 7. Proposta tecnica per blender-artist

### 7.1 Cosa conta davvero [V calcolo di visibilità]
Celle di terreno visibili dalla partenza (`morin_local_30m_visibile_spawn.png`): 15,8 km² in totale, di cui
**~4,2 km² tra 1,5 e 3 km, ~7,8 km² tra 3 e 5 km**, solo ~1,7 km² tra 5 e 8 km e ~1,3 km² oltre. Il 79 % del terreno visibile
è entro 5 km: lì va la risoluzione.

### 7.2 Mesh del terreno (anelli, dalla griglia `morin_local_30m.npy`)
| Anello | Distanza dalla partenza | Contenuto | Passo griglia | Tri stimati |
|---|---|---|---|---|
| A | 0,25-1,5 km | città e colle del centro | non dal DEM: blocchi edifici + suolo lisciato (filtro di minimo 5×5 sul DSM per togliere i tetti [S]) | (nel budget edifici di fondale) |
| B | 1,5-5 km | cresta SO-O-NO, Lerici vicino, Varignano | 30 m lungo le creste, 60 m sui versanti (decimazione per errore, ≤ 3 m) | 30-40k |
| C | 5-10 km | M. Capri, M. Croce, Lerici, Arcola | 90-120 m | 8-12k |
| D | 30-50 km | Appennino e Apuane | una "tenda" di silhouette (strip verticale) costruita dal profilo ad angolo costante, posta a 12-15 km | ≤ 1k |

**Budget totale proposto: ≤ 55k tri a LOD0**, diviso in **8 settori da 45°** (≤ 8k ciascuno) per permettere culling e HLOD,
con 2 LOD (~50 % e ~15 %). Una sola risoluzione per settore, cuciture con bordo condiviso (o gonna verticale di 10 m) per non lasciare fessure.
Tolleranza: a 1080p con 90° di FOV un pixel vale 0,083° → 2 m a 1,5 km, 6 m a 4 km, 12 m a 8 km: la decimazione
può lavorare con un errore ammesso proporzionale alla distanza [V calcolo].
Le creste (tabella §3) vanno preservate: conviene bloccare i vertici lungo le linee di cresta (CSV `lat, lon` del punto di cresta per azimut).

### 7.3 Quote e acqua
- Z in Blender = quota s.l.m. − 1,5 m (Z 0 = banchina, [S]). L'acqua di gioco è a Z −1,0 m (PLAN): la linea di costa del DEM finisce
  così 0,5 m sotto la superficie; aggiungere una gonna fino a −5 m sotto la costa per non vedere fessure.
- Il DEM è un DSM: lungo la costa urbanizzata (Le Grazie, Fezzano, Lerici) le quote includono edifici; per il fondale è un vantaggio
  (danno volume), non correggere.

### 7.4 Curvatura terrestre [V calcolo]
Abbassamento = d²/2R × (1 − k), k = 0,13: **0,3 m a 2 km, 1,1 m a 4 km, 4,4 m a 8 km (0,03°)** → **trascurabile** fino a 10 km.
A 35 km vale 84 m e a 50 km 171 m (0,2°): già incluso nel profilo; per la tenda dell'anello D usare direttamente gli angoli del CSV.
L'orizzonte marino geometrico dagli occhi (3,3 m s.l.m.) è a **6,5 km**, 0,06° sotto l'orizzontale.

### 7.5 Distanze in UEFN, nebbia e visibilità [S, da verificare da uefn-builder]
- 10 km = 1 000 000 uu. Se UEFN limita la dimensione dell'isola o la distanza di rendering, alternativa: **omotetia** dell'anello C
  verso la partenza (es. ×0,5 su distanze, ×0,5 sulle altezze relative all'occhio) che conserva gli angoli dalla partenza;
  errore di parallasse percepibile solo per spostamenti grandi (lungo i 551 m della passeggiata la cresta a 4 km ruota di ~8°, quella
  dimezzata di ~16°). Gli anelli A-B vanno tenuti a scala reale.
- Mettere `cull distance` 0 (mai) sui settori del terreno e niente collisione (fuori dall'area giocabile).
- Nebbia esponenziale ad altezza con "aerial perspective": inizio ~1,5 km; a 4 km le colline devono restare verdi ma azzurrate
  (~30-40 % di foschia); Appennino/Apuane quasi color cielo (85-90 %). La foschia della cresta del Castellana serve a staccare
  l'antenna bianca (§1).

### 7.6 Texture e materiale
- Un **atlas 1024 px per settore** (o un'unica 2048 per l'anello B se il budget memoria lo consente; CLAUDE.md §4 indica 1024 per il fondale).
  Base: `morin_local_30m_colore_clc.png` (30 m/pixel; per 1024 px su un settore B di ~3,5 km il pixel vale ~3,5 m) con rumore
  macro per rompere i bordi CORINE e una tinta per fascia di quota (più chiaro e giallo-oliva in basso dove ci sono terrazze, verde scuro sopra).
- **Case sparse come pittura nell'albedo** (rettangolini chiari 2-4 px crema/rosa/ocra con un pixel rosso coppo), concentrate:
  Marola-Cadimare-Fabiano (200°-235°, quota < 250 m), Le Grazie e Fezzano sulla riva (165°-195°), Pitelli-Arcola (30°-75°),
  San Terenzo-Lerici (100°-120°). Niente mesh: a 3 km una casa di 10 m vale 0,2° (≈ 2 px).
- Eventuale normal map generica a bassa frequenza per i boschi; roughness alta e costante.

### 7.7 Città di fondale
Restano gli edifici di fondale ≤ 5k tri ciascuno (CLAUDE.md §4): il colle del centro (307°-345°) e il settore 295°-325° a 400-600 m
sono i punti dove le sagome si vedono oltre i giardini. Usare le altezze del CSV (5-8 piani) e il suolo dal DEM lisciato.

---

## 8. Confronto con le foto

| Foto | Direzione stimata | Corrispondenza con il profilo | Stato |
|---|---|---|---|
| `vista/vista montagne.jpg` (Alamy, solo riferimento) | lungo la passeggiata verso SO (~221°) | La vetta dominante appena a sinistra del punto di fuga = **Monte Coregna (223°)**, che sale a destra (dietro le palme) verso il **Santa Croce (243°)**. A sinistra cresta più bassa con sella (Bocca dei Cavallin, 205°) e il **Castellana (191°)**. Case sul versante basso = Marola/Fabiano (fascia a terrazze CORINE 210°-240°). Rapporto delle altezze (sinistra ~2/3 della vetta centrale) coerente con 6,7° contro 9-10° | [S] buona corrispondenza |
| `vista/banchina_vista_montagne_verso_ponte.jpg` | verso SO dalla banchina vicino al ponte | Due cime: a sinistra Castellana (191°), al centro Coregna/Santa Croce con case sotto. Dalla zona del ponte il Santa Croce sale a 10,9° | [S] |
| `ponte/ponte_verso_passegiata.png` | dal ponte verso NO (~313°) | Montagna larga a sinistra dell'antenna = **Monte Parodi (281°)** con la discesa verso Due Gemelli/Bermego (297°) e il calo a 4° dopo 300°; a destra case sul pendio = **colle del centro** (307°-345°) | [S] buona corrispondenza |
| `arredi/giardini_con panchine_affianco_palme.jpg` | verso SO con i giardini a destra | Montagna arrotondata a destra del centro (~235-250°) = massiccio del **Santa Croce** | [S] |
| `arredi/cannone_metà_banchina_verso_mare.jpg` | verso il mare (~130°) da metà passeggiata | Colline basse a sinistra (Lerici, 2-3°) che scendono in mare verso 120°, poi **orizzonte marino aperto** (124°-154°) | [S] buona corrispondenza |

Nessuna foto ha esif/FOV noti: le corrispondenze sono a vista. Per confermarle basterebbe una foto dalla partenza con un
riferimento di direzione (es. il ponte nell'inquadratura).

---

## 9. Dati ancora [S]
- Quota della banchina (+1,5 m s.l.m.) e quindi degli occhi (3,3 m): sposta gli angoli di < 0,05° sulle colline, irrilevante.
- Nomi dei crinali lontani (Appennino 30-38°, Apuane 58-74° e 90°): solo posizione e quota sono [V DEM].
- Identità del "colle del centro" (Castello San Giorgio / Poggio) e quanto sia terreno o edifici nel DSM.
- Gli edifici OSM a 15 e 18 piani (§6) e l'assenza di piani sulla cortina di Viale Italia.
- Limiti di distanza di rendering e dimensione del mondo in UEFN (§7.5).
- Colori: proposti da CORINE e dalle foto a occhio; da tarare con foto dell'utente con luce del tardo pomeriggio.

---

## 10. Colle cittadino v2 (blender-artist, 2026-11-19)

Script `blender/scripts/morin_fondale_colle.py` (usa `morin_fondale.py`), sorgente `blender/arte_fondale.blend` (copia della v1 in
`blender/arte_fondale_v1.blend`), collezione `FONDALE_Colle`. Posizioni in `exports/fondale/fondale_posizioni_v2.csv` (righe v1 +
colonna `stato_v2`).

**Perché il colle v1 era piatto.** La sagoma in angolo era già quasi quella del DSM (gli edifici senza piani prendevano il residuo
DSM − suolo), ma il suolo dell'anello A era il **minimo 5×5 del DSM** (finestra 150 m): sul colle (~350 m di diametro) prendeva il
piede del versante e la cima scendeva da ~77 a ~64 m s.l.m.; gli edifici diventavano un muro uniforme di scatole a tetto piano e
chiare, senza pendio visibile né gradoni.

**Cosa cambia [V DEM, S per i dettagli].**
- Suolo nel settore 295°-358° dalla partenza, 280-1500 m (rampe di 8° e 100/250 m): max(suolo v1, **minimo 3×3 + 2 passate di
  binomiale 3×3**, solo celle di terra). Cima del suolo ~77 m s.l.m. (DSM 92 m con edifici e alberi), rialzo massimo 17 m.
- Edifici (tutti quelli dei settori NO e N, 1318) poggiati su questo suolo: base al punto più basso della pianta − 1 m (gradoni a
  valle), altezza piani × 3,2 + 1,3 m da OSM o residuo DSM. **Tetti a padiglione** in coppi (piramide sul baricentro, falda
  0,22 × √area, 1,2-4 m) sulle piante convesse ≤ 10 lati e < 1500 m² (1046 edifici); tetti piani grigi/coppo sugli altri.
- Tinte più scure della v1 (§5): facciate crema/ocra/rosa/bianco sporco 0,74-0,88, coppi (0,46-0,60; 0,27-0,36; 0,21-0,26).
- Macchie d'albero (320 chiome opache 8-14 m) fra le case, più fitte in alto (parco del castello [S]); deroga in `docs/decisioni.md`.
- Texture planare 1024 del suolo `T_Fondale_Colle_Suolo_D` (1,1 m/px): giardini, alberi, strade, case dipinte fra le mesh.

**Sagoma confrontata col profilo DSM "tutto"** (elevazione massima per azimut, vertici delle mesh):
dalla partenza 318-336°: DSM 6,8-8,4°, v1 7,2-7,7°, **v2 7,4-8,8°**; dall'imbocco del ponte 336-348°: DSM 5,2-6,5°, v1 5,4-6,3°,
**v2 5,6-6,7°**. Il colle v2 è al più 0,6° sopra il DSM: non è stato esagerato oltre il dato. Se in sessione risulta ancora basso
rispetto alla foto dal ponte, la leva è un fattore di esagerazione del rialzo (da decidere con l'utente, sarebbe una deroga).

**Linea di vista:** nessun vertice degli asset nuovi nel cono partenza/imbocco → antenne (antenne a 180-187° dalla partenza, asset
nuovi a 221 m minimi e fuori azimut).

**In UEFN:** importare da zero i 9 asset nuovi (×3 LOD, colore vertice con `FbxFactory` come §8.1 di `docs/uefn_fondale.md`),
materiale facciate per città e alberi, nuova MI per il suolo; nascondere `SM_Fondale_Citta_NO_01..03` e `N_01..02` (cancellarli solo con
conferma dell'utente). Render: `docs/qa/arte_fondale_v2_colle_*.png`.
