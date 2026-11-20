# Scheda — Blocco 2: tratto centrale della Passeggiata Morin (X ≈ 251 → 560)

Legenda: **[V]** verificato (fonte citata) · **[V-utente]** confermato dall'utente · **[F]** letto da una foto in `ref/foto/` · **[S]** stima, da confermare.
Coordinate di progetto come in `area.md`: X lungo la passeggiata verso NE, Y verso la città, metri. In UE: (X·100, −Y·100).
Geo-scout, 2026-11-20. Niente Blender né UEFN.

**Fonti**
- OSM: l'estratto `ref/osm/morin_bbox.osm` si ferma a lat 44,10539 e quindi non copre la fine della passeggiata. Per questo ho scaricato
  dall'API OSM (`/api/0.6/map`, 2026-11-20) un estratto nuovo, salvato in **`ref/osm/morin_blocchi23.osm`** (bbox 44,1004-44,1090 N,
  9,8240-9,8362 E). © OpenStreetMap contributors, ODbL. La conversione in coordinate di progetto usa la stessa proiezione di `area.md`.
  Controllo: il faro (node 1327347929) cade a (678,6; −327,1), contro (678; −326) di `area.md`.
- REDAMARE: Finestre sull'Arte, 27-05-2022 ([link](https://www.finestresullarte.info/arte-contemporanea/la-spezia-inaugurato-monumento-redamare-sabrina-d-alessandro)).
- Foto dell'utente in `ref/foto/` (§9). Google solo come riferimento visivo: non ho salvato nulla.
  Il 2026-11-20 l'utente ha aggiunto catture Street View della fine passeggiata e del raccordo col molo: §4.5 e §9 aggiornati (dati marcati [F]).
- **Da non duplicare:** la sezione generale è in `sezione.md`, la banchina in `banchina.md`, le palme in `palme.md`, i Giardini a Mare
  in `zona_parcheggio_chiosco.md` §4, le colline e la città in `fondale.md`.

Nomi reali (bar, aziende) citati **solo per identificare il luogo**. Nel gioco i nomi sono inventati (CLAUDE.md §5).

---

## 1. Box e confini

| Voce | Valore | Stato |
|---|---|---|
| Box giocabile | X 240 … 570, Y −10 … 150 | proposta |
| lat / lon | **44,10318 – 44,10636 N · 9,82585 – 9,83007 E** | calcolo |
| Box con il fondale lato città (fino a Y 260) | 44,10318 – 44,10701 N · 9,82482 – 9,83007 E | calcolo |
| Inizio | X ≈ 251,4: fine del ciglio del Blocco 1, oggi chiuso da `SM_Banchina_Testata_Fine` | [V] PLAN.md |
| Fine del ciglio rettilineo | **X 548,7, Y 78,3**: qui il ciglio piega verso −Y e diventa il fianco ovest del Molo Italia | [V] OSM coastline 137121074 |
| Fine dell'area pedonale | X 559-560, Y 79-100. Oltre ci sono il raccordo in cubetti verso il molo e Largo Fiorillo | [V] OSM 850396604 |
| Lunghezza del tratto | 297 m di ciglio (X 251,4 → 548,7), 309 m di passeggiata (→ X 560) | [V] |

## 2. Sezione trasversale: cosa resta e cosa cambia rispetto a `sezione.md`

Ho controllato le way OSM lungo X 251-560. La sezione di `sezione.md` **resta valida per tutto il tratto**, con le eccezioni elencate qui sotto.

| Fascia | Y | Nel Blocco 2 | Stato |
|---|---|---|---|
| Ciglio | 80 (79,4 a X 289, 78,3 a X 548,7) | rettilineo, con una leggera deriva verso il mare di 1,7 m in 260 m. Per il kit: **retta unica a Y 80**, scarto < 2 m | [V] OSM |
| Camminamento a lastre | 80-89 | invariato, 9 m | [V] OSM 850396604 |
| Cordolo | 89 (88,4 a X 277, 89,7 a X 558) | continuo fino a X 558. A X 277 c'è un nodo `kerb=raised`, dove lo attraversa il vialetto diagonale (§4.3) | [V] OSM 850396603, node 7933688365 |
| Fascia palme | 89-102 | **2 filari** a Y ≈ 91-93 e 99-100, fino a **X 557 / 556**. Corridoio pedonale a Y ≈ 95 (footway 1198056664), fino a X 559 | [V] OSM 378875629/31, decisione utente "sempre e solo due filari" |
| Giardini a Mare (prato) | 102-116 | prato `leisure=park` **fino a X 526,5**. Da X 526,5 a 541,6 c'è un triangolo di verde (way 850396608). Da X ≈ 545 a 560 c'è la piazzetta del chiosco ottagonale (§4.5) | [V] OSM 850396610, 850396608 |
| Vialetto lungo il viale | ~117,7-118 | **nuovo rispetto al Blocco 1:** footway pavimentata X 301 → 556,6, lungo il bordo del prato verso il viale | [V] OSM 850396607 |
| Oleandri | 119,1-119,5 | continuano fino a X 556. Le posizioni sono già in `exports/giardini/giardini_posizioni_v1_blocco2.csv` (55 oleandri + 69 moduli di panchina lunga) | [V] OSM 850406862 |
| Viale Italia | 121-139 | X 253-355: due carreggiate a senso unico (assi Y 127-128 e 132-134). X 355-396: un'unica sede a 4 corsie (asse Y 128,5). X 396-483: di nuovo due carreggiate (Y 129 e 135) con **isola centrale**. Da X 483: 4 corsie, asse Y 129,8 | [V] OSM 850396600/601/593/592/594, 193303765 |
| Ciclabile | 141-147 | Y 141,3-141,7; tra X 436 e 466 fa una gobba fino a Y 147 | [V] OSM 84393784 |
| Lato città | > 144 | Giardini pubblici fino a X 439, poi Via Pietro Micca (X 439-452), giardinetto X 458-511, Via XX Settembre (X 519-520), giardino X 532-621 davanti al Palazzo Comunale | [V] OSM |

