# Marina del Blocco 1: pontili e barche (porto turistico Assonautica)

Scheda di geo-scout, 2026-11-20. Richiesta dell'utente: "c'è da fare al blocco uno il pontile con le barchette".
Legenda: **[V]** verificato (fonte citata) · **[S]** stima motivata, da confermare · **[F]** letto da una foto in `ref/foto/`.
Coordinate di progetto in metri: origine all'imbocco del ponte, X lungo la passeggiata verso NE, Y verso la città (il mare è a Y < 80).
Conversione in UE: (X·100, −Y·100, Z·100). Proiezione e assi come in `ref/area.md` §2.
Dati OSM: `ref/osm/morin_bbox.osm` e `ref/osm/morin_blocchi23.osm`, © OpenStreetMap contributors (ODbL).
Generatore riproducibile dei CSV: `exports/marina/gen_marina_v1.py` (seed fisso; si lancia con un Python 3 qualsiasi, nessuna dipendenza).

---

## 1. Fonti usate

| Fonte | Cosa se ne ricava |
|---|---|
| OSM, 16 way `man_made=pier` fra X 75 e 316 | geometria di tutti i pontili [V]. Nessun pontile ha i tag `width` o `floating`, tranne quello d'imbarco (già fatto) |
| OSM node 4685390142 `leisure=marina` "La Spezia Porto Turistico Assonautica Marina" (X 200,6, Y 0,2) | nome e natura dell'impianto [V] |
| OSM node 10844624351 "Assonautica Provinciale A.S.D La Spezia" (X 159,0, Y 72,9) | sede del circolo alla radice del pontile principale [V] |
| OSM ferry 42145971 e 1188647917 | rotte dei battelli (schematiche) che passano a ovest della marina: lì niente barche |
| [F] `vista/vista_dall_alto.png` (vista aerea zenitale, ~6,4 px/m) | larghezze, lunghezze delle barche, ormeggio perpendicolare, densità |
| [F] `vista/vista_dall_alto_2.png` (vista aerea obliqua, prospettiva: gli angoli non si misurano) | densità, colori, circolo bianco sulla radice della spina |
| [F] `vista/banchina_vista_montagne_verso_ponte.jpg` (dal ciglio a X ~280 verso SO) | barche aperte con teli blu, molti alberi di barche a vela, circolo con pareti scure |
| [F] `vista/vista montagne.jpg` (foto stock Alamy, solo riferimento visivo) | barchini aperti vicino al pontile NE, circolo scuro con insegna |
| [F] `ponte/ponte_verso_passegiata.png`, `ponte/ponte1.png` | dal ponte: tendalini blu, scafi bianchi e blu, piccole vele, alberi in fila |
| [F] `vista/parcheggio_iniziale.png`, `vista/inizio_passegiata_*` | la marina vista da terra: alberi delle barche a vela oltre il battello |

Le foto Google (aeree, Street View) sono solo riferimento visivo: nessuna geometria è stata ricavata da esse, solo stime di misura.

---

## 2. Geometria dei pontili (OSM, coordinate di progetto)

Ciglio della banchina: Y_q(X) = 80,27 − 0,00217·(X − 44) [V, dalle scalette v2]. Tutti i pontili radicati al ciglio partono da Y ≈ 80.

### 2.1 Pontile principale ("spina") e fingers, OSM way 149964057 [V]
| Tratto | Polilinea (X, Y) | Lunghezza |
|---|---|---|
| Spina, tratto dritto | (151,1; 80,1) → (151,6; 62,8) → (151,4; 43,2) → (151,2; 17,6) → (150,9; −11,7) → (150,7; −40,6) → (150,4; −66,9) → (150,3; −86,0) | 166 m |
| Spina, gomito verso SE | (150,3; −86,0) → (165,1; −101,1) → (195,5; −132,0) | 65 m |
| Spina, tratto finale | (195,5; −132,0) → (197,1; −176,6) | 45 m |
| Pontile esterno (coda della stessa way) | (197,1; −176,6) → (295,5; −174,4) | 98 m |
| **Totale way 149964057** | | **373,7 m** |

