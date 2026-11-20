# Scheda — Foto nuove dell'utente (2026-11-20): dehors, cestini, cartelli, Sirena, pescherecci, imbarco, ingresso della marina

Legenda: **[V]** verificato con fonte citata (OSM, articolo) · **[V-foto]** si vede nella foto indicata (forma, colore, numero) ·
**[S]** stima (calcolo o prospettiva), da confermare · **[V-utente]** detto dall'utente.
Coordinate di progetto (X lungo la passeggiata verso NE, Y verso la città, Z in alto, origine all'imbocco del ponte): `ref/area.md`.
**UE = (X·100, −Y·100, Z·100)**. Azimut "di progetto" misurato da +Y verso +X, come in `radice_molo.md` §10.1
(az 90 = +X, az 180 = −Y verso il mare, az 270 = −X verso il ponte). **Yaw UE = az − 90.**
Dati OSM: `ref/osm/morin_bbox.osm`, `ref/osm/morin_blocchi23.osm`, © OpenStreetMap contributors (ODbL).
Geo-scout, 2026-11-20. Nessun uso di `blender` né di `unreal-mcp`.

**Foto analizzate** (catture Street View e foto dell'utente; per le texture vale la deroga [SV] di CLAUDE.md §5):
| Sigla | File | Px | Cosa |
|---|---|---|---|
| R2 | `ref/foto/vista/ristoranti_visti_da_di_fronte_2.png` | 1150 × 519 | dehors dei ristoranti A1-A3 |
| T1 | `ref/foto/vista/traghetto_bigliettaria_azzurra.png` | 1156 × 584 | casette, tettoia, pontile e traghetto, di tre quarti |
| T2 | `ref/foto/vista/biglietteria_traghetto_di_fronte.png` | 1190 × 597 | portale e cancello, frontale |
| M1 | `ref/foto/vista/nautica_marina.png` | 1372 × 502 | ufficio galleggiante, passerella, portale di lato |
| M2 | `ref/foto/vista/marina_nautica.png` | 1240 × 599 | portale della marina, frontale |
| K | `ref/foto/arredi/cestino.png` | 161 × 187 | cestino |
| G | `ref/foto/arredi/cartelli_inizio_passegiata.png` | 179 × 309 | palo con cartelli, new jersey blu e bianchi |
| S | `ref/foto/arredi/scultura_donna_con_pinne_su_sedia.png` | 496 × 459 | Sirena sulla sedia |
| F1 | `ref/foto/vista/inizio_passegiata_ristoranti_che_vanno_verso_il_ponte.png` (2023, già in `radice_molo.md`) | 1886 × 811 | usata per controllo |

**Da NON modellare né copiare nelle texture:** cerchi/frecce di navigazione (R2 in basso, x 460-800 / y 455-519; M1 sull'acqua,
x 460-620 / y 400-458; M2 a destra, x 1130-1240 / y 395-425), icona arancione "forchetta e coltello" (R2 x 950-1015 / y 58-105),
scritte "© 2025/2026 Google" (R2 x 230-330 / y 330-345 e x 645-700 / y 55-65; T1 x 795-885 / y 190-200 e x 650-700 / y 470-480;
T2 x 180-300 / y 10-50 e x 1080-1170 / y 50-70; M2 x 520-590 / y 125-140, x 340-430 / y 400-415, x 900-990 / y 170-180),
la scritta di UI in basso a sinistra in T1 (x 0-100 / y 520-584), persone (R2 x 410-520 / y 185-280; M2 tutta la fascia
x 360-700 / y 255-599 con la bicicletta), il furgone con targa (R2 x 0-50), i piccioni.

---

## 1. Punti di presa delle foto

| Foto | Punto (X; Y; Z) | Azimut | Yaw UE | FOV orizz. | Metodo | Stato |
|---|---|---|---|---|---|---|
| R2 | **(9,5; 105; ~2,5)**, sulla strada di servizio all'altezza dell'incrocio | **≈ 234°** (verso SO, guarda la fila A di sbieco) | 144 | ~90° | minimi quadrati su 3 punti di facciata OSM: risvolto di A3 (0,9; 79,9) a x 170, inizio e fine della parte rosa (0,55; 98,8) x 585 e (0,55; 102,6) x 790; controllo con lo scudo giallo sull'arco (x 940) | [S] ±1 m in X, ±2,5 m in Y, ±6° |
| T1 | **(63; 82; ~2,5)**, sul camminamento a ~2 m dal ciglio | **≈ 135°** | 45 | ~100° | camminamento che fugge a sinistra (+X), pontile che fugge a destra (−Y), altezza apparente della casetta vicina (~3 m su 240 px → ~6 m) | [S] ±3 m, ±10° |
| T2 | **(71,7; 84; ~2,5)**, davanti al portale | **≈ 180°** (lungo il pontile, verso −Y) | 90 | ~90° | il portale è centrato sull'asse OSM del pontile (way 175935430, X 71,7 a Y 80,3) | [S] ±1,5 m |
| M1 | **(160; 81; ~2,5)**, sul ciglio a NE del portale | **≈ 210°** | 120 | ~100° | punto di fuga del ciglio (Y 80, OSM coastline) oltre il bordo destro; il portale si vede di tre quarti dal lato +X | [S] ±4 m, ±10° |
| M2 | **(151; 84; ~2,0)**, davanti al portale | **≈ 180°** | 90 | ~85° | il ciglio attraversa la foto in orizzontale; a sinistra (+X) gru del porto commerciale e nave da crociera, a destra (−X) palme della passeggiata e Mirabello | [S] ±1,5 m |
| S | **(17; 98; ~1,7)**, sull'angolo in cubetti | **≈ 200°** (verso il ponte) | 110 | ~70° (ritaglio) | statua sul pavé a coda di pavone, strada d'asfalto a destra (−X), bacino a sinistra (+X), fila A gialla sul fondo a destra, cartelli di divieto del molo (13-15; 80-83) in alto a sinistra | [S] ±3 m |
| G | non ricavabile (teleobiettivo, ritaglio da 179 px) | — | — | — | il palo è stato localizzato con F1 (§4) | — |
| K | primo piano, luogo non ricavabile | — | — | — | — | — |

**Conferma della lettura di T1/T2.** In T2 il traghetto si vede a sinistra del cancello, cioè sul lato **+X (est)** del pontile;
in T1, con la camera a ovest che guarda verso est, il traghetto è **oltre** il pontile. Le due foto concordano: il traghetto era ormeggiato
sul **lato est** del pontile. Anche la rete e la ringhiera stanno sul lato **ovest** (T1 x 490-690, T2 x 740-790), e il lato est è libero
per l'imbarco. Nel progetto il battello è a **ovest** (`Arte_Imbarco_Battello` X 6656, pontile X 7200): vedi §7.6 e domanda D1.

---

## 2. Dehors dei ristoranti della fila A (radice del molo)

### 2.1 Cosa si vede in R2 (2025) [V-foto]
- **Ombrelloni quadrati bianchi** (telo crema-bianco, palo bianco/grigio chiaro, bracci a raggiera): **5 aperti** nel tratto inquadrato
  (Y ≈ 84 → 107), più 1-2 parzialmente visibili verso A3 giallo. Uno grande davanti all'arco giallo, gli altri più piccoli.
  Quello grande poggia su una **piastra di base chiara** (~0,8 × 0,8 m, in pietra o cemento) [V-foto]; misure [S].
- **Tavoli neri** quadrati a gamba centrale e **sedie nere** (polipropilene/rete metallica), 2-4 sedie per tavolo: ~10 tavoli visibili.
- **Fioriere grigio-antracite** squadrate con arbusti sempreverdi (pittosporo/lauro/elaeagnus, foglia verde-giallastra): ~11 visibili,
  a gruppi di 2-3 lungo il fronte del dehors, con varchi per entrare.
- **Lavagna** in legno arancio-bruno a cavalletto (A-frame) con scritte a gesso: davanti al gruppo di sinistra.
- **Cavalletto pubblicitario bianco** (A-frame in lamiera con cornice) "RISTO PESCHERIA — o mangi o porti via — SCEGLI IL PESCE —
  SCEGLI LA COTTURA", con un pesce disegnato: davanti al gruppo centrale.
- In basso a destra un **carrello di legno su ruote** (pallet con ruote, ~1,2 × 0,6 m): opzionale.
- Insegne: pannello bianco "Consorzio Pescatori — Sapori di Mare e di Terra" sopra la parte rosa (A2); scudo bordeaux "dai pescatori"
  con illustrazione sull'arco giallo (A1). Entrambe da sostituire (§9).

### 2.2 Posizioni ricavate (camera R2, orizzonte a y ≈ 153, camera 2,5 m) [S, ±1 m]
| Oggetto | Px (base) | Posizione (X; Y) | UE |
|---|---|---|---|
| Palo dell'ombrellone grande (4 × 4) | x 850, y 380 | **(2,6; 103,7)** | (260, −10370) |
| Fioriera centrale, la più a sinistra | x 525, y 330 | (3,4; 99,7) | (340, −9970) |
| Fioriera centrale, la più a destra | x 705, y 365 | (3,1; 102,3) | (310, −10230) |
| Fioriera davanti all'arco | x 1070, y 410 | (2,2; 105,6) | (220, −10560) |
| Fioriere lontane, gruppo di sinistra | x 60-200, y 240-250 | X ≈ 4, Y ≈ 84-88 | (400, −8400…−8800) |
| Ombrelloni piccoli a sinistra | x 220-410 | X ≈ 3-4, Y ≈ 94 e ≈ 98 | — |
| Cavalletto "Risto Pescheria" | x 470, y 382 | **(5,1; 100,4)** | (510, −10040) |
| Lavagna | x 145, y 293 | **(5,7; 92,8)** | (570, −9280) |

**Regola che ne esce** (facciata OSM a X ≈ 0,3-0,6 per Y > 79,9; a X ≈ 1,2-1,4 per Y 68-79,9):
- fascia del dehors **dalla facciata a X ≈ 4,2** (3,5-4 m di profondità) [S];
- fioriere in fila **parallela alla facciata, asse X ≈ 3,2-4,0**, gruppi di 2-3 con varchi di 1-1,5 m [S];
- pali degli ombrelloni a **X ≈ 2,6-3,5**, passo ~4-4,5 m lungo Y [S];
- **striscia pedonale libera X ≈ 4,2 → 6,5** (bordo ovest dell'asfalto nel modello), su cui stanno solo lavagna e cavalletto [S].

### 2.3 Misure degli elementi
| Elemento | Misure | Colore (campione dalla foto) | Stato |
|---|---|---|---|
| Ombrellone quadrato grande | telo **4,0 × 4,0 m** (misurato ~3,4-3,6 m sulla proiezione), bordo del telo a ~2,4 m, cima ~3,1 m; palo Ø ~6 cm; base 0,8 × 0,8 × 0,1 m | telo bianco caldo, palo bianco | forma [V-foto]; misure [S] |
| Ombrellone quadrato piccolo | telo **3,0 × 3,0 m** (misurato ~3,0 m), stesse altezze | come sopra | [S] |
| Tavolo | 0,70 × 0,70 m, h 0,75, gamba centrale e piede a croce | nero | [S] |
| Sedia | 0,45 × 0,50 m, seduta 0,45, schienale 0,85 | nera | [S] |
| Fioriera | **1,00 × 0,45 × 0,45 m** + arbusto h 0,7-1,0 m (totale ~1,3-1,5 m) | antracite **#222B35** | [V-utente] forma; misure [S]; coincide con `radice_molo.md` §3.2 |
| Lavagna A-frame | 0,6 × 1,1 m, cornice in legno | legno arancio-bruno, lavagna nera | [S] |
| Cavalletto bianco A-frame | 0,6 × 1,1 m | bianco, scritte blu-rosse (da reinventare) | [S]; riusare `SM_Molo_CavallettoMenu` (0,7 × 0,41 × 1,09) con texture nuova |

### 2.4 Proposta di layout per sezione (da R2 per A1-A3 bianco; A3 giallo e A4 per analogia) [S]
Sezioni e tratti Y da `radice_molo.md` §10.2 (ordine corretto). A5 = dehors a righe del ristorante C, **già fatto** (`molo_posizioni_v2.csv`).
| Sezione | Tratto Y | Ombrelloni (pali) | Tavoli | Fioriere | Altro |
|---|---|---|---|---|---|
| A1 arco giallo + risvolto nord | 102,6 → 108 | 1 grande 4 × 4 a (2,6; 103,7) | 3 | 2: (2,2; 105,6), (1,0; 108,0) | — |
| A2 rosa | 98,8 → 102,6 | 1 piccolo 3 × 3 a (2,4; 98,6) | 2 | 3 in fila a X 3,3: Y 99,7 / 100,9 / 102,1 | cavalletto (5,1; 100,4) |
| A3 bianco | 79,9 → 98,8 | 4 piccoli a X 3,0: Y 94,5 / 90,0 / 85,5 / 81,5 | 8 | 6: due gruppi da 3 a X 3,8, Y 84,0-86,4 e 91,8-94,2 | lavagna (5,7; 92,8) |
| A3 giallo | 68 → 79,9 | 2 piccoli a X 3,8: Y 76,0 / 71,5 | 4 | 3 a X 4,4: Y 69,0 / 73,8 / 78,6 | — |
| A4 blocco sud | 62 → 68 | nessuno | 0-2 | 2 a X 4,0: Y 63,0 / 66,5 | — |
| **Totale** | 62 → 108 | **8** (1 grande + 7 piccoli) | **~18** (con 2-4 sedie: ~55 sedie) | **16** | 1 lavagna, 1 cavalletto |

Collisioni: box bassi per fioriere e basi degli ombrelloni; tavoli e sedie box semplici (come il dehors del ristorante C).
Nessun elemento oltre X 4,2 tranne lavagna e cavalletto: la corsia del molo (X 4,2 → 9,55) resta libera.

---

## 3. Cestini

### 3.1 Il cestino tipico (foto K, e cestino "cilindrico scuro" di F1) [V-foto]
| Voce | Dato | Stato |
|---|---|---|
| Forma | corpo a **capsula**: pianta ovale/rettangolare con spigoli molto arrotondati, fianchi verticali, **cupola** in alto con **bocca ovale** sul fronte della cupola; nessun piede visibile | [V-foto] K |
| Fronte | **fascia verticale in rilievo** al centro con uno stemma in alto e decori/scritta in verticale (stemma comunale: pubblico, si può tenere stilizzato); piccola **targhetta bianca** a destra della bocca | [V-foto] K |
| Materiale e colore | ghisa o acciaio verniciato **grigio grafite** (campione **#4B4A48**), satinato con polvere e graffi chiari | [V-foto]; materiale [S] |
| Misure | **0,50 (L) × 0,38 (P) × 0,95 m**, bocca ~0,22 × 0,12 m | [S] (proporzioni della foto: altezza/larghezza ≈ 1,9) |
| Confronto | `SM_Morin_Cestino` attuale: cilindro 0,45 × 0,45 × 0,95 m, 252 tri. **Forma diversa**: serve `SM_Morin_Cestino_v2` (≤ 600 tri, LOD 50/15 %) | [V] `docs/uefn_arte.md` §22 |

### 3.2 Posizioni
| Fonte | Posizioni (X; Y) | Stato |
|---|---|---|
| OSM `amenity=waste_basket` nel Blocco 1 | **(18,0; 91,3)** node 5913688317 e **(41,9; 92,4)** node 5913688321 (check_date 2024-10-16). Nessun altro cestino OSM fra il ponte e X 300 | [V] OSM |
| F1 (2023) | un cestino all'angolo, calcolato a ≈ (16,8; 93,7): è quello OSM (18,0; 91,3) entro l'errore | [V-foto] / [S] posizione |
| Progetto (9 istanze `Arte_Imbarco_Cestini`, CSV `exports/imbarco/imbarco_posizioni_v1.csv`) | Y 92,1, X **18,55 / 36,55 / 72,55 / 90,55 / 126,55 / 144,55 / 180,55 / 198,55 / 234,55** (panchina + 2,05 m; passo 18 o 36 m, medio 27 m) | [V] CSV |

**Proposta:** sostituire la mesh nelle **stesse 9 posizioni** (regola "accanto alla panchina", decisione del 2026-11-20 in `docs/decisioni.md`).
Il primo (18,55) coincide con OSM (18,0). Il secondo OSM (41,9) cade fra le palme 38,4 e 47,4: con il **layout v4** della fascia palme
(PLAN, ancora aperto: filari da X 20,4, tutto −0,6 m) conviene spostare `Cestino_01` da 36,55 a **≈ 41,9** se la panchina vicina lo
permette. Il passo reale non è ricavabile da OSM (solo 2 nodi) [S].

---

## 4. Cartelli all'inizio della passeggiata (lato mare) e new jersey

### 4.1 Posizione [S calcolo]
Nella F1 (2023, camera `radice_molo.md` §10.1: (13,65; 118,43; 2,84), az 199,7°, FOV 87°) c'è un palo sottile a x ≈ 413 px con la base a
y ≈ 435-440, subito dietro una barriera e un cestino. Proiettato a terra: **palo a (19,2; 81,1) ± 1,5 m**, cioè sullo **spigolo della
banchina** dove il camminamento incontra il molo (nodo OSM della coastline **(19,2; 80,4)**). È l'inizio della passeggiata, lato mare,
sulla destra di chi parte dal ponte verso NE, come dice l'utente [V-utente]. UE **(1920, −8110, 0)**.
La foto G (ritaglio a teleobiettivo) mostra dietro il palo l'acqua del bacino, barche della marina e un traghetto con le zattere rosse.

### 4.2 Il palo e i pannelli [V-foto G; misure S]
| Elemento | Descrizione | Misure [S] |
|---|---|---|
| Palo | tubo zincato grigio chiaro | Ø 60 mm, h ~3,2 m |
| Targa in cima (orizzontale, a bandiera) | bianca, bordo nero, testo nero su due righe: **"banchina / G. Thaon di Revel"** (nome pubblico: si tiene) | ~0,90 × 0,25 m, a ~3,0 m |
| Testata del pannello | targhetta bianca con un gabbiano stilizzato: **"banchina Costantino Morin"** (pubblico: si tiene) | ~0,60 × 0,12 m |
| Pannello principale | bianco; pittogramma **blu** con adulto e bambino per mano; sotto, testo: **"ATTENZIONE — I bambini devono essere accompagnati per mano lungo la banchina"** | ~0,60 × 0,90 m, bordo inferiore a ~1,9 m |
| Targhetta in basso | gialla con testo piccolo **illeggibile** (forse riferimento all'ordinanza o al Comune) | ~0,60 × 0,15 m. Nel gioco: testo generico non leggibile [S] |
Il testo del pannello è un avviso pubblico: si riproduce com'è. Le lettere vanno ricostruite in vettoriale (il pannello nella foto è
largo ~50 px: troppo poco per una texture).

### 4.3 New jersey blu e bianchi [V-foto G]
- Sono **barriere in plastica riempibili d'acqua** (sagoma arrotondata, superficie liscia e lucida, tappi di riempimento), alternate
  **blu** e **bianche**: non sono le barriere in cemento bianco-nere già nel progetto (`SM_Morin_NewJersey`, 2,0 × 0,61 × 0,81 m).
  Materiale [S] dalla forma (spigoli molto arrotondati, nessuna scheggiatura, colore pieno).
- Misure tipiche dei modelli in plastica: **1,20 × 0,45 × 0,75 m** [S].
- In G se ne vedono **2** (una blu ai piedi del palo, lungo il ciglio; una blu-bianca in primo piano ruotata rispetto alla prima):
  seguono lo **spigolo** della banchina. Nella F1 del 2023 al loro posto c'era una barriera in cemento bianco-nera a ≈ (18,7; 89).
- **Proposta [S]: 4 barriere**, alternate blu/bianco, a 0,35 m dal ciglio:
  - lungo Y 80 (yaw UE 0): **(20,4; 80,35)**, **(21,7; 80,35)**;
  - lungo lo smusso verso il molo (ciglio OSM da (19,2; 80,4) a (10,2; 71,3), yaw UE ≈ −45,3, lato lungo lungo lo smusso): **(17,6; 79,3)**, **(16,5; 78,2)**.
  Da confermare con l'utente (domanda D2). Attenzione a `Bitta_00` (26,0; 80,7): libera.

---

## 5. Scultura: la Sirena sulla sedia

| Voce | Dato | Stato |
|---|---|---|
| Nome e autore | **"La Sirena del Golfo dei Poeti"**, artista **Aidyn Zeinalov**, `artwork_type=statue`, `material=metal` | [V] OSM node 9592234744 |
| Posizione | **(13,8; 91,9)**, sull'angolo in cubetti fra la strada di servizio e l'inizio della passeggiata, ~2-3 m dal cordolo dell'asfalto. UE **(1380, −9190, 15)** (angolo in cubetti a +0,15 m) | [V] OSM; la foto S conferma il contesto (cubetti a coda di pavone, strada a destra, bacino e pescherecci a sinistra, cantiere con rete arancione e camion sul molo, fila A gialla sul fondo) |
| Cosa rappresenta | donna seduta su una **sedia** di legno/metallo, busto leggermente in avanti, mani sulle ginocchia, **pinne da sub ai piedi** appoggiate su una lastra; è la "sirena" moderna | [V-foto] S |
| Materiale | bronzo scuro con patina (campione **#4D4B47**); basamento in **pietra o cemento grigio a superficie bocciardata** (**#979089**) con una lastra di bronzo in cima (rete/sabbia a rilievo) | bronzo [V] OSM (metal) + [V-foto]; pietra [S] |
| Misure | basamento **1,40 × 1,00 × 0,75 m** [S]; sedia a grandezza naturale (seduta 0,45, schienale ~0,95 m sopra il basamento); figura seduta alta ~1,30 m sopra il basamento; **totale ~2,1-2,2 m** | [S] dalle proporzioni (sedia come metro) |
| Orientamento | la figura guarda verso la **strada e i ristoranti** (−X), con lo schienale verso il bacino: az ≈ 280 ± 20°, yaw UE ≈ 190 | [S] |
| Nel 2023 | in F1 al suo posto c'è il "blocco grigio basso" ≈ (11; 93) di `radice_molo.md` §2.3: era probabilmente il basamento | [S] |
| Nel gioco | `SM_Molo_Sirena`: opera d'autore, quindi **stilizzata** e non una copia fedele (decisione già presa in `radice_molo.md` §7.1). Nome dell'opera e dell'artista sono pubblici: possono stare su una targhetta | — |

---

## 6. Pescherecci davanti al ristorante C

### 6.1 Dove [V OSM + V-utente]
- Il ristorante C ("ristorante bianco e blu", `SM_Molo_Edificio_C_v2`) occupa X −12,1 → −7,5, Y 24,8 → 42,2 [V OSM 205840540].
  Di fronte, oltre la corsia del molo e la fila di palme in vaso (X 8, Y 31-67), c'è il **ciglio est del molo**: dal confine OSM
  (coastline 137121074) corre da (10,2; 71,3) a (6,8; −79,3), quindi **X ≈ 9,6 a Y 45, 9,4 a Y 35, 9,1 a Y 25** [V].
- OSM mappa anche un **pontiletto** stretto lungo il ciglio, `man_made=pier` way 1382978940, da **(11,1; 35,0) a (7,2; −77,8)** [V]:
  a sud di Y 35 le barche si ormeggiano a questo, a nord direttamente al ciglio.
- Nella foto S e in F1 si vedono barche bianche con cabina ormeggiate lungo questo ciglio (F1 x 510-590, ≈ X 12-15, Y 60-70) [V-foto].
- Nel progetto quell'acqua è vuota (nessuna barca di `marina_barche_v3.csv` a X < 45) [V].

### 6.2 Tipo e aspetto (piccola pesca ligure) [S, da conoscenza generale: nessuna foto ravvicinata]
| Tipo | Lunghezza × larghezza | Aspetto |
|---|---|---|
| **A — peschereccio da strascico/piccola pesca** | 14 × 4,6 m, bordo libero ~1,2 m | scafo in legno o vetroresina **bianco** con **fascia/opera morta azzurra** o **rossa** e antivegetativa rossa sotto la linea d'acqua; **timoniera** bianca a prua-centro (h ~2,3 m sopra il ponte) con vetri, albero con luci e radar; a poppa **portale a A** (gallows) e **tamburo salpareti** (verricello) con rete verde-blu arrotolata; galleggianti arancioni, cassette di plastica, copertoni come parabordi |
| **B — peschereccio piccolo** | 11 × 4,0 m | come A ma con cabina più piccola e solo verricello salpareti a prua; scafo bianco con fascia **verde** |
| **C — gozzo da pesca con tuga** | 8,5 × 2,8 m | gozzo ligure in legno con piccola tuga, falchetta in legno chiaro, scafo bianco con fascia azzurra; può riusare la base di `SM_Morin_Barca_Gozzo` (6,0 × 2,3 m) scalata e con tuga |
Nomi sugli scafi: inventati (§9), niente numeri di matricola reali (si può usare una sigla finta "SP 000").

### 6.3 Posizioni proposte (ormeggio di fianco, prua verso +Y, origine alla linea di galleggiamento come il battello) [S]
| Barca | Centro (X; Y) | Ingombro Y | UE (X, Y, Z) | Yaw UE |
|---|---|---|---|---|
| A 14 m | (13,9; 28,0) | 21 → 35 (lungo il pontiletto) | (1390, −2800, −100) | −90 |
| B 11 m | (12,2; 42,0) | 36,5 → 47,5 (al ciglio, X 9,6) | (1220, −4200, −100) | −90 |
| C 8,5 m | (13,6; 15,0) | 10,8 → 19,2 | (1360, −1500, −100) | −90 |
Fra scafo e ciglio/pontiletto ~0,5 m con copertoni. La C resta 11 m a nord dell'imbocco del ponte (Y 0): la vista sulle antenne
dalla partenza non cambia (barche basse, < 6 m). Budget: ≤ 30k tri come il battello è eccessivo; proposta ≤ 6k (A), ≤ 4k (B), ≤ 2k (C).

---

## 7. Biglietteria, pontile d'imbarco e traghetto (X ≈ 72)

### 7.1 Planimetria [V OSM + S]
- Terminal: `amenity=ferry_terminal` "Terminal Traghetti di La Spezia" in **(71,7; 80,3)**, operatore **Consorzio Marittimo Turistico
  Cinque Terre - Golfo dei Poeti** (sito "navigazionegolfodeipoeti") [V OSM node 1864967381].
- Pontile: way 175935430 da **(71,7; 80,3) a (70,8; 52,0)**, 28,3 m, `surface=wood`, `floating=yes` [V OSM]; l'articolo de La Nazione
  (11-01-2026, già in `banchina.md`) lo descrive su tubi d'acciaio infissi. In T1 sotto il tavolato si vedono **travi d'acciaio e montanti
  tubolari che entrano in acqua**, nessun galleggiante evidente: vale l'articolo [V-foto + V].
- Le **casette e il portale non stanno sul camminamento**: in T1 la loro base è oltre la linea del ciglio, su una **piattaforma di radice**
  raggiunta da una piastra metallica grigia (T1 x 255-355 / y 400-440; T2 x 290-800 / y 565-597) [V-foto]. Piattaforma ≈ **X 67,5 → 76,0,
  Y 77,5 → 80,0** [S]. Il camminamento (Y 80-89) resta libero, come nel modello attuale.

### 7.2 Le casette (2) [V-foto T1, T2; misure S, scala dalla maniglia della porta a ~1,05 m: ~167 px/m in T2]
| Voce | Casetta EST (+X) "biglietteria" | Casetta OVEST (−X) "ufficio" |
|---|---|---|
| Centro | **(74,4; 78,9)** · UE (7440, −7890) | **(69,0; 78,9)** · UE (6900, −7890) |
| Pianta | ~2,2 × 2,3 m | ~2,3 × 2,3 m |
| Altezze | gronda ~2,5 m, colmo ~2,9-3,1 m | uguale |
| Tetto | **a capanna**, colmo **lungo Y** (timpani verso città e verso mare), manto in lamiera grigio-azzurra (#889CB4) con scossalina bruna | uguale |
| Pareti | **righe verticali bianche e blu** (blu **#2A91F4** circa, bianco #D9E1E7); zoccolo **azzurro pieno** (#79C5EA) alto ~0,55-0,65 m; spigoli e cornici blu | uguale |
| Fronte verso città | **sportello** con bancone in legno (~0,55 × 1,0 m, mensola a ~1,05 m) sotto una **tenda a righe** blu-bianche sporgente ~0,6 m; logo e "LINEA 01 GOLFO DELLA SPEZIA" sullo zoccolo | **porta** con maniglia, **bacheca** con cornice (~0,6 × 0,8 m), pannelli azzurri con icone e avvisi; telecamera sotto la gronda |
| Fianco verso il camminamento | pannello azzurro "LINEA 01 GOLFO DELLA SPEZIA" con logo | pannello azzurro con logo |
**Righe:** in T2 il passo è **57 px** (blu ~30 px, bianco ~27 px) su una facciata larga ~365 px: **13 righe** (7 blu e 6 bianche) per lato.
Con la scala della maniglia ogni riga misura **~17-20 cm**; l'utente stimava ~25 cm. Il **numero** di righe è certo, la misura no:
proposta di modellare 13 righe sulla larghezza reale della facciata (= ~17 cm su 2,2 m) e far confermare (domanda D3).

### 7.3 Il portale centrale [V-foto T2]
- Due montanti in tubolare bianco, larghezza utile ~**2,4 m**, sopra un **pannello sagomato** (bordo superiore ad arco) largo ~2,4 m e
  alto ~1,0 m, con cima a **~3,4-3,6 m** [S].
- Fascia blu in alto: "TRASPORTO DI LINEA VIA MARE / FERRY LINES"; sotto, su fondo azzurro: "Biglietteria / Ticket Office";
  a sinistra "LINEA 01 GOLFO DELLA SPEZIA / LINE 01 GULF OF LA SPEZIA"; a destra il **logo della compagnia** (da sostituire, §9).
- Al centro uno **schermo** in cornice bianca, ~**1,2 × 0,8 m** (in T2 trasmette un video con persone: nel gioco grafica inventata).
- Dietro il portale, una **tettoia** con struttura metallica bianca e **mantovana a righe blu-bianche** (T1 x 490-670 / y 235-275) che
  copre il primo tratto del pontile, ~**5-6 m** (Y ≈ 72 → 78), h ~2,6 m [S]. Pennone bianco con bandiere (~8 m) subito dietro il portale,
  ≈ (72,9; 78,0) [S], altri due pali più bassi con bandiere bianche sulla tettoia.

### 7.4 Il cancello bianco con l'onda [V-foto T2]
Un'anta a sbarre verticali bianche (tubolare ~4 cm, passo ~10 cm), ~**1,1 × 1,9 m** [S], con una **decorazione a due onde blu**
a metà altezza (sagome in lamiera, la superiore azzurro-blu più spessa). Si apre verso il pontile, centrata sull'asse X 71,7, a Y ≈ 79,3.
Ai lati del cancello pannelli fissi uguali fino alle casette [S].

### 7.5 Il pontile [V-foto T1, T2]
| Voce | Dato | Stato |
|---|---|---|
| Larghezza del tavolato | **~3,0 m** (T2, alla scala del portale) | [S] |
| Tavolato | doghe **trasversali** in legno grigio-bruno consumato (#59585B), con le teste a vista | [V-foto] |
| Struttura | travi d'acciaio scure lungo i bordi, montanti tubolari in acqua | [V-foto] + articolo [V] |
| Parabordi | **copertoni neri** appesi al bordo, ~ogni 4 m: ~6 visibili sul lato ovest in T1 → ~7 per lato, 14 in tutto [S] | forma [V-foto]; numero [S] |
| Bitte | 3-4 bitte nere basse in testa al pontile (T2 x 585-640) | [V-foto]; posizione [S] |
| Lato ovest | **rete a maglia sciolta** (chain-link) su telaio d'acciaio zincato, h ~1,8 m, sotto la tettoia (Y ~72-78); poi **ringhiera tubolare bianca** h ~1,1 m (T1 x 590-690) | [V-foto]; misure [S] |
| Lato est | libero (lato d'imbarco) | [V-foto] |
| Arredi | un tavolino e una sedia di plastica per il personale, a metà (T2) | [V-foto]; opzionale |

### 7.6 Il traghetto [V-foto T1, T2; misure S]
- Scafo e sovrastrutture **bianchi**; due ponti: ponte principale chiuso da **grandi finestrature scure**, ponte superiore aperto con
  ringhiera bianca; **timoniera** a prua del ponte superiore con vetri scuri e **salvagente** bianco-rosso sul frontale; albero con radar e antenne.
- **Fila di zattere autogonfiabili rosse** (contenitori cilindrici, ~8-10, Ø ~0,6 × 1,2 m) lungo la ringhiera del ponte superiore, verso poppa.
- **Oblò** tondi in fila sullo scafo (indicazione dell'utente [V-utente]; in T1 non si distinguono alla risoluzione della foto).
- Lunghezza: non misurabile dalle foto (vista di sbieco, tagliata); i battelli del golfo stanno sui **25-35 m**. Il nostro 32 m va bene [S].
- Lato d'ormeggio: **est** del pontile nelle foto (§1).

### 7.7 Confronto con gli asset del progetto
| Asset (`docs/uefn_arte.md` §22) | Oggi | Realtà | Cosa cambiare |
|---|---|---|---|
| `SM_Morin_Biglietteria` (3,4 × 2,6 × 3,1 m, 324 tri), posata a (75,8; 77,6) | **un solo** box sulla piattaforma | **2 casette a capanna a righe** + portale con insegna e schermo + cancello con l'onda + tettoia a righe | sostituire con un kit: `SM_Imbarco_Casetta` (2 varianti: sportello/porta, ≤ 1,5k), `SM_Imbarco_Portale` (≤ 1k), `SM_Imbarco_Cancello` (≤ 600, sbarre su card masked), `SM_Imbarco_Tettoia` (≤ 1k), `SM_Imbarco_Rete` (masked, ≤ 200) |
| `SM_Morin_PontileImbarco` (7,1 × 28,6 m, 1.240 tri), X 70,4-77,5 | tavolato largo 7,1 m | tavolato **~3 m** + piattaforma di radice ~8,5 × 2,5 m | restringere il tavolato a 3 m sull'asse OSM (X 71,7 → 70,8), tenere la piattaforma; aggiungere copertoni (~14), bitte di testa (4), rete e ringhiera sul lato ovest |
| `SM_Morin_Battello` (32,0 × 7,54 × 8,27 m, 3.351 tri), a X 66,56 (lato **ovest**) | 2 ponti, scala di poppa | 2 ponti, timoniera con salvagente, **zattere rosse**, oblò, radar | aggiungere zattere rosse, salvagenti, fila di oblò (texture), albero con radar. **Lato d'ormeggio: decide l'utente (D1)**; spostarlo a est (X ≈ 72,9 + 3,8 ≈ 76,9) cambia le verifiche di salita a bordo già fatte |

---

## 8. Ingresso della marina (X ≈ 151)

### 8.1 Dove [V OSM + S]
- Il portale sta sul ciglio (Y 80, OSM coastline) **alla radice della spina** del pontile principale (way 149964057, primo nodo
  **(150,9; 80,1)**). Centro del portale ≈ **(151,0; 81,2)**, fronte verso la città (+Y) [S]. UE **(15100, −8120, 0)**, yaw UE 0
  (il piano del portale è parallelo a X).
- L'**ufficio galleggiante** sta subito dietro il portale, spostato verso **+X** (M2: dietro il cancello, un po' a sinistra; M1: davanti
  alla camera, a sinistra del portale). Centro ≈ **(158; 71)**, ~10 × 6 m [S]. È il nodo OSM **"Assonautica Provinciale A.S.D La Spezia"
  (158,8; 72,9)** [V]. UE (15800, −7100).
- Dal portale una **passerella con ringhiera blu** scende verso −Y al galleggiante della spina; è la nostra `Marina_Passerella_Spina`
  (151,1; 80,03), yaw 90 [V CSV `exports/marina/marina_pontili_v3.csv`]. Nel fondo di M1 si vede il pontile d'imbarco a X 72 con i traghetti.
- **Sostituisce il nostro "Circolo Nautico Vento Contrario"** (`SM_Morin_Marina_Circolo`, centro (161; 72), 16 × 10 × 3,5 m, pareti scure
  e insegna rossa: stime da viste aeree, `marina_blocco1.md` §2): stessa posizione, ma è più piccolo e completamente diverso (§8.2).

### 8.2 Ufficio galleggiante [V-foto M1, M2; misure S]
| Voce | Dato |
|---|---|
| Struttura | scatola su **pontone** scuro (acciaio/cemento, bordo libero ~0,5 m, catene d'ormeggio); pareti alte ~**3,0 m**; tetto piano praticabile con **terrazza**: candelieri inox ogni ~1 m e cavi/corde, h ~1,0 m; una piccola tenda bianca a punta sul tetto |
| Misure | fronte verso il portale (+Y) **~10 m** (rapporto 3:1 con l'altezza in M1); profondità ~6 m [S, non visibile] |
| Rivestimento | **doghe orizzontali in legno** bruno-arancio (teak/iroko, campione **#8D5A35**), ~**12 cm** con fuga scura sottile |
| Insegna sul fronte | logo tondo (blu-rosso con vela) a sinistra e scritta a lettere bianche in rilievo **"ASSONAUTICA"** (h ~0,45 m) con sotto **"La Spezia | Porto A. De Benedetti"** (h ~0,2 m): **da sostituire** (§9) |
| Posizione Z | tetto del pontone a Z ≈ −0,5 (UE −50), pareti fino a +2,5, terrazza fino a +3,5 [S] |

### 8.3 Portale d'ingresso [V-foto M2, M1; scala dalla bitta (~0,7 m) e dal cancello (~2,0 m): ~167 px/m in M2]
| Voce | Dato [S] |
|---|---|
| Telaio | profilati d'acciaio verniciato **blu** (#1B50AB in ombra, #3072C9 in luce), montanti ~0,15-0,20 m; altezza **~3,0 m**, luce fra i montanti ~**2,2 m** |
| Architrave | pannello blu ~1,9 × 0,7 m con lettere **in rilievo argento** "ASSONAUTICA" (da sostituire) |
| Cancello | **due ante** ~1,0 × 2,0 m: parte alta a **sbarre verticali**, parte bassa a **pannello pieno** (~0,8 m) con un **emblema tondo** (Ø ~0,5 m, da sostituire con un emblema inventato) |
| Pilastro +X | ~0,4 × 2,4 m, scritta verticale "PORTO TURISTICO ALBERTO DE BENEDETTI" (da sostituire); dietro, verso il mare, un **pannello espositivo** blu con una foto d'epoca in bianco e nero (due donne in abiti antichi sugli scogli): nel gioco una foto d'epoca generica o un'immagine inventata |
| Pilastro −X | ~0,6 × 2,4 m con **lettore di badge**, citofono, cartello giallo "area videosorvegliata" (generico: si può tenere), e un pannello laterale blu verso il mare |
| Passerella | ringhiera **blu** a 3 correnti orizzontali, h ~1,1 m, su passerella metallica; il galleggiante della spina ha un bordo in legno |

### 8.4 Bitta in ghisa arrugginita [V-foto M2]
Sul ciglio a **−X** del portale, ≈ **(147,5; 80,4)** [S], UE (14750, −8040, 0). Bitta **a colonna** (fusto cilindrico Ø ~0,30 m con anello
più largo in cima e collare a metà), h **~0,70 m**, ruggine **#8C6347** con resti di vernice rossa e nera. Diversa dalle bitte "a fungo"
nere della banchina (0,45 m, `banchina.md`): serve una variante `SM_Banchina_Bitta_Colonna` (≤ 500 tri), anche solo in questo punto.

---

## 9. Nomi delle attività private: parodie proposte
Regola dell'utente (`docs/decisioni.md`, 2026-11-20): attività commerciali con nome parodia scherzoso, nomi pubblici reali si tengono.
| Reale (solo riferimento) | Dove | Proposta | Alternative |
|---|---|---|---|
| "dai pescatori" (gastronomia, scudo bordeaux sull'arco di A1) | A1 | **"DAI PESCATORI PIGRI"** (scudo con un polpo che dorme in un'amaca) | "Dai Pescatori Sbadati" |
| "Consorzio Pescatori — Sapori di Mare e di Terra" (pannello sopra A2) | A2 | **"CONSORZIO RETI BUCATE — Sapori di Mare e di Tèra"** | "Consorzio Pescatori Pigri" |
| "Risto Pescheria — o mangi o porti via" (cavalletto) | cavalletto | **"RISTO LISCHERIA"** (lisca = spina di pesce); i motti generici "o mangi o porti via / scegli il pesce / scegli la cottura" possono restare | "Pesce & Basta" |
| "Mitili & Mitili" (OSM, ristorante C) | C | già **"AL MUSCOLO STANCO"** (fatto) | — |
| "Navigazione Golfo dei Poeti" (compagnia di navigazione: logo sul portale e sulle casette) | imbarco | **"NAVIGAZIONE GOLFO DEI POETASTRI"** (logo: un gabbiano con la penna d'oca su un'onda); sullo schermo "Enjoy the mugugno" | "Navigazione Rima Baciata", "Navigazione Golfo dei Mugugni" |
| "Assonautica (Provinciale) La Spezia" (associazione/circolo con concessione) | ufficio, portale | **"ASSONNAUTICA"** (assonnata: logo tondo con una vela che sbadiglia) | "Assonautica dei Pigri" |
| "Porto (Turistico) A. De Benedetti" / "Porto Turistico Alberto De Benedetti" | ufficio, pilastro del portale | **"Porto Turistico Vento Contrario"**: unifica con il circolo già inventato (`CREDITS.md`) e non usa il nome di una persona reale | — |
| nomi dei pescherecci | §6 | "MUGUGNO II", "ACCIUGA FELICE", "NON CE N'È" (in stile con le barche della marina) | — |
**Restano come sono (pubblici):** "banchina Costantino Morin", "banchina G. Thaon di Revel", l'avviso "ATTENZIONE — I bambini devono
essere accompagnati per mano lungo la banchina", "La Sirena del Golfo dei Poeti" (opera pubblica), "Biglietteria / Ticket Office",
"TRASPORTO DI LINEA VIA MARE / FERRY LINES", "LINEA 01 GOLFO DELLA SPEZIA" (descrizione della linea, senza marchio [S]),
nomi di località sulle destinazioni (Portovenere, Lerici, Cinque Terre), il cartello generico di videosorveglianza, lo stemma comunale sul cestino.

---

## 10. Texture: porzioni utilizzabili come base [SV] (ritagliare, raddrizzare, de-lighting; pixel nell'immagine originale)
Regole: niente persone, targhe, loghi o nomi privati, UI di Street View (elenco in testa alla scheda). Ogni texture derivata va in
`docs/CREDITS.md` con la marca [SV] e la foto sorgente; l'utente le ricontrolla prima della pubblicazione.
| Texture proposta | Foto e porzione (x, y) | Note |
|---|---|---|
| `T_Imbarco_Casetta_Righe_D` (1024) | **T2** casetta ovest, righe sopra i pannelli: x 800-1110, y 120-235 e x 800-1160, y 390-490 (escludere la maniglia x 915-945 e la telecamera x 1110-1140); casetta est x 30-200, y 300-460 | raddrizzare; ricostruire il modulo a righe tileable con il passo misurato (13 righe per facciata) |
| `T_Imbarco_Casetta_Zoccolo_D` | **T2** x 805-1160, y 495-585 (azzurro pieno, senza scritte) | |
| `T_Imbarco_Tenda_Righe_D` | **T2** x 0-290, y 200-290 (tenda dello sportello); **T1** x 490-670, y 235-275 (mantovana della tettoia) | |
| Tetto in lamiera + scossalina | **T2** x 780-1160, y 95-175 | |
| `T_Imbarco_Legno_v2_D` (tavolato del pontile) | **T2** x 560-660, y 450-560 (evitare tavolino e sedia x 665-760) | doghe trasversali consumate |
| Cancello con l'onda | **T2** x 375-535, y 215-525 | solo riferimento: sbarre e onde si ricostruiscono in vettoriale (card masked) |
| Rete chain-link | **T1** x 490-585, y 270-440 | ricostruire la maglia con alfa; la foto dà colore e passo |
| Fianco del pontile con copertoni | **T1** x 590-975, y 320-450 | riferimento per travi e copertoni |
| Scafo e zattere del traghetto | **T1** x 590-885, y 215-330 (zattere x 820-885, y 255-275) | solo tinta e disposizione; nessun nome visibile |
| Lastre della banchina e ciglio | **T1** x 100-330, y 430-584 (evitare la scritta di UI x 0-100); ciglio x 400-700, y 470-584 | confronto con `MI_Pav_Lastre` |
| `T_Marina_Ufficio_Doghe_D/N` (2048) | **M1** doghe: x 160-700, y 300-365 (sotto la scritta) e y 195-215 (sopra); colonna x 650-700, y 195-365. Escludere logo x 255-340 / y 220-295 e scritte x 355-645 / y 225-280 | doghe orizzontali ~12 cm |
| Pontone dell'ufficio | **M1** x 165-700, y 365-395 | |
| `T_Marina_Portale_Blu_D` | **M2** solo la tinta e l'usura (lamiera blu x 355-680, y 45-60; montante x 685-700, y 300-400); il resto ha scritte, persona o emblema | colore procedurale #1B50AB-#3072C9 con graffi |
| Ringhiera blu della passerella | **M1** x 760-1015, y 270-360 | tinta #7797B7 in controluce: usare il blu del portale |
| `T_Banchina_Bitta_Ruggine_D` | **M2** x 955-1025, y 380-505 | ottima base per la ruggine |
| Lastre del ciglio della marina | **M2** x 820-1240, y 450-599; **M1** x 900-1372, y 420-502 | |
| `T_Molo_Fioriera_v2_D` | **R2** x 575-760, y 315-365 (fianchi delle fioriere) | antracite #222B35 |
| Arbusti delle fioriere (card) | **R2** x 490-790, y 215-330 | come in `radice_molo.md` §8 |
| Telo dell'ombrellone | **R2** x 720-1100, y 70-130 (sotto del telo, in ombra) | aggiungere il lato in luce procedurale |
| Masselli davanti ai ristoranti | **R2** x 330-460 e x 800-1040, y 420-519 (evitare cerchio di UI x 460-800 e carrello x 1040-1150) | confronto con `T_Molo_Masselli` |
| Intonaco giallo A1 / rosa A2 | **R2** x 1015-1100, y 150-220 (senza scudo x 875-1010) / x 590-640, y 120-180 (senza pannello x 640-745) | già coperti da `radice_molo.md` §8: solo controllo tinta |
| `T_Morin_Cestino_v2_D` (512) | **K** x 40-125, y 15-175 (corpo e fascia con lo stemma) | pochi pixel: usarla come base e ripulirla, ricostruire la fascia in rilievo come normal |
| `T_Morin_NJPlastica_D` (512) | **G** x 20-100, y 225-290 (blu); bianco procedurale | |
| Pannello dei cartelli | **G** x 40-90, y 45-150: solo impaginazione | ricostruire testo e pittogramma in vettoriale (§4.2) |
| `T_Molo_Sirena_Basamento_D` | **S** x 110-360, y 270-405 | pietra bocciardata #979089; la figura in bronzo è stilizzata (niente texture dalla statua) |

---

## 11. Tabella riassuntiva delle posizioni (progetto e UE)
| Elemento | Progetto (X; Y; Z) | UE (X, Y, Z) | Yaw UE | Stato |
|---|---|---|---|---|
| Ombrellone grande A1 | (2,6; 103,7; 0) | (260, −10370, 0) | 0 | [S] |
| Fila fioriere A2 | X 3,3, Y 99,7-102,1 | (330, −9970…−10210, 0) | 90 (lato lungo lungo Y) | [S] |
| Cavalletto "Risto Lischeria" | (5,1; 100,4; 0) | (510, −10040, 0) | ~−30 | [S] |
| Lavagna | (5,7; 92,8; 0) | (570, −9280, 0) | ~−20 | [S] |
| Fascia dehors A1-A4 | X facciata → 4,2, Y 62 → 108 | X 30…420, Y −6200…−10800 | — | [S] |
| Cestini (9, mesh nuova) | Y 92,1; X 18,55 … 234,55 (§3.2) | Y −9210, Z 15 | 0 | [V] CSV |
| Cestini OSM | (18,0; 91,3), (41,9; 92,4) | (1800, −9130), (4190, −9240) | — | [V] OSM |
| Palo dei cartelli | (19,2; 81,1; 0) | (1920, −8110, 0) | pannello rivolto verso +X/+Y [S] | [S] calcolo F1 |
| New jersey plastica 1-2 | (20,4; 80,35), (21,7; 80,35) | (2040, −8035), (2170, −8035) | 0 | [S] |
| New jersey plastica 3-4 | (17,6; 79,3), (16,5; 78,2) | (1760, −7930), (1650, −7820) | −45,3 | [S] |
| Sirena | (13,8; 91,9; 0,15) | (1380, −9190, 15) | ~190 | [V] OSM pos.; orient. [S] |
| Peschereccio A 14 m | (13,9; 28,0; −1,0) | (1390, −2800, −100) | −90 | [S] |
| Peschereccio B 11 m | (12,2; 42,0; −1,0) | (1220, −4200, −100) | −90 | [S] |
| Gozzo da pesca C 8,5 m | (13,6; 15,0; −1,0) | (1360, −1500, −100) | −90 | [S] |
| Portale biglietteria | (71,7; 79,3; 0) | (7170, −7930, 0) | 0 | asse [V] OSM; Y [S] |
| Casetta est (sportello) | (74,4; 78,9; 0) | (7440, −7890, 0) | 0 | [S] |
| Casetta ovest (porta) | (69,0; 78,9; 0) | (6900, −7890, 0) | 0 | [S] |
| Tettoia + rete | X 70,2-73,2, Y 72-78 | X 7020-7320, Y −7200…−7800 | 0 | [S] |
| Pennone | (72,9; 78,0) | (7290, −7800) | — | [S] |
| Pontile (asse OSM) | (71,7; 80,3) → (70,8; 52,0) | (7170, −8030) → (7080, −5200) | ≈ 91,8 (radice → testa) | [V] OSM |
| Portale della marina | (151,0; 81,2; 0) | (15100, −8120, 0) | 0 | [S] |
| Ufficio galleggiante | (158; 71; −0,5) | (15800, −7100, −50) | 0 | [S]; nodo OSM (158,8; 72,9) [V] |
| Bitta arrugginita | (147,5; 80,4; 0) | (14750, −8040, 0) | — | [S] |

---

## 12. Domande per l'utente
- **D1. Traghetto:** nelle foto T1/T2 è ormeggiato sul lato **est** del pontile e la rete/ringhiera sta a ovest; nel gioco è a **ovest**.
  Lo spostiamo a est (rifacendo le verifiche di salita a bordo) o lo lasciamo dov'è?
- **D2. Cartelli e new jersey:** confermi il palo sullo spigolo dove il camminamento incontra il molo (~(19; 81)) e quante barriere blu/bianche
  ci sono (proposta: 4, due lungo il ciglio e due sullo smusso)? Che cosa c'è scritto sulla targhetta gialla in basso?
- **D3. Righe delle casette:** dalla foto risultano 13 righe per facciata, ~17-20 cm ciascuna. Va bene, o preferisci 25 cm (righe meno fitte)?
- **D4. Ufficio della marina:** una foto del lato verso il mare o dall'alto (profondità, porte, finestre, terrazza).
- **D5. Pescherecci:** se hai una foto delle barche lungo il molo davanti al ristorante C, possiamo copiarne colori e attrezzature.
- **D6. Sirena:** verso dove guarda (la strada o il bacino)?

---

## 13. Inizio della passeggiata: Sirena, lampione e prime palme (foto aggiunte in serata, 2026-11-20)

Segnalazione dell'utente [V-utente]: "la passeggiata inizia con un po' di marciapiede dove c'è poi la statua e solo dopo inizia la palma,
in corrispondenza della statua un palo della luce e poi dietro iniziano le coppie di palme. […] 68×2 palme."
Conclusioni e layout corretto: **`ref/palme.md` §6** (qui solo l'analisi delle foto).

| Sigla | File | Px | Cosa |
|---|---|---|---|
| S1 | `ref/foto/vista/vista__statua.png` | 1161 × 571 | dall'angolo in cubetti verso il bacino: Sirena, cestino, palo "accesso autorizzati / area pedonale", prima palma, bici; palo del lampione in primo piano a sinistra |
| S2 | `ref/foto/vista/vista__statua2.png` | 833 × 580 | dall'incrocio di Viale Italia (strisce pedonali in basso): pini e prime palme a sinistra, lampione a 2 globi con cartelli al centro, Sirena, dehors e strada di servizio a destra |
| S3 | `ref/foto/vista/vista_inizio_passeggiata.png` | 1371 × 652 | dal lato città verso il mare: lampione a 2 globi sovrapposti con manifesto su riquadro di pietra, prime palme nelle aiuole quadrate, cestini, new jersey, ristoranti a destra |

**Da NON copiare nelle texture:** scritte "© 2025 Google" (S1 x 740-810 / y 180-195; S2 x 480-570 / y 270-285), etichetta di Street View
"Banchina Thaon di Revel" sull'asfalto (S1 x 800-1161 / y 380-571: **non è una scritta reale**), freccia di navigazione (S3 x 1090-1280 / y 540-585),
riquadro della mappa (S3 x 0-150 / y 635-652), persone (S1 x 355-445 / y 310-360 e x 990-1040 / y 340-380; S3 x 45-80 / y 385-445),
auto con targa (S2 x 0-235 / y 420-500; S3 x 750-800 / y 400-445), manifesto "Jurassic" (S3 x 795-860 / y 400-490).

### 13.1 Punti di presa e metodo [S]
Camera a ~2,5 m, orizzonte e scala dalla posizione OSM di oggetti noti. Precisione ±1,5 m in pianta.
| Foto | Punto (X; Y) | Direzione | Riferimenti usati |
|---|---|---|---|
| S1 | **(14,9; 102,6)** | verso −Y, ruotata ~19° verso +X | Sirena (13,8; 91,9) e cestino (18,0; 91,3) da OSM: la distanza fra i due ricavata dalla foto (4,21 m) coincide con OSM (4,24 m) |
| S2 | sulla corsia di Viale Italia, X ≈ 10-15, Y ≈ 125-135 | verso −Y | strisce pedonali OSM (way 1486816241, X 15,4) a sinistra, strada di servizio a destra. Solo lettura qualitativa: l'ordine degli oggetti |
| S3 | **(16,2; 108)** | verso −Y | coppia di palme allineata (filari a 7,0 m, OSM), cestino OSM (18,0; 91,3) ritrovato a (16,2; 92,9) |

### 13.2 Cosa si vede e dove sta
| Oggetto | Foto | Posizione ricavata | Confronto | Stato |
|---|---|---|---|---|
| Nessuna palma fra la strada e la prima coppia | S1, S3 | — | il gioco ha una coppia a X 12 | [V-foto] |
| Prima palma del filare 1 (tronco con luminarie, cartello e bici accanto) | S1 x 490 | **(20,6; 91,4)** | OSM inizio filare (20,4; 92,9) | [V-foto] / [S] posizione |
| Prima coppia (filare 2 davanti, filare 1 dietro, quasi in linea) | S3 x 400 e x 600 | X ≈ 20 ± 1,5; distanza in profondità ≈ 6,6 m (filari a 7,0 m) | OSM X 20,4 per entrambi i filari | [V-foto] |
| Sirena sul basamento grigio, a ~1 m dal bordo dell'asfalto | S1 x 790-900; S2 x 525 | usata come riferimento (OSM) | gioco (13,8; 91,9): giusto | [V] OSM + [V-foto] |
| Cestino a capsula | S1 x 612; S3 x 685 | (16,2-18,0; 91,3-92,9) | OSM (18,0; 91,3) | [V] |
| **Lampione a 2 globi sovrapposti** (globo alto e globo basso sullo stesso fusto, cima ~6 m, base su riquadro di pietra chiara ~0,9 m, manifesti incollati sul fusto) | S3 x 830 (base y 590); S1 palo in primo piano x 30-100 con l'ombra del globo a terra (x 190-260, y 520-555); S2 x 435 | **(15,3; 101,9) ± 1,5** (S3: (14,5; 101,4); S1: (16,2; 101,9)) | gioco `Arte_Molo_Lampione2Globi_00` (13,0; 106,0) da F1 2023 | posizione [S]; tipo [V-foto] |
| Palo "accesso autorizzati / area pedonale" (cerchio rosso + pannello con pedone blu) | S1 x 530; S2 x 470 | ≈ (18,4-19,7; 91,4-92,5), a ridosso dell'aiuola della prima palma | non c'è nel gioco | [S] |
| Lampione a 2 globi su bracci, accanto a una panchina, lato mare | S3 x 255 (panchina x 280-330) | X ≈ 31-32 | OSM panchina (31,7; 92,8); gioco Lampione_00 a 16,8 | [S] |
| Dissuasore cilindrico grigio, new jersey bianchi e blu sul ciglio, auto parcheggiata | S3 x 650-900 / y 420-485 | ciglio Y ≈ 80-83, X ≈ 12-25 | new jersey già in §4.3 | [V-foto] |
| Aiuole quadrate bordate di pietra chiara, terra scura | S3 x 270-530 / y 520-590 | lato ~3,5 m | gioco 3,6 × 3,0 | [S] |

### 13.3 Domande per l'utente
- **D-P1. Gazebo:** OSM lo mette dopo **tre** coppie di palme (X ≈ 40, fra la 3ª e la 4ª), la tua indicazione del 2026-11-19 dopo **due**
  (X ≈ 32, dove OSM ha una panchina con schienale). Con il passo giusto (8 m) quale vale? Proposta: X 40,4 (OSM).
- **D-P2. Lampione a 2 globi sovrapposti:** dalle foto nuove sta all'altezza della Sirena ma **sul filo del filare lato città** (Y ≈ 102,
  ~3 m prima della prima palma); nel gioco è 4 m più verso Viale Italia (Y 106). Confermi lo spostamento?
- **D-P3.** Il palo con "accesso autorizzati / area pedonale" accanto alla prima palma lo vogliamo nel gioco (cartello pubblico, testo generico)?