**Varchi nel prato** (dove il prato non deve essere continuo):
- X ≈ 275-301: vialetto diagonale dalla banchina (274,7; 85,7) alle strisce di Viale Italia (301,2; 117,7). Way 183535305 [V].
- X ≈ 437-506: due vialetti diagonali e un anello (462-501; 111,7) che portano al semaforo pedonale di X 506 (Via XX Settembre). Way 850396591, 850396598, 850396596 [V].

## 3. Ritmo degli arredi della fascia palme (continuazione del Blocco 1)

Regole del Blocco 1 (`sezione.md` §6, [V-utente]): palme a passo 9 m, filari allineati, una panchina ogni 2 palme, un lampione ogni 4 palme.

| Elemento | Blocco 1 (ultimo) | Blocco 2 (proposta) | Numero | Stato |
|---|---|---|---|---|
| Palme (2 filari, Y 92,6 e 99,6) | X 246 (griglia v3, 12 + 9k) · X 254,4 (layout v4 in PLAN, 20,4 + 9k) | **stessa griglia del Blocco 1**: con la v4 X 263,4 … **551,4** (33 per filare); con la v3 X 255 … 552 (34 per filare). Panchine e lampioni si spostano di −0,6 m insieme | **66-68** | passo [S] (vedi la nota sotto) |
| Panchine a lastra (Y 92,1) | X 232,5 | X 250,5 + 18k: **268,5 … 538,5** | 16 | [S] continuazione |
| Lampioni a 2 globi (Y 92,85) | X 232,8 | X 268,8 + 36k: **268,8 … 520,8** | 8 | [S] continuazione |
| Tombini (coppie, corridoio) | 8 coppie | ~10 coppie | ~10 | [S] |
| Aiuole delle palme | — | una per palma | 66 | [V-utente] forma |

**Nota sul passo, da verificare.** OSM mappa 9 panchine senza schienale a Y ≈ 92,1-92,8, alle X **256, 272, 288, 304,5, 320, 336,5, 352, 368,6, 384**.
L'intervallo è costante, **~16 m** [V OSM]. Se la regola "una panchina ogni due palme" è giusta, il passo delle palme sarebbe **~8 m** e non 9.
Con 8 m i filari X 20,4-557 contengono 68 palme ciascuno, contro le 60 attuali.
La posizione OSM delle panchine non è un rilievo (errore di qualche metro), ma la regolarità è sospetta.
Nel Blocco 1 si è usato 9 m. **Proposta:** restare a 9 m nel Blocco 2 per coerenza e chiedere il conteggio (foto F7).
OSM non mappa panchine oltre X 384: dopo quel punto si continua col ritmo del Blocco 1 [S].

## 4. Elementi notevoli

### 4.1 Gruppo cannoni + REDAMARE (a cavallo del confine col Blocco 1)
| Elemento | Posizione | Dimensioni | Fonte | Stato |
|---|---|---|---|---|
| Cannone 1, ad avancarica, su affusto | **X 249,0, Y 82,1** | canna ~2,2-2,5 m, bocca Ø ~0,30 m; affusto in legno scuro a 4 ruote piene in ghisa, ~1,6 × 0,9 × 0,8 m; canna rivolta al mare (−Y) | OSM 5913835513; forma [F] `cannone_*`, `scultura_*` | posizione [V], misure [S] |
| Cannone 2 | **X 259,3, Y 82,4** | come il cannone 1 | OSM 5913835504 | [V] / [S] |
| **Scultura "REDAMARE"** (Sabrina D'Alessandro, 2022) | **fra i due cannoni: X ≈ 250,5-258, Y ≈ 82-83**, lettere parallele al ciglio, leggibili da terra (lo spettatore guarda verso il mare) | 8 lettere in acciaio corten, maiuscole bastoni spesse; **h ~1,2-1,4 m**, profondità ~0,35 m, lunghezza totale **~7,5 m** su piastra corten ~8 × 0,6 × 0,05 m | "tra due antichi cannoni ad avancarica, davanti alle acque del golfo" [V Finestre sull'Arte]; corten [V]; forma [F] `scultura_*` | posizione dedotta [V-OSM+articolo]; misure [S] |
| Seconda ancora | **X 279,9, Y 82,6** | come la prima, ~2,7 × 3,2 m | OSM 5913835508 | [V]; forma [S] (foto F2) |

**Correzione al PLAN.** PLAN.md mette cannone e REDAMARE "a ~275 m, a metà della passeggiata". OSM e l'articolo li mettono **fra X 249 e 259**,
cioè 16-26 m prima. Il cannone 1 cade ancora nel Blocco 1, ma oggi non è modellato. Il gruppo va fatto **tutto insieme nel Blocco 2**.
Tutti e tre gli oggetti stanno sul camminamento (Y 81,5-84) e lo restringono, come l'ancora 1: vale la stessa deroga alla corsia di 8 m
già registrata in `docs/decisioni.md`.