I fingers sono pontili secondari interi (non i piccoli "finger" da un posto barca): partono dalla spina verso +X e finiscono a X ≈ 260.

| Finger | OSM way | Radice → punta | Lunghezza | Distanza dal precedente |
|---|---|---|---|---|
| F1 | 149964075 | (151,6; 62,8) → (261,9; 62,9) | 110,3 m | 17,2 m dal ciglio |
| F2 | 149964059 | (151,4; 43,2) → (261,6; 41,8) | 110,2 m | 20,4 m |
| F3 | 149964070 | (151,2; 17,6) → (260,4; 17,0) | 109,2 m | 24,7 m |
| F4 | 149964102 | (150,9; −11,7) → (260,5; −10,8) | 109,5 m | 28,6 m |
| F5 | 149964068 | (150,7; −40,6) → (259,4; −38,9) | 108,7 m | 28,5 m |
| F6 | 149964079 | (150,4; −66,9) → (260,8; −69,1) | 110,4 m | 28,3 m |
| F7 | 149964062 | (165,1; −101,1) → (261,4; −99,9) | 96,3 m | 32,0 m |
| F8 | 149964065 | (195,5; −132,0) → (260,8; −131,0) | 65,3 m | 31,2 m (e 44 m dal pontile esterno) |

Lo specchio fra due fingers cresce verso il largo (17 → 32 m): vicino alla banchina stanno le barche piccole, al largo quelle grandi.
È la regola usata per il layout (§4).

### 2.2 Altri pontili della marina [V]
| Pontile | OSM way | Polilinea | Lunghezza | Note |
|---|---|---|---|---|
| Pontile a L, gamba | 175935435 | (105,4; 80,3) → (106,3; 62,3) → (106,7; 29,6) | 50,7 m | barche piccole ai due lati [F] |
| Pontile a L, testa | 175935435 | (106,7; 29,6) → (89,4; 29,5) | 17,3 m | la punta ovest è a X 89,4: confina con la zona del battello. Barche a vela sul lato sud [F] |
| Pontile a L, ramo | 529818282 | (106,3; 62,3) → (88,9; 61,6) | 17,4 m | barche piccole ai due lati [F] |
| Pontile largo | 175935434 | (126,9; 80,2) → (127,1; 45,5) | 34,7 m | **più largo degli altri, ~5 m [F]**, senza barche ormeggiate nelle viste aeree [F] |
| Pontile NE | 175935432 | (289,6; 79,8) → (291,7; −6,5) | 86,3 m | barche ai due lati (`ref/blocco2.md` §4.2) |
| Pontile esterno 2 | 175935436 | (197,1; −176,6) → (196,0; −213,1) → (213,9; −229,7) → (316,4; −228,6) | 163,5 m | in parte fuori dal box del Blocco 1 (Y < −215, X > 300): solo fondale |

Esclusi: pontile d'imbarco 175935430 (X 71,8, già modellato), pontile 912795089 (X 90, Y −114…−163: è dentro l'area militare
`landuse=military` 224920367, non è della marina), i pontili di Mirabello (già fatti) e quelli a Y < −300.

