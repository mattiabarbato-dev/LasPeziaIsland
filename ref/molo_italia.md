# Scheda — Blocco 3: Molo Italia, ristorante galleggiante e faro rosso

Legenda: **[V]** verificato (fonte citata) · **[F]** letto da foto · **[S]** stima, da confermare.
Coordinate di progetto come in `area.md`: X lungo la passeggiata verso NE, Y verso la città, metri. In UE: (X·100, −Y·100).
Geo-scout, 2026-11-20. Niente Blender né UEFN.

**Fonti**
- OSM: estratto `ref/osm/morin_blocchi23.osm`, scaricato dall'API OSM il 2026-11-20 (il vecchio `morin_bbox.osm` non arriva fin qui).
  © OpenStreetMap contributors, ODbL.
- Faro: database "Lighthouses of Italy: Liguria" di R. Rowlett ([ibiblio.org/lighthouse/itanw.htm](https://ibiblio.org/lighthouse/itanw.htm)),
  con i riferimenti ARLHS ITA-294, Admiralty E1290, NGA 7764. Concorda con i tag `seamark` di OSM.
- Ristorante: OSM (`building=houseboat`) e schede pubbliche di recensioni ([pos.do](https://pos.do/fr/la-spezia/restaurant/i-gabbiani)).
  Fonte debole: la uso solo per "chiatta ristrutturata con un piano superiore".
- Progetti AdSP sul Molo Italia (rettifica e prolungamento, 2015; riqualificazione del primo tratto, conferenza di servizi
  [MIT 2019-2020](https://mit.gov.it/node/12410)). **Non ho trovato conferme che siano stati realizzati**: vale la geometria OSM attuale.
- Nessuna foto dell'utente mostra il Molo Italia (§9). Google solo come riferimento visivo: non ho salvato nulla.

Nomi reali citati solo per identificare il luogo. Nel gioco: nomi inventati, niente marchi di compagnie, bar o distributori (CLAUDE.md §5).

---

## 1. Box

| Voce | Valore | Stato |
|---|---|---|
| Box giocabile | X 540 … 710, Y −345 … 150 | proposta |
| lat / lon | **44,10322 – 44,10731 N · 9,82832 – 9,83437 E** | calcolo |
| Punti chiave (lat, lon) | gomito 44,104251 / 9,831883 · faro 44,104261 / 9,833946 · ristorante (centro) 44,105257 / 9,830577 | calcolo da OSM |

## 2. Geometria del molo (OSM)

Il molo è dentro il poligono della coastline 137121074, che ne dà i bordi. Il percorso pedonale è la way 132740887 + 801989878 "Molo Italia".

| Tratto | Bordo ovest/sud (lato passeggiata) | Bordo est/nord | Larghezza | Lunghezza | Stato |
|---|---|---|---|---|---|
| **Radice** (Y 85 → 2) | smusso del ciglio da (548,7; 78,3) a (555,0; 41,9), poi X 555 | terraferma: Capitaneria e calata (la coastline esce verso est a Y ≈ 1,6) | — | — | [V] OSM |
| **Ramo 1**, ortogonale alla passeggiata (verso −Y) | X 555,0 → 556,1 (da Y 41,9 a −204,5) | X 571,6-573,6 (da Y 1,6 a −198,5) | **16,5-17,5 m** | **285 m** di percorso (Y 85,2 → −200,3) | [V] OSM |
| **Gomito** | (556,1; −204,5) | (571,6; −198,5) | — | percorso (567,3; −200,3) → (568,8; −203,8) | [V] |
| **Ramo 2**, a ~136° (verso SE) | (556,1; −204,5) → (677,2; −332,2): 176 m | (571,6; −198,5) → (688,7; −321,6): 170 m | **15,4 m** | **161 m** di percorso, fino a (679,9; −320,7) | [V] OSM. Angolo interno 136,5° (dir. 43,5° da −Y verso +X) |
| **Testata** | (677,2; −332,2) – (688,7; −321,6), lato dritto | | 15,6 m | — | [V]. Il progetto 2015 prevedeva una piazza circolare Ø 15 m col faro al centro; OSM mostra una testata **dritta** → non realizzata o non mappata [S] |
| **Moli a dito** sul lato est del ramo 1 | D1: X 572,7-622,6, Y −107,7 … −114,5 · D2: X 573,4-622,3, Y −152,2 … −157,9 | — | 5-7 m | ~50 m ciascuno | [V] OSM (coastline + pier 1161085501, 1161085499). Sono pieni, non pontili su pali [S] |

**Percorso pedonale:** asse a X ≈ 567,5 lungo il ramo 1 (5 m dal bordo est, 12 m dal bordo ovest), poi lungo l'asse del ramo 2.
`highway=pedestrian`, `lit=yes`, `motor_vehicle=permit`, `bicycle=yes` [V OSM 801989878].

| Dato | Valore | Stato |
|---|---|---|
| Superficie | radice Y 4-85: **masselli** (`paving_stones`, way 132740887); molo vero e proprio: **asfalto** (`surface=asphalt`) | [V] OSM; aspetto [S] |
| Quota del piano | come la banchina: ciglio a ~0,6-1,0 m sull'acqua, quindi **Z 0** nel gioco | [S] (stesso porto, stessa banchina storica; `banchina.md` §0) |
| Ciglio | blocchi di pietra chiara come la passeggiata, oppure cordolo in cemento | [S] foto M2 |
| Parapetti / ringhiere | **nessuno mappato** (nessuna `barrier` sul molo). Su un molo d'ormeggio di solito il bordo è libero | assenza [V]; bordo libero [S] → foto M2 |
| Illuminazione | `lit=yes`; lampioni non mappati | [V] / tipo [S] foto M4 |
| Accesso | la radice si raggiunge dalla fine della passeggiata con la strada in cubetti X 560-570, Y 85 (way 238848747) | [V] |

## 3. Il ristorante "galleggiante"

| Voce | Valore | Stato |
|---|---|---|
| Identificazione | **"I Gabbiani"**, `amenity=restaurant`, **`building=houseboat`** (way 851135245). È l'unico ristorante sull'acqua lungo il Molo Italia | [V] OSM; "ristorante galleggiante sul Molo Italia" [V] schede pubbliche |
| Struttura | **chiatta (barcone) ristrutturata**, ormeggiata di fianco al molo: non è una palafitta né una piattaforma fissa | OSM `houseboat` + recensioni [V, fonte debole]; struttura dello scafo [S] |
| Posizione | **lato est del ramo 1**, verso il bacino interno, **X 574,2-593,7, Y −46,3 … −56,7**. Il centro è a **(583,9; −51,5)**, ~136 m dalla linea della passeggiata (Y 85) | [V] OSM |
| Dimensioni in pianta | **19,5 × 10,3 m**, lato lungo perpendicolare al molo (verso +X) | [V] OSM |
| Distanza dal molo | ~2,6 m dal ciglio est (X 571,6) | [V] calcolo |
| Accesso | **passerella** (way 851135244, `bridge=yes`, `layer=1`) da (567,8; −48,7) a (574,2; −48,8), con **cancello in legno** sul bordo della chiatta (node 7939085847, `barrier=entrance`, `material=wood`). La passerella sull'acqua è lunga ~2,6 m, larga ~1,5-2 m [S] | [V] OSM |
| Livelli | **due**: sala al piano dello scafo + **piano superiore** (le recensioni consigliano "il piano di sopra" per la vista) | [V, fonte debole] |
| Altezze | scafo ~1,0 m sull'acqua; piano terra ~2,8 m; piano superiore ~2,8 m, forse terrazza coperta; totale **~6,5-7 m** sull'acqua | [S] foto M5 |
| Aspetto | sovrastruttura chiara (bianco o legno) con grandi vetrate su tutti i lati, terrazza in alto con tenda o tettoia, scafo scuro | [S] da confermare con le foto M5-M6 |
| Nel gioco | nome inventato, nessuna insegna reale. Interno: solo i vetri con un fondo semplice, niente arredo modellato | proposta |

## 4. Il faro rosso

| Voce | Valore | Stato |
|---|---|---|
| Posizione | **(678,6; −327,1)**, sulla testata del ramo 2, ~4 m dal centro della testata verso il lato sud | [V] OSM node 1327347929 |
| Tipo | **torretta tonda** con **ballatoio** (gallery) e **lanterna**: non è un semplice fanale su palo | [V] ibiblio |
| Altezza | torre **~8 m**; piano focale **8 m** | [V] ibiblio + OSM `seamark:light:height=8` |
| Colori | torre **rosso acceso**; lanterna metallica argentata | [V] ibiblio |
| Luce | `seamark:light:character=Fl`, `colour=red`, `period=4`, `sequence=1+(3)`: **un lampo rosso ogni 4 s** (1 s acceso, 3 s spento); portata 8 miglia | [V] OSM + ibiblio |
| Riferimenti | Admiralty E1290, ARLHS ITA-294, NGA 7764 | [V] |
| Accesso | si arriva a piedi lungo il molo; torre chiusa | [V] ibiblio |
| Proporzioni proposte | fusto cilindrico Ø ~1,6-2,0 m (forse leggermente tronco-conico), alto ~6 m, su un basamento ~0,5 m; ballatoio Ø ~2,6 m con ringhiera h 1 m; lanterna Ø ~1,2 m, h ~1,3 m; cupoletta con sfiato | [S] foto M7 |
| Nel gioco | **secondo faro visivo** del livello (CLAUDE.md §2.3): MI emissiva rossa con lampo a 4 s (Fl 1+3) | proposta |

## 5. Intorno al molo

| Elemento | Posizione | Dimensioni | Fonte | Stato |
|---|---|---|---|---|
| Imbarco battelli Cinque Terre | radice del dito D1, node (567,1; −111,2) `amenity=ferry_terminal` | — | OSM 9981146925 | [V] |
| Battelli turistici ormeggiati | ai due moli a dito D1/D2, lato est | 30-35 × 7 m come quello dell'imbarco del Blocco 1 | OSM (terminal) + `elementi.md` | presenza [S] foto M3 |
| Panchine in cemento senza schienale, 4 posti | (567,3; −171,2), (567,4; −179,2) | ~2,4 × 0,5 m | OSM 9981146926/24 (`material=concrete`) | [V] |
| Panchina | (555,3; −96,0), sul bordo ovest | — | OSM 13092712901 | [V] |
| Cestino metallico bianco | (567,6; −164,0) | — | OSM 9981146923 | [V] |
| Capitaneria di Porto | edificio a L, X 592,5-617,2, Y 44,4-80,8 (node 599,2; 61,9) | 2-3 piani [S] | OSM 205843153, 215802259 | pianta [V]; altezza [S] |
| Altri edifici della radice | X 579-593, Y 19,5-40,8 · X 615-630, Y 20-41 | 1-2 piani [S] | OSM 205839145, 205839033 | [V] |
| Calata in masselli lungo Y ≈ 10 | X 568-635 | — | OSM 1410344011 | [V] |
| 3 chioschetti tondi (punti informazioni, taxi) | X ≈ 585, 603,5, 620,5, Y ≈ 107 | Ø ~3,5 m | OSM 352041386/88/87 | [V] |
| Posteggio taxi | X 582-625, Y 89-103 | 10 + 10 posti | OSM 1111180854/53 | [V] |
| Fontana "del Palio del Golfo" | nella rotatoria di Largo Fiorillo, X 640-649, Y 85-94 | Ø ~9 m, illuminata, acqua non potabile | OSM 1198056663, rotatoria 602363058 | [V] |
| Terminal crociere | X 677-725, Y 64-96, 1 piano, tetto piano | 48 × 32 m | OSM 175935400 | [V] |
| Circoli nautici (canottieri, vela) | X 681-711, Y 6-53, con pontili X 677-714, Y −28 e −67 | — | OSM 205841403, 205842197, 1161085494/95/504 | [V] |
| Area portuale di Calata Paita (recintata) | da X 748 verso est | — | OSM 1317207033, 1227366789 | [V]: solo fondale |
| Distributore di carburante | (605,8; 139,6), lato città | — | OSM 228154573 | [V]: fondale, senza marchio |
| Navi da crociera | ormeggiate più a est (Molo Garibaldi), visibili da lontano; si vede una nave anche in `giardini.webp` | — | [F] | posizione [S]: sagoma di fondale facoltativa |
| Sculture o targhe sul molo | **nessuna mappata** | — | OSM (assenza) | [S] foto M8 |

## 6. Raccordi

| Raccordo | Dove | Cosa fare |
|---|---|---|
| Con il Blocco 2 | X 548,7-560, Y 41,9-100 | `SM_Banchina_Angolo_MoloItalia` (scheda `blocco2.md` §5) chiude il ciglio della passeggiata e apre il fianco ovest del molo. La pavimentazione passa dalle lastre della passeggiata ai masselli della radice (X 555-572, Y 4-85) e poi all'asfalto del molo (Y < 4). Il pavimento resta a Z 0, senza gradini |
| Strada d'accesso | X 560-570, Y 85 (cubetti) e Largo Fiorillo X 569, Y 85-130 | Riusare `SM_Molo_Pav_Strada_v2` / `M_Molo_Masselli` (cubetti) e `M_Molo_Asfalto`. Le auto restano fuori: niente veicoli sul molo |
| Barriere | — | La barriera di fine blocco va spostata a est della radice (X ≈ 575 per Y > 4), più una barriera sull'accesso a Largo Fiorillo. L'acqua Acqua V2 va estesa fino a X ~720, Y −350 |
| Linea di vista | dalla fine della passeggiata il faro è a ~420 m in diagonale | nessun asset alto sul ramo 1 deve coprirlo [S], da verificare con il render |

## 7. Tabella degli elementi per la produzione

Priorità: **A** = identifica il posto · **B** = contorno visibile · **C** = dettaglio o fondale.

| # | Elemento | Posizione (X, Y) | Dimensioni | Fonte | Stato | Asset proposto | Texture nuove | Priorità |
|---|---|---|---|---|---|---|---|---|
| 1 | Suolo del molo (radice + 2 rami + 2 dita) | §2 | 17 × 285 m + 15,4 × 161 m | OSM | [V] | **nuovo** `SM_MoloItalia_Suolo` (pezzo unico in coordinate di progetto, UCX a box), `M_Molo_Asfalto` + `M_Molo_Masselli` | 0 | A |
| 2 | Ciglio del molo | i 4 lati lunghi + le dita | ~800 m di bordo | OSM | [V] | **kit** `SM_Banchina_Mod4m_v2` (~190 moduli) + `_Nicchia`/`Scaletta_v2`, testate su misura (gomito, punta, dita) | 0 | A |
| 3 | Faro rosso | (678,6; −327,1) | h ~8 m, Ø ~1,8 m | OSM + ibiblio | [V] | **nuovo, pezzo unico** `SM_MoloItalia_Faro` (≤ 8k tri): fusto con `T_Ponte_Acciaio` + MI rossa, ballatoio come le ringhiere esistenti, lanterna `M_Morin_Master_Vetro`, luce emissiva | 0 | A |
| 4 | Ristorante galleggiante | (583,9; −51,5) | 19,5 × 10,3 × ~7 m | OSM | pianta [V], alzato [S] | **nuovo, pezzo unico** `SM_MoloItalia_RistoranteGalleggiante` (≤ 20k tri, UCX) + passerella | **1024 D+N+ORM ≈ 2,7 MiB** (scafo + facciate). Alternativa a 0: `T_Morin_Imbarco` (scafo/legno) + `T_Molo_Facciate` + vetro | A |
| 5 | Bitte | lati d'ormeggio: est del ramo 1, dita D1/D2, forse ovest | passo ~12 m | decisione utente | [S] | **kit** `SM_Banchina_Bitta_v2`, **solo dove ormeggiano barche** (foto M2/M3) | 0 | B |
| 6 | Lampioni del molo | lungo l'asse X ≈ 567,5 e il ramo 2 | passo ~20-25 m [S] | `lit=yes` | [S] | **kit**: lampioni alti del molo del ponte (Tranche 2, da fare) o `SM_Morin_Lampione`, secondo la foto M4 | 0 | B |
| 7 | Panchine in cemento ×2, panchina, cestino | §5 | — | OSM | [V] | **kit** `SM_Morin_Panchina` (variante cemento via MI), `SM_Morin_Cestino` | 0 | C |
| 8 | Battelli ai moli a dito | D1, D2 | 30-35 m | [S] | [S] | **kit** `SM_Morin_Battello` (1-2 istanze) | 0 | B |
| 9 | Capitaneria + edifici della radice | §5 | 2-3 piani | OSM | pianta [V] | **nuovo** low-poly (≤ 5k tri ciascuno) con `T_Fondale_Palazzo_A/B/C` o `T_Molo_Facciate` | 0 | B |
| 10 | Chioschetti tondi ×3 | Y ≈ 107 | Ø 3,5 m | OSM | [V] | **nuovo** `SM_Morin_ChioschettoTondo` (1 mesh, 3 istanze) con atlante `T_Morin_Chiosco` | 0 | C |
| 11 | Fontana del Palio + rotatoria | (644,5; 89,5) | Ø 9 m | OSM | [V] | **nuovo** semplice: vasca `MI_Banchina_Blocchi`, acqua con il vetro esistente o un MI a tinta | 0 | C |
| 12 | Terminal crociere, circoli nautici, Calata Paita | §5 | — | OSM | [V] | **kit** sagome di fondale (`SM_Fondale_EdificioVetrate`, palazzi) | 0 | C |
| 13 | Barche dei circoli, yacht | pontili X 677-714 | — | OSM | [V] | **kit** `SM_Mirabello_YachtA`, `YachtB_v2` | 0 | C |
| 14 | Nave da crociera lontana (facoltativa) | E/SE, oltre X 750 | ~250-300 m | [F] | [S] | **nuovo** sagoma di fondale ≤ 5k tri, materiale a tinta senza texture | 0 | C |

## 8. Stima della memoria texture

| Voce | Set | MiB (con mip) |
|---|---|---|
| Ristorante galleggiante (scafo, facciate, vetrate) | 1024 D + N + ORM | ≈ **2,7** |
| Faro, molo, bitte, lampioni, battelli, edifici | riuso | 0 |
| **Totale Blocco 3** | | **≈ 2,7 MiB** (0 con l'alternativa di riuso). Obiettivo ≤ 10 MiB |

Con i due blocchi insieme si stimano **≈ 5,6-8,3 MiB**: con i 236 MiB di oggi si arriva a **242-244 MiB**, sotto la soglia di 245 ma
con pochissimo margine. **Consiglio:** per l'agave e per il ristorante scegliere le alternative di riuso, oppure liberare memoria prima
(LODBias 1 su qualche texture lontana, ad esempio le 4096 del ponte viste da lontano: decisione dell'utente).

## 9. Foto disponibili

**Nessuna** foto in `ref/foto/` mostra il Molo Italia, il ristorante o il faro. `giardini.webp` mostra in lontananza una nave da crociera
oltre le palme (porto commerciale a E/SE).

## 10. Foto da chiedere all'utente (Blocco 3)

1. **M1 — Il molo d'infilata dalla radice**, da (567; 80) verso −Y (SE lungo il ramo 1): larghezza, pavimento, lampioni, cosa c'è sul bordo ovest.
2. **M2 — Il ciglio del molo di profilo**, da metà del ramo 1 (Y ≈ −100) lungo il bordo ovest e poi lungo il bordo est: quota sull'acqua, bitte, ringhiere sì/no, materiale.
3. **M3 — Un molo a dito** (D1, Y ≈ −111): dalla radice verso est, con un battello ormeggiato se c'è.
4. **M4 — Un lampione del molo** intero, con una persona accanto.
5. **M5 — Il ristorante galleggiante di fianco**, dal molo all'altezza di Y ≈ −30 guardando verso SE: scafo, i due piani, terrazza, passerella e cancello.
6. **M6 — Il ristorante dal lato acqua o dall'alto**, ad esempio dal ramo 2 guardando indietro verso N: forma del tetto e lato verso il bacino.
7. **M7 — Il faro**: una foto intera da ~15 m con una persona accanto e una del ballatoio e della lanterna.
8. **M8 — La testata del ramo 2** intorno al faro: forma (dritta o tonda), panchine, targhe, ringhiere.
9. **M9 — Il gomito** (Y ≈ −200) verso il faro: com'è il raccordo fra i due rami, ci sono ostacoli o gradini.
10. **M10 — La radice vista dalla fine della passeggiata**, da (545; 90) verso SE: Capitaneria, strada in cubetti, chioschetti, inizio del molo.

## 11. Ordine di lavoro proposto (Blocco 3)

Da iniziare dopo il Blocco 2, oppure insieme al punto 1 del Blocco 2 per il raccordo.
1. **(blender-artist) Suolo e ciglio** del molo (elementi 1-2): blockout prima, poi kit banchina v2. (uefn-builder) Acqua V2 estesa, barriere spostate.
2. **Faro rosso** (3): pezzo unico, con la luce lampeggiante (MI emissiva; il lampo con un device o con Verse, a cura di uefn-builder o verse-dev).
3. **Ristorante galleggiante + passerella** (4), dopo le foto M5-M6.
4. **Arredi del molo:** lampioni, panchine, cestino, bitte solo nelle zone d'ormeggio (5-7), dopo le foto M2-M4.
5. **Battelli e barche** (8, 13).
6. **Radice e fondale:** Capitaneria, chioschetti, fontana, terminal, circoli (9-12), nave da crociera facoltativa (14).
7. (qa-tester) Sessione: percorso radice → faro senza fessure, cadute in acqua dai bordi liberi, faro visibile dalla passeggiata, memoria.