### 4.2 Ormeggi e acqua davanti al tratto
| Elemento | Posizione | Dimensioni | Fonte | Stato |
|---|---|---|---|---|
| Fingers del pontile principale Assonautica | estremità a X ≈ 259-262, Y 63 … −131 | già nel Blocco 1 (`elementi.md` §1) | OSM 149964057… | [V] |
| Pontile Assonautica NE | X 289-292, da Y 79 a −7 (86 m) | largo ~2,5 m [S]; barche ai due lati | OSM 175935432 | [V] |
| Pontile esterno Assonautica | X 196-316, Y −177 … −230 | 163 m, in mare: fondale | OSM 175935436 | [V] |
| **Specchio d'acqua libero** | X ≈ 296 … 548, davanti al ciglio | nessun pontile mappato; nelle foto `cannone_*` e `scultura_*` si vede acqua aperta con battelli lontani | OSM (assenza) + [F] | [V] |
| Bitte | **nessuna, per ora** | si mettono solo dove c'è ormeggio (decisione utente). X 251-296: ormeggio della marina, ma le barche stanno ai pontili. X 296-548: nessun ormeggio mappato | decisione utente; [S] | da confermare con la foto F4 |
| Scalette alla marinara | ~1 ogni 50 m, come nel Blocco 1: **6 nicchie** a X ≈ 300, 350, 400, 450, 500, 540 | modulo `SM_Banchina_Mod4m_Nicchia` + `SM_Banchina_Scaletta_v2` | [S] | — |
| Barche ormeggiate al ciglio | sì, nella foto Alamy `vista montagne.jpg` (verso SO): barche affiancate al ciglio nella zona della marina | — | [F] | posizione esatta [S] |

### 4.3 Giardini a Mare e arredi lato città
| Elemento | Posizione | Dimensioni | Fonte | Stato |
|---|---|---|---|---|
| Prato | X 251-526,5, Y 102-116, con i varchi del §2 | — | OSM 850396610 | [V] |
| Aiuole di rose con bordo in lamiera scura, siepi basse, agavi | sparse nel prato | aiuole rettangolari ~6-12 × 2-3 m; agavi Ø ~1,5-2 m | [F] `giardini.webp`, `giardini_affianco_palme.jpg`, `giardini_con panchine_affianco_palme.jpg`; disposizione non mappata | [S] posizioni |
| Panchine bianche **a schienale curvo** | lungo un vialetto interno ai giardini | ~1,8 × 0,7 × 0,8 m, pietra/cemento bianco | [F] `giardini_con panchine_*` | [S] posizioni |
| Panchina lunga continua (Y 101,7) | continua dal Blocco 1 | modulo 4 m | CSV `giardini_posizioni_v1_blocco2.csv` (69 moduli) | posizioni [S] |
| **Memoriale "Agli Aviatori"** (1983) | **X 397,8, Y 110,6** | stele o monumento ~2-3 m [S] | OSM 7933688347 | posizione [V]; forma [S] (foto F5) |
| Pannello "WATERFRONT MAP" | X 300,2, Y 113,8 | pannello ~1,5 × 2 m | OSM 7955911722 | [V] |
| Pannello "Mappa del centro" | X 501,1, Y 109,1 | idem | OSM 7955911723 | [V] |
| Fontanella a colonnina | X 460,7, Y 111,6 | h ~1 m | OSM 8478856178 | [V] |
| Edicola/casottino giallo con insegna | sotto le palme, lato mare, X non nota | ~4 × 3 × 3 m | [F] `giardini_affianco_palme.jpg` (con gommone esposto accanto) | [S]: posizione, e se esiste ancora |
| Strisce pedonali su Viale Italia | X 300,7 (zebra) · X 506,4 (semaforo a chiamata) · X 520 (semaforo, incrocio con Via XX Settembre) | — | OSM 1352945068, 7933688353, 10120380247, 252732410 | [V] |

### 4.4 Lato città (solo fondale)
| Elemento | Posizione | Note | Stato |
|---|---|---|---|
| Giardini pubblici | X ≤ 439, Y 144-295 | alberi già posati nel Blocco 1 fino a ~X 330 (CSV viale) | [V] OSM 107277712 |
| Fontana "Resistenza" | X 386, Y 159 | nei Giardini pubblici, oltre il viale | [V] OSM 3822359189 |
| Stele a Nazario Sauro | X 314,6, Y 166,1 | idem | [V] OSM 7952694060 |
| Monumento a Garibaldi | **non cade qui**: è a X ≈ −73, Y ≈ 199 (Blocco 1, `elementi.md` §4) | — | [V] |
| Cortina edilizia (Viale Mazzini) | fronte a **Y 206-208**: X 260-308, 320-370, 382-446, 469-498; albergo X 528-567 (Y 207-234); **Palazzo Comunale** X 586-625 (Y 204-241) | OSM non dà i piani. Nelle foto: palazzi di 5-7 piani chiari. Il Palazzo Comunale è uno dei pochi edifici riconoscibili da lontano [S] | piante [V] OSM; altezze [S] |
| Torre chiara | nella foto `giardini_affianco_palme.jpg` spunta una torre squadrata oltre gli alberi del viale | probabilmente un edificio alto del centro [S] | [F] |