### 2.3 Larghezza, tipo, quote
| Voce | Valore | Stato |
|---|---|---|
| Larghezza della spina | ~3 m (≈ 20 px nella vista zenitale) | [S] da [F] `vista_dall_alto.png` |
| Larghezza dei fingers e del pontile a L | 2,5-3 m | [S] da [F] |
| Larghezza del pontile largo (X 127) | ~5 m | [S] da [F] |
| Tipo | spina, fingers, pontile a L e NE **galleggianti** (moduli in cemento/legno, tavolato scuro sui fingers, spina più chiara); pontile largo forse **fisso** su pali | [S]: OSM non ha `floating=yes`; tipico delle marine del golfo |
| Piano di calpestio dei galleggianti | Z −0,45 (0,58 m sull'acqua), come a Mirabello | [S] coerente con `docs/decisioni.md` 2026-11-20 |
| Collegamento a terra | passerella incernierata ~3,5 m dal ciglio (Z 0) al galleggiante (Z −0,45), pendenza ~7° | [S]: non si vede nelle foto |
| Colonnine acqua/luce | non risolvibili nelle foto; standard nelle marine: 1 ogni 2 posti barca, ~1 m, bianche | [S]. Il modulo `SM_Mirabello_Pontile` le ha già (centrali, ogni 10 m) |
| Gallocce/anelli | sui bordi, ~1 ogni posto barca | [S]. Già nel modulo Mirabello (ogni 5 m) |
| Circolo nautico (sede Assonautica) | sulla radice della spina, lato est, X ~152-170, Y ~64-80; 1 piano (~3,5 m), pareti scure (bruno/nero) con insegna rossa, tetto piano chiaro | posizione [V] OSM node; forma e colori [F] `vista_dall_alto*`, `vista montagne.jpg`; misure [S] |

---

## 3. Le barche: cosa si vede nelle foto

| Voce | Osservazione | Stato |
|---|---|---|
| Ormeggio | **perpendicolare al pontile**, alla mediterranea (cima di poppa al pontile, trappa a prua sul corpo morto), su entrambi i lati di ogni finger. Nessun finger a posto singolo | [F] viste aeree; tipo di ormeggio [S] (standard in Liguria) |
| Verso | in maggioranza **di poppa** al pontile (prua verso lo specchio d'acqua); i barchini spesso di prua | [S]: dall'alto la prua non sempre si distingue |
| Passo | ~larghezza della barca + 0,7 m (2,9-4,7 m) | [S] |
| Densità | quasi piena: ~85-90 % dei posti occupati sui fingers, meno sul lato ovest della spina (~50 %) | [F] |
| Taglie | pontile a L: 4-7 m (barchini, gozzi, gommoni), 9-11 m le vele sulla testa; fingers interni 5-8 m; fingers esterni e pontile esterno 9-13 m; lato ovest della spina barche grandi sparse (11-13 m) | [F] misure da `vista_dall_alto.png` (barche lunghe 25-80 px a ~6,4 px/m) |
| Tipi | barche a motore aperte e cabinati (la maggioranza), gozzi liguri, gommoni, barche a vela 8-12 m (molti alberi visibili da terra e dal ponte), qualche motoryacht 12-15 m | [F] |
| Colori | scafi **bianchi** quasi tutti; ~10-15 % blu scuro; gozzi bianchi con fascia azzurra/verde/rossa o in legno; **teli e tendalini blu** molto frequenti, qualche beige; gommoni con tubolari grigi o neri | [F] `banchina_vista_montagne_verso_ponte.jpg`, `ponte_verso_passegiata.png` |
| Dettagli | parabordi bianchi/blu, fuoribordo bianchi o neri, capottine blu, randa raccolta sotto il copriranda blu | [F]/[S] |

---

## 4. Layout di riempimento (v1)

Regole applicate dal generatore:
- Lunghezza massima per lato in base allo specchio d'acqua: (distanza fra pontili − 3 m di pontile − 2 × 0,4 m di distacco − corridoio
  di manovra ≥ 4,4 m) / 2. Corridoio minimo che resta: 4,4 m fra F1 e F2 (barche ≤ 6 m), 7-14 m al largo.
- Distacco poppa-bordo pontile 0,4 m (+ variazione −0,15…+0,25 m), passo = larghezza + 0,7 m, imbardata ±2°.
- Posti vuoti casuali: 15 % sui fingers, 20-30 % sui pontili esterni, 50 % sul lato ovest della spina.
- 30 % di gozzi e gommoni ormeggiati di prua (variante con suffisso `_prua`).
- Zone lasciate libere (nessuna sagoma di barca le tocca):
  - zona del battello e del pontile d'imbarco: X 55-90, Y −120…82;
  - specchio davanti alle scalette X 92, 140, 188 (e 300 del Blocco 2): ±4 m in X, da Y 66 al ciglio;
  - sede del circolo: X 151,5-171, Y 64-82;
  - corridoio di 12 m attorno alle due rotte dei battelli OSM (ovest della spina);
  - i pontili stessi.
- Varchi d'accesso: le radici dei pontili (passerelle) restano libere: le barche partono da ~3 m dalla spina e dal ciglio.

| Specchio | Lmax lato | Miscela usata |
|---|---|---|
| ciglio–F1 (17 m) e F1–F2 (20 m), pontile a L | 6 m | gommoni 45 %, gozzi 55 % |
| F2–F3 (25 m), lato est del pontile a L, lato est del pontile NE | 7,5 m | gommoni 20, gozzi 35, motoscafi 45 % |
| F3–F6 (28-29 m), lato nord di F8 | 9 m | gommoni 8, gozzi 12, motoscafi 50, vela 9 m 30 % |
| F6–F8 (31-32 m), lato ovest del pontile NE, gomito della spina | 10-11 m | gozzi 5, motoscafi 40, vela 9 m 25, vela 11 m 30 % |
| testa del pontile a L (lato sud) | 11 m | vela 9 m 50, vela 11 m 50 % |
| F8–pontile esterno (44 m), pontile esterno, pontili esterni 2, lato ovest della spina | 13,2 m | motoscafi 15, vela 11 m 30, yacht 13 m 55 % |

### 4.1 Risultato (`exports/marina/marina_barche_v1.csv`, 475 barche)
| Zona | Barche |
|---|---|
| Pontile a L (gamba, testa, ramo) | 22 |
| F1 / F2 / F3 / F4 / F5 / F6 / F7 / F8 | 48 / 52 / 53 / 48 / 47 / 52 / 33 / 24 (totale 357) |
| Pontile esterno (nord e sud) + pontile esterno 2 (nord) | 26 + 14 |
| Lato ovest della spina (dritto, gomito, tratto finale) | 25 |
| Pontile NE (ovest 18, est 13) | 31 |

| Tipo | Asset | Misure (L × B) | N. | % |
|---|---|---|---|---|
| Motoscafo / cabinato | `SM_Morin_Barca_Motoscafo` (nuovo) | 7,5 × 2,7 m | 159 | 33 % |
| Gozzo ligure | `SM_Morin_Barca_Gozzo` (nuovo) | 6,0 × 2,3 m | 103 | 22 % |
| Gommone | `SM_Morin_Barca_Gommone` (nuovo) | 5,0 × 2,2 m | 70 | 15 % |
| Vela 9 m | `SM_Morin_Barca_Vela9` (nuovo) | 9,0 × 3,0 m | 70 | 15 % |
| Vela 11 m | `SM_Mirabello_YachtB_v2` (esistente) | 11,0 × 3,6 m | 40 | 8 % |
| Motoryacht 12,5-13 m | `SM_Mirabello_YachtA` (esistente) | 13,2 × 4,0 m | 33 | 7 % |

Per categoria: **motore 6-9 m 55 %, vela 9-11 m 23 %, gommoni 15 %, yacht 12-13 m 7 %** (proposta iniziale: 50/25/15/10).
Gli yacht sono meno del 10 % perché sopra i 12 m c'è posto solo al largo (specchi ≥ 44 m) e sul lato ovest della spina.
49 barche (gozzi e gommoni) sono ormeggiate di prua.

Varianti di colore nel CSV (colonna `variante`): Motoscafo `Bianco_TelaBlu` 77, `Bianco` 43, `Blu` 22, `Bianco_TelaBeige` 17 ·
Gozzo `Bianco_FasciaAzzurra` 35, `Bianco_FasciaVerde` 27, `Legno` 15, `Azzurro` 14, `Bianco_FasciaRossa` 12 ·
Gommone `Tubolari_Grigio` 31, `Tubolari_Nero` 29, `Tubolari_Rosso` 10 · Vela9 `Bianco_CoprirandaBlu` 37, `Bianco` 24, `Blu` 9 ·
YachtA e YachtB_v2 `base` (esiste una sola versione). Le varianti si fanno con material instance o con atlanti diversi, a scelta di blender-artist.

Estensione delle barche: X 93,7…311,7, Y −223,5…74,3. Una ventina (pontile esterno 2, lato est del pontile NE) cade appena fuori dal
box del Blocco 1 (X > 300 o Y < −215): sono fondale, si possono togliere senza danno.

---

## 5. I CSV

Colonne: `asset,nome,x,y,z,yaw,pitch,roll,variante`, in uu, gradi, yaw UE (= −rotZ di Blender), come gli altri CSV di posa.

### 5.1 `exports/marina/marina_pontili_v1.csv` (73 righe)
- Origine di ogni modulo alla **radice, sul piano di calpestio**, +X locale verso la punta (convenzione di `SM_Mirabello_Pontile`,
  `blender/scripts/morin_mirabello.py`). Z −45 (calpestio a −0,45 m).
- Ogni tratto è coperto da moduli da 48 m (`SM_Mirabello_Pontile`, 22 righe) e poi da moduli da 12 m (`SM_Morin_Marina_Pontile12`,
  46 righe, **nuovo**). Quando 12 m sono troppi, l'ultimo modulo è arretrato fino a finire sulla punta e sovrapposto al precedente:
  quelle 18 righe hanno **Z −46** (1 cm più basso, niente z-fighting). Scarto massimo in punta 0,6 m.
- Ripiego finché `Pontile12` non esiste: `SM_Mirabello_Pontile` con **scala X 0,25** (variante `nuovo_fallback_...`). Le colonnine e
  le gallocce si schiacciano, ma da lontano va bene.
- I fingers partono dal bordo della spina (1,4 m dall'asse), così le due mesh non si compenetrano.
- I galleggianti radicati al ciglio partono 3,5 m dentro l'acqua: in mezzo va la `SM_Morin_Marina_Passerella` (3 righe, pitch −7,33°,
  origine sul ciglio a Z 0, +X verso il mare).
- `SM_Morin_Marina_PontileLargo` (1 riga, X 127, Z 0, fisso): **nuovo**, 35 × 5 m. Ripiego: due file di `SM_Mirabello_Pontile`
  a ±1,45 m dall'asse, scala X 0,72.
- `SM_Morin_Marina_Circolo` (1 riga, centro X 161, Y 72): **nuovo**, edificio di fondale.
- Collisioni: decisione di Mirabello (2026-11-20, `docs/decisioni.md`): pontili e barche **senza collisione**. Qui però i pontili
  partono dal ciglio e sono raggiungibili a piedi: **decisione da chiedere all'utente** (dare UCX ai moduli della marina o lasciarli
  senza: si cade in acqua).