### 4.5 Fine della passeggiata e raccordo con il Molo Italia (X 540-575) — aggiornato 2026-11-20 con le foto nuove
Foto: `vista/incrocio_molo_italia_passegiata_morin.png` (I1), `vista/incrocio_molo_italia_passegiata_morin_2_chiosco_info_point.png` (I2),
`vista/3_aste_bandiere_molo.png` (A3), `vista/monumento_molo.png` (MO), `vista/chiosco_2_fine_passegiata_morin.png` (C2),
`vista/guardia_costiera_molo_italia_2.png` (G2). Sono tutte **catture Street View** (vedi §9). Le grandi scritte bianche in 3D sull'asfalto
("Molo Italia", "Largo Michele Fiorillo", "...na Thaon di...") sono **etichette dell'interfaccia di Street View**: non sono dipinte e **non vanno modellate**.

| Elemento | Posizione | Dimensioni / aspetto | Fonte | Stato |
|---|---|---|---|---|
| **Scritta "PASSEGGIATA MORIN"** nel pavimento | nel corridoio fra i filari, **X ≈ 552-560, Y ≈ 92-100**, prima della prima palma da NE; si legge guardando verso SO | due righe: "PASSEGGIATA" (~7 m) e "MORIN" (~4 m); lettere **h ~0,6-0,7 m**, tratto ~0,12 m, in pietre bianche annegate nei cubetti | [F] `scritta_pavimento_inizio_passegiata_lato_opposto_al_ponte.jpg`. Le foto nuove non la inquadrano | posizione e misure [S] |
| **Piazzale terminale** (fine camminamento → smusso → radice del molo) | X ≈ 545-570, Y ≈ 45-100 | pavimento in **cubetti di porfido grigio-rosato posati ad archi** (coda di pavone), continuo fino al ciglio dello smusso; nessun gradino visibile fra passeggiata, piazzale e radice; nessun parapetto sul ciglio | [F] I1, G2 | [F]; il limite esatto lastre/cubetti è [S] |
| **Ciglio dello smusso** | da (548,7; 78,3) a (~555; ~45) | **banchina a blocchi**, con coronamento chiaro rettilineo come il resto della passeggiata, salto di ~1 m sull'acqua; **niente bitte e niente barche** nell'ultimo tratto della passeggiata (le barche ormeggiate si vedono solo lontano, verso la marina) | [F] A3, I1; geometria [V] OSM | [F] |
| **Inizio della scogliera** | dal **monumento** (~Y 45) in poi, lungo tutto il fianco ovest del ramo 1 | dove finisce lo smusso il bordo **non è più banchina**: è una **scogliera di massi** (massi grigio-ocra ~1-2 m) sotto il marciapiede del molo. Vale per tutto il lato esterno del molo (vedi `molo_italia.md` §2) | [F] MO, `molo_italia_1-7` | [F]; il punto esatto di passaggio è [S] ±5 m |
| **Tre aste portabandiera** | allineate lungo il ciglio dello smusso, verso la sua estremità nord: **~(550-554; 58-68)** | 3 aste **bianche** cilindriche, **h ~11-12 m**, interasse ~3-4 m, basamento piccolo a raso; bandiere: Italia, una bianca (Comune/Regione), Unione Europea (in A3 ne è issata una sola: le bandiere cambiano) | [F] I1, A3 (altezza confrontata con una persona alla base in I1) | posizione [S] ±5 m; h [F] stima ±1,5 m |
| **Monumento con busto** (lunetta) | angolo fra smusso e ramo 1, **~(553; 46)** ±5 m | **lunetta semicircolare** Ø ~8-9 m che sporge sulla scogliera, chiusa da un **muretto in pietra a vista** h ~0,6-0,8 m; dentro, 4-6 **pilastrini in pietra** h ~0,6 m con **catene** fra l'uno e l'altro; al centro una **stele in pietra chiara** ~1,0 × 0,6 × 2,5 m su un gradino, con targa/emblema in bronzo in cima, e un **busto in bronzo** su un piedistallo basso al fianco; lampione a pastorale accanto | [F] MO, A3 (il muretto in primo piano), I1 | forma [F]; nome e iscrizione illeggibili [S] → integrazione n. 5 |
| **Lampioni del raccordo** | lungo il ciglio dell'acqua, dal piazzale verso il molo | **a pastorale con un globo** (vedi `molo_italia.md` §2.3), non a due globi come la passeggiata. I lampioni a 2 globi della passeggiata arrivano fino al chiosco | [F] I1, G2, C2 | [F] |
| **Cartello d'ingresso alla passeggiata** | ~(562; 90), dove il camminamento incontra Largo Fiorillo | palo con cartello "zona pedonale" + limite **10 km/h**, su una base gialla in plastica | [F] I1, G2 | posizione [S] |
| **Fioriere quadrate nere** | fila fra Largo Fiorillo e il percorso pedonale del molo, ~X 562-570, Y 70-95 | 4-6 fioriere ~0,8 × 0,8 × 0,6 m, nere, con piante basse | [F] G2, I1 | [S] numero e posizione |
| **Parcheggio alla radice del molo** | lato ovest dell'inizio del ramo 1, accanto al monumento (Y ≈ 0-40) | auto in fila con strisce gialle, fra la carreggiata e i lampioni | [F] MO | [S] estensione → riuso del kit `SM_Morin_Auto_*` |
| **Chiosco-bar ottagonale** ("chiosco 2"; "Il Piccolo Faro" in OSM) | **X 548,5-555,1, Y 106,1-112,9** (centro 551,9; 109,5) | pianta ottagonale Ø **~6,5 m** [V]; **h ~3,3-3,6 m** al colmo [F stima con le persone al bancone]; **tetto in lamiera grigia** a falde basse con gronda sporgente; **tende a falda color crema** su tutti i lati; bancone in legno; locandine colorate | OSM way 352041625; aspetto [F] C2, I2 | pianta [V]; aspetto [F]; forma ottagonale non leggibile in foto [S] |
| **Dehors del chiosco** | intorno al chiosco, soprattutto verso SO (X 540-552) e verso il mare (Y 102-106) | 4-5 **ombrelloni quadrati bianco-écru** ~3 × 3 m; **botti** usate come tavoli alti con sgabelli neri; tavolini tondi con piano in vetro; **fioriere rettangolari** in cotto e grigie con arbusti; 2 lampioni a 2 globi dentro il dehors | [F] C2, I2 | [F]; disposizione [S] → kit `SM_Morin_Ombrellone`, `TavoloSet`, `Fioriera` + una botte nuova semplice |
| **Pavimento della piazzetta del chiosco** | X 545-560, Y 102-116 | cubetti grigi con **fasce di lastre bianche** (~0,4-0,5 m) che incorniciano i riquadri | [F] C2 | [F] → `M_Molo_Masselli` + `M_Pav_Fascia` |
| Oleandri a fiore bianco e prato | dietro il chiosco (lato viale) e a SO (triangolo verde) | prato con bambini che giocano a sinistra in C2 = triangolo verde X 526-541 | [F] C2; OSM 850396608 | [V]/[F] |
| Triangolo verde | (526,5; 100,9) – (541,6; 100,5) – (526,5; 114,8) | — | OSM 850396608 | [V] |
| Stalli per disabili (4) | X 561-566, Y 100-117 | lungo la strada d'accesso al molo; in I1 auto parcheggiate sul bordo destro | OSM 1089508561-63, 1111180847; [F] I1 | [V]: fuori dal Blocco 2, nel raccordo |
| **Largo Michele Fiorillo** | X 565-580, Y 40-130 | **asfalto chiaro**, strisce pedonali a zebra fra la fine della passeggiata e il parcheggio dei taxi; dissuasori bassi in pietra/cemento ("panettoni") ~0,5 m ogni ~1,5 m sul bordo del parcheggio; un **palo alto** di illuminazione stradale (~9-10 m, una testa) | OSM; [F] I2 | [F] |
| Raccordo verso il molo | percorso pedonale in cubetti lungo l'acqua X 555-570, Y 45-85 (way 238848747 + 132740887); carreggiata in asfalto di Largo Fiorillo a est | — | OSM + [F] G2 | [V] → dettagli in `molo_italia.md` §6 |

**Cosa cambia per `SM_Banchina_Angolo_MoloItalia`:** lo smusso resta banchina a blocchi (kit v2) da (548,7; 78,3) fino a ~Y 47; lì il pezzo
chiude contro la **lunetta del monumento** (muretto in pietra, non banchina) e da lì in poi il fianco ovest del molo è **scogliera**, non ciglio.
Sul piazzale nessun parapetto; aste e monumento sono gli unici oggetti alti sul ciglio.

### 4.6 Cosa OSM non mappa nel tratto
Lampioni, bitte, tombini, cestini, alberi singoli, aiuole di rose, agavi: **nessuno** [V, assenza nell'estratto del 2026-11-20].
Gli unici lampioni mappati della zona sono lontani (via della stazione, X > 850).

## 5. Raccordi

| Raccordo | Dove | Cosa fare | Stato |
|---|---|---|---|
| Con il Blocco 1 | X 251,4 | **nascondere** `Arte_Banchina_Testata_Fine` (non cancellarlo) e proseguire con `SM_Banchina_Mod4m_v2` dalla stessa retta. Pavimentazione, cordolo e fascia palme ripartono dagli stessi moduli (passo 4 m / 9 m) senza scalini. Il blockout della passeggiata e `Barriera_FineBlocco` (X 251,3) vanno spostati a X ≈ 560 | [V] PLAN.md |
| Viale | X 326 | i moduli `SM_Viale_Italia_Strada_v2` arrivano già a X 326: proseguire fino a X ~560, più 2 moduli incrocio (X 506 e 520) | [V] PLAN.md |
| Con il Molo Italia | X 548,7 → 555 | il ciglio fa uno **smusso**: da (548,7; 78,3) a (555,0; 41,9), angolo di ~80° col ciglio della passeggiata. Serve un pezzo di testata nuovo, `SM_Banchina_Angolo_MoloItalia`, con lo stesso materiale della v2. **Dalle foto (2026-11-20):** banchina a blocchi solo fino a ~Y 47, poi la lunetta del monumento (muretto in pietra) e la scogliera del molo; piazzale in cubetti fino al ciglio, senza parapetto; 3 aste bianche h ~11-12 m sul ciglio (§4.5) | [V] OSM coastline; [F] |

## 6. Tabella degli elementi per la produzione

Priorità visiva: **A** = si vede dalla corsia e identifica il posto · **B** = contorno visibile · **C** = dettaglio o fondale.
Texture nuove: "0" = nessuna texture nuova.

| # | Elemento | Posizione (X, Y) | Dimensioni | Fonte | Stato | Asset proposto | Texture nuove | Priorità |
|---|---|---|---|---|---|---|---|---|
| 1 | Ciglio banchina | X 251,4-548,7, Y 80 | 74 moduli da 4 m + 1 resto | OSM | [V] | **kit** `SM_Banchina_Mod4m_v2` + `_Nicchia` + `Scaletta_v2` | 0 | A |
| 2 | Angolo verso il Molo Italia | (548,7; 78,3) → (555; 41,9) | ~37 m di smusso | OSM | [V] | **nuovo** `SM_Banchina_Angolo_MoloItalia` (≤ 2k tri), materiale `MI_Banchina_Blocchi` | 0 | B |
| 3 | Camminamento, cordolo, fascia palme, aiuole | X 251-560, Y 80-102 | moduli 4 m / 9 m | OSM + [V-utente] | [V] | **kit** `SM_Pav_Camminamento_4m`, `SM_Pav_Cordolo_9m`, `SM_Pav_FasciaPalme_9m`, `SM_Pav_Aiuola` | 0 | A |
| 4 | Palme | 66-68, X ~255-552 (§3) | come il Blocco 1 | §3 | passo [S] | **kit** `SM_Morin_PalmaA` (+ B/C se fatte) | 0 | A |
| 5 | Panchine, lampioni, tombini | §3 | — | §3 | [S] | **kit** `SM_Morin_Panchina`, `SM_Morin_Lampione`, `SM_Morin_Tombino` | 0 | A |
| 6 | Cannoni ×2 | (249,0; 82,1), (259,3; 82,4) | ~2,5 × 1,0 × 1,0 m | OSM + [F] | [V] pos. | **nuovo** `SM_Morin_Cannone` (≤ 4k tri, 1 istanza ×2): canna `MI_Banchina_Ghisa`, affusto `T_Morin_Imbarco_Legno` (riuso) | 0 | A |
| 7 | REDAMARE | X 250,5-258, Y 82-83 | 7,5 × 0,35 × 1,3 m | articolo + [F] | [V] pos. dedotta | **nuovo** `SM_Morin_Redamare` (lettere estruse, ≤ 2k tri) | **corten 1024 (D+N+ORM) ≈ 2,7 MiB**, da `src/rusty_metal_02` (Poly Haven CC0). Alternativa a 0 MiB: `T_Banchina_Ghisa` con tinta ruggine nel MI | A |
| 8 | Ancora 2 | (279,9; 82,6) | ~2,7 × 3,2 m | OSM | [V] | **kit** `SM_Morin_AncoraMonumento` con yaw diverso | 0 | A |
| 9 | Scritta "PASSEGGIATA MORIN" | X 552-560, Y 92-100 | 2 righe, lettere h 0,65 m | [F] | [S] | **nuovo** `SM_Pav_Scritta_Morin`: lettere come mesh piatta a +3 mm sui cubetti, materiale `M_Pav_Fascia` (pietra bianca) | 0 | A |
| 10 | Prato Giardini a Mare | X 251-526,5, Y 102-116 | ~275 × 14 m con 2 varchi | OSM | [V] | **nuovo** `SM_Morin_Prato_Giardini_B2` (pezzo unico, come la v1), `M_Morin_Prato` | 0 | B |
| 11 | Oleandri + panchina lunga | Y 119,5 / 101,7 | 55 + 69 | CSV già pronto | [V]/[S] | **kit** (`giardini_posizioni_v1_blocco2.csv`) | 0 | B |
| 12 | Vialetto lungo il viale e diagonali | Y ~118; X 275-301; X 437-506 | larghezza ~2,5-3 m [S] | OSM | [V] | **kit** lastre `M_Pav_Lastre` / masselli `M_Molo_Masselli` su mesh nuove semplici | 0 | B |
| 13 | Aiuole di rose con bordo metallico | nel prato | ~8 × 2,5 m | [F] | [S] | **nuovo** `SM_Morin_AiuolaRose` (bordo + card fiori), fiori da `T_Viale_Fiori` (riuso) | 0 | B |
| 14 | Agave | nel prato | Ø 1,5-2 m | [F] | [S] | **nuovo** `SM_Morin_Agave` (card o foglie spesse, ≤ 2k tri) | **1024 D(+alpha)+N ≈ 2,7 MiB**. Se si vuole 0: foglie geometriche con `MI_Morin_Bosso` ritinta | C |
| 15 | Panchina a schienale curvo | nei giardini | 1,8 × 0,7 × 0,8 m | [F] | [S] | **nuovo** `SM_Morin_PanchinaCurva` (≤ 1,5k tri), `M_Pav_Fascia` | 0 | C |
| 16 | Memoriale Aviatori | (397,8; 110,6) | ~2-3 m [S] | OSM | [V] pos. | **nuovo** semplice, pietra `M_Pav_Fascia` / `MI_Banchina_Blocchi` | 0 | C |
| 17 | Pannelli informativi ×2, fontanella | (300,2; 113,8), (501,1; 109,1), (460,7; 111,6) | — | OSM | [V] | **kit** cartelli (`T_Morin_Cartelli`, riuso con grafica generica) + fontanella **nuova** semplice | 0 | C |
| 18 | Chiosco-bar ottagonale + dehors | (551,9; 109,5) | Ø 6,5 m, h ~3,5 m | OSM + [F] C2 | [V] pianta, [F] aspetto | **nuovo** `SM_Morin_ChioscoOttagonale` (tetto in lamiera grigia, tende crema, bancone in legno) con atlante `T_Morin_Chiosco` + dehors `SM_Morin_Ombrellone`, `TavoloSet`, `Fioriera` (kit) + botte-tavolo nuova semplice | 0 | B |
| 22 | Tre aste portabandiera | ~(550-554; 58-68) | h ~11-12 m, Ø ~0,12-0,15 m | [F] I1, A3 | pos. [S] | **nuovo** `SM_Morin_AstaBandiera` (≤ 500 tri, 3 istanze) + bandiere su card con `T_Morin_Cartelli` o tinta | 0 | B |
| 23 | Monumento con busto + lunetta | ~(553; 46) | lunetta Ø 8-9 m, stele 2,5 m | [F] MO | forma [F], pos. [S] | **nuovo** `SM_Morin_MonumentoRadice` (≤ 4k tri): muretto `MI_Banchina_Blocchi`, stele `M_Pav_Fascia`, busto e targa in bronzo (tinta), catene semplici | 0 | B |
| 24 | Cartello zona pedonale, fioriere nere | ~(562; 70-95) | — | [F] I1, G2 | [S] | **kit** cartelli + `SM_Morin_Fioriera` ritinta | 0 | C |
| 19 | Viale Italia X 326-560 | Y 121-139 | ~12 moduli + 2 incroci | OSM | [V] | **kit** `SM_Viale_Italia_Strada_v2`, `SM_Viale_Italia_Incrocio_v3`, `SM_Morin_Semaforo`, `SM_Viale_Spartitraffico_Fiori` (isola X 396-483); traffico finto allungato | 0 | B |
| 20 | Cortina lato città | Y 206-241, X 357-625 | ~10-12 sagome | OSM | piante [V], h [S] | **kit** `SM_Fondale_Palazzo_A/B/C` | 0 | C |
| 21 | Battelli / barche al largo | specchio X 296-548 | — | [F] | [S] | **kit** `SM_Morin_Battello`, `SM_Mirabello_YachtA/B_v2` | 0 | C |

**Asset nuovi senza texture nuove:** 2, 6, 9, 10, 12, 13, 15, 16, 17 (fontanella), 18.
**Asset con texture nuove:** 7 (REDAMARE) ed eventualmente 14 (agave).

## 7. Stima della memoria texture

| Voce | Set | MiB (con mip, BC1/BC5 come in `docs/uefn_arte.md`) |
|---|---|---|
| Corten REDAMARE | 1024 D + N + ORM | 0,67 + 1,33 + 0,67 ≈ **2,7** |
| Agave (facoltativa) | 1024 D (BC3, alpha) + N | 1,33 + 1,33 ≈ **2,7** |
| Grafica generica dei 2 pannelli (se non entra nell'atlante cartelli) | 512 D | ≈ **0,2** |
| **Totale Blocco 2** | | **≈ 2,9 MiB** senza agave · **≈ 5,6 MiB** con agave (obiettivo ≤ 10 MiB) |

Tutto il resto è riuso. Restano da tenere d'occhio due cose: le istanze e i triangoli (66 palme in più a ≤ 10k tri con LOD), e la memoria
delle mesh, che non è texture ma conta nel limite dell'isola.

## 8. Ordine di lavoro proposto (Blocco 2)

1. **(blender-artist) Struttura:** banchina X 251-548,7 (moduli, nicchie, scalette), `SM_Banchina_Angolo_MoloItalia`, pavimentazione e cordolo,
   blockout del suolo esteso fino a X 560. CSV posizioni v1 del Blocco 2. → (uefn-builder) import, nascondere `Testata_Fine`, spostare `Barriera_FineBlocco`.
2. **Palme, panchine, lampioni, tombini** dal ritmo del §3 (solo CSV + istanze HISM esistenti). Prima di farlo, chiedere F7 (passo).
3. **Gruppo REDAMARE + cannoni + ancora 2** (elementi 6-8): è il punto più riconoscibile del blocco.
4. **Scritta "PASSEGGIATA MORIN"** e chiosco ottagonale (fine passeggiata).
5. **Giardini a Mare:** prato B2 con i varchi, oleandri e panchina lunga dal CSV esistente, vialetti.
6. **Viale Italia** X 326-560 con gli incroci X 506/520 e l'isola; cortina di sagome; allungare il traffico finto.
7. Dettagli: aiuole di rose, agavi, panchine curve, memoriale, pannelli, fontanella.
8. (qa-tester) Sessione: raccordo a X 251 senza fessure, deroga corsia accanto a cannoni e REDAMARE, memoria.

## 9. Foto già disponibili per questo tratto

| File | Cosa si vede | Uso |
|---|---|---|
| `arredi/cannone_metà_banchina_verso_mare.jpg` | Cannone su affusto in legno scuro a 4 ruote piene, canna in ghisa verso il mare, sul camminamento a lastre a ~1 m dal ciglio; acqua aperta, battello in lontananza, colline di Lerici | forma del cannone; specchio d'acqua libero |
| `arredi/scultura_caratteri_cubitali_affianco_cannone.png` | "REDAMARE" in corten su piastra, parallela al ciglio, vista da terra verso il mare; a sinistra un cannone con una targhetta/luce sull'affusto; navi e barche lontane | forma, colore e proporzioni delle lettere |
| `pavimentazione/scritta_pavimento_inizio_passegiata_lato_opposto_al_ponte.jpg` | "PASSEGGIATA / MORIN" in pietre bianche nei cubetti a coda di pavone, fra i due filari, vista verso SO; lampione a 2 globi sul filare lato mare | posizione e grafica della scritta; conferma del kit lampioni |
| `vista/banchina_vista_montagne_verso_ponte.jpg` | Ciglio a grandi blocchi bianchi, ancora sul camminamento con un pannello accanto, panchine a lastra, lampione, marina a sinistra; vista verso SO | ancora 2 (o 1) e ciglio; non dice a quale X sia la camera [S] |
| `vista/vista montagne.jpg` (Alamy, **solo riferimento**, mai texture) | Camminamento con una **fascia longitudinale** di lastre a ~1/3 dal mare, panchine, filari, barche al ciglio; vista verso SO | conferma la fascia longitudinale [S] |
| `arredi/giardini.webp` | Prato con aiuole di rose (rosse e rosa) bordate di lamiera scura, filare di palme, nave da crociera in lontananza | aiuole di rose |
| `arredi/giardini_affianco_palme.jpg` | Giardini a Mare dal bordo del corridoio: prato, siepi, agavi, oleandri lungo il viale, casottino giallo e gommone sotto le palme | agavi, edicola gialla [S] |
| `arredi/giardini_con panchine_affianco_palme.jpg` | Vialetto in cubetti fra le palme e un'aiuola di rose, panchine bianche a schienale curvo, agavi, auto sul viale | panchina curva, vialetto interno |

**Foto aggiunte il 2026-11-20** (tutte in `ref/foto/vista/`, tutte **catture Street View**: utilizzabili anche per le texture con la marca
**[SV]** secondo la deroga di CLAUDE.md §5, senza persone, targhe, filigrane "© Google", bussola e etichette 3D delle vie):

| File | Punto di presa (X, Y) e direzione | Cosa si vede | Conferma / corregge |
|---|---|---|---|
| `incrocio_molo_italia_passegiata_morin.png` (I1, panorama ~160°, con scritte dell'utente) | ~(565; 90), verso SSO (fra −X e −Y), nell'angolo della baia | piazzale in cubetti ad archi; a destra l'inizio della passeggiata (cartello zona pedonale + 10 km/h, fioriere, palme e lampioni a 2 globi); al centro le 3 aste sul ciglio; a sinistra il monumento, palme in aiuola e lampioni a pastorale verso il molo; sullo sfondo marina e colline | conferma: niente parapetto, niente gradini; **nuovi**: aste, monumento, lampioni a pastorale |
| `incrocio_molo_italia_passegiata_morin_2_chiosco_info_point.png` (I2) | ~(572; 80) su Largo Fiorillo, verso +Y (città) | a sinistra il chiosco con dehors e palme; strisce pedonali; parcheggio taxi sotto i pini con i chioschetti dell'info point; palo alto; palazzi di Viale Mazzini (uno a torre ~12 piani) | conferma chiosco e posteggio taxi; i chioschetti sono **casette a facce piane**, non tonde (vedi `molo_italia.md` §5) |
| `chiosco_2_fine_passegiata_morin.png` (C2) | ~(549; 97), corridoio fra i filari, verso +Y | chiosco con tetto in lamiera e tende crema, dehors con ombrelloni, botti, fioriere; cubetti con fasce bianche; oleandri bianchi | **copre la foto F8** (solo il lato verso il mare: la forma ottagonale non si legge) |
| `3_aste_bandiere_molo.png` (A3) | ~(560; 48), radice del molo accanto al monumento, verso −X (SO, lungo la passeggiata) | le 3 aste in primo piano; il ciglio della passeggiata d'infilata, senza bitte; muretto in pietra del monumento a sinistra | **copre F9** e in parte F4 (ultimo tratto del ciglio: niente bitte) |
| `monumento_molo.png` (MO) | ~(565; 40), verso O | lunetta del monumento con stele, busto, pilastrini e catene; auto parcheggiate; lampioni a pastorale e scogliera lungo il ramo 1 | **nuovo**: monumento e inizio della scogliera |

Nessuna foto mostra ancora: il memoriale Aviatori, il passo delle palme, il chiosco dal lato del viale.

## 10. Foto da chiedere all'utente (Blocco 2)

Stato al 2026-11-20: **F8 coperta in parte** da C2 (manca il chiosco visto dal viale), **F9 coperta** da A3, MO e I1, **F4 coperta in parte** da A3
(ultimo tratto, niente bitte). Restano F1, F2, F3, F5, F6, F7, F10 e la parte mancante di F4/F8. Le richieste prioritarie sono in `molo_italia.md` §10.

1. **F1 — Gruppo REDAMARE di fronte.** Dal camminamento a ~8 m dal ciglio (X ≈ 254, Y ≈ 90), verso il mare: le lettere intere e i due cannoni ai lati, con una persona accanto per la scala.
2. **F2 — Ancora 2 (X 280).** Di lato, da X ≈ 270 guardando verso NE: ancora e basamento, per capire se è uguale alla prima.
3. **F3 — Un cannone di profilo**, da 3 m, con un piede o una scarpa accanto all'affusto: lunghezza della canna, ruote, eventuale targa.
4. **F4 — Ciglio d'infilata da X ≈ 300 verso NE**, inquadrando il bordo fino al Molo Italia: bitte, anelli, scalette, barche ormeggiate.
5. **F5 — Memoriale "Agli Aviatori"** (Giardini a Mare, X ≈ 398, all'altezza della metà del tratto): intero, con una persona accanto.
6. **F6 — Giardini a Mare dall'alto o in diagonale**, tra X 300 e 500: disposizione delle aiuole di rose, delle agavi e del vialetto interno.
7. **F7 — Passo delle palme:** contare le palme di un filare fra l'ancora 2 (X 280) e la scritta a fine passeggiata, oppure fotografare due panchine consecutive con le palme fra loro.
8. **F8 — Chiosco ottagonale a fine passeggiata** (X ≈ 552): da ~15 m, verso SE, con dehors e scritta nel pavimento.
9. **F9 — Fine passeggiata vista dal molo**, dalla radice del Molo Italia (X ≈ 560, Y ≈ 60) verso NO e SO: angolo del ciglio, strada in cubetti, stalli, chiosco.
10. **F10 — Viale Italia dal marciapiede** a X ≈ 450: isola centrale, semafori di X 506/520, palazzi di Viale Mazzini (piani).