### 5.2 `exports/marina/marina_barche_v1.csv` (475 righe)
- Convenzione degli scafi (dallo script di Mirabello, `_hull_loft`): **origine al galleggiamento, al centro; +X = prua**. Per questo
  z = **−103** per tutte le barche (pelo dell'acqua; immersione già nel modello). Nota: a Mirabello gli yacht sono a −100 perché lì
  l'acqua del Blender era a −1,0: se gli scafi galleggiano 3 cm troppo bassi, uefn-builder alzi tutto a −100.
- `SM_Mirabello_YachtA` ha l'origine non centrata (X −6,95…6,25): il generatore ne tiene conto.
- Prua: ormeggio di poppa → yaw = direzione dal pontile verso l'acqua; `_prua` nella variante → ruotata di 180°.
- `nome`: `Barca_<pontile>_<n>`, per selezionare un pontile intero in UEFN (es. tutte le `Barca_F8_*`).

---

## 6. Asset nuovi per blender-artist

Budget di CLAUDE.md §4: prop ≤ 4k tri. Sono asset ripetuti centinaia di volte: tenersi molto sotto, come gli yacht di Mirabello
(600/272/126). 2 LOD (50 % e 15 %), niente collisione (vedi §5.1), atlante condiviso (scafo bianco, blu, teak, tela blu/beige,
gomma, acciaio, legno) a 1024-2048 px. Convenzione: origine al galleggiamento al centro, +X prua, misure dalle foto [S].

| Asset | Misure | Forma e riferimenti | Tri LOD0 proposti |
|---|---|---|---|
| `SM_Morin_Barca_Gommone` | 5,0 × 2,2 m, tubolari Ø 0,5 m, h 1,2 m con la consolle | tubolari grigi/neri attorno a scafo bianco a V, consolle centrale bianca, fuoribordo nero. [F] `ponte_verso_passegiata.png` (a destra) | ≤ 800 |
| `SM_Morin_Barca_Gozzo` | 6,0 × 2,3 m, bordo libero 0,8 m | gozzo ligure: prua e poppa a punta, falchetta in legno, piccolo tendalino o teli blu, fuoribordo/entrobordo; varianti con fascia colorata. [F] `banchina_vista_montagne_verso_ponte.jpg` (barche aperte coi teli blu in primo piano) | ≤ 1.000 |
| `SM_Morin_Barca_Motoscafo` | 7,5 × 2,7 m, h ~2,2 m con parabrezza | open/cabinato piccolo: scafo bianco, tuga bassa, parabrezza, **capottina/bimini blu** (molto frequente), fuoribordo bianco. [F] `ponte_verso_passegiata.png`, `vista_dall_alto.png` | ≤ 1.200 |
| `SM_Morin_Barca_Vela9` | 9,0 × 3,0 m, albero 12-13 m dal galleggiamento | barca a vela da crociera, scafo bianco (variante blu), randa sul boma col copriranda blu, fiocco avvolto bianco. Copia in scala di `SM_Mirabello_YachtB_v2` (11 m) va bene | ≤ 600 |
| `SM_Morin_Marina_Pontile12` | 12 × 2,8 m, stessa sezione di `SM_Mirabello_Pontile` | galleggiante: fianchi grigi in cemento, tavolato scuro, bottazzo in gomma, gallocce ogni 3 m sui due lati, 1 colonnina. Serve per i tratti corti e per finire i tratti lunghi (46 istanze) | ≤ 300 |
| `SM_Morin_Marina_PontileLargo` | 35 × 5 m, calpestio a Z 0 | pontile fisso (forse su pali), tavolato o cemento chiaro, pali tondi ogni ~4 m. [F] `vista_dall_alto.png` (pontile chiaro senza barche fra il pontile a L e la spina) | ≤ 1.500, UCX box |
| `SM_Morin_Marina_Passerella` | 3,6 × 1,4 m | passerella in alluminio con corrimano ai due lati e piastra di appoggio; origine sul lato a terra | ≤ 400, UCX box se i pontili avranno collisione |
| `SM_Morin_Marina_Colonnina` (opzionale) | 0,35 × 0,35 × 1,1 m | colonnina acqua/luce bianca con cappello e luce verde/blu: serve solo se `Pontile12` non la include | ≤ 100 |
| `SM_Morin_Marina_Circolo` | ~16 × 10 × 3,5 m | sede del circolo su palafitta alla radice della spina: pareti scure (bruno/nero), insegna rossa con nome inventato, tetto piano chiaro, pontile-terrazza. [F] `vista_dall_alto*.png`, `vista montagne.jpg`, `banchina_vista_montagne_verso_ponte.jpg` | ≤ 2.000 |

Nessun nome o logo reale sui modelli (CLAUDE.md §5): niente "Assonautica", nomi di barche inventati o assenti.

Stima di carico: 475 barche × ~1.000 tri LOD0 medi ≈ 0,5 M tri se fossero tutte al LOD0; dalla passeggiata la maggior parte è
oltre 50 m, quindi LOD1/LOD2. Da verificare in UEFN (uefn-builder: un HISM per asset e variante, come per le auto).

---

## 7. Dati da confermare [S]

1. Larghezza dei pontili (spina 3 m, fingers 2,5-3 m, pontile largo 5 m): una foto dalla banchina o dalla radice della spina.
2. Galleggianti o fissi, e se c'è una passerella al ciglio: foto della radice della spina e del pontile a L.
3. Verso delle barche (di poppa o di prua) e presenza di colonnine sui fingers: una foto dalla testa di un finger.
4. Forma, colori e misure della sede del circolo.
5. Se il pontile esterno (Y −175) e il pontile esterno 2 (Y −213…−230) sono pontili d'ormeggio o una diga galleggiante.
6. Ordine delle taglie: in questa versione le barche crescono verso il largo, come suggerisce la distanza fra i fingers.
7. Convenzione "+X = prua" degli yacht di Mirabello: dallo script (`_hull_loft`, "+X prua"). Da guardare in UEFN dopo la posa.
